"""Import ONLY actually downloaded CC0/CC-BY audio as 48 kHz stereo PCM WAV.

Selected Kenney assets can be retrieved from a pinned public GitHub mirror.
Freesound login-only sounds are never downloaded via guessed preview URLs.
OpenGameArt archives may be passed explicitly after local download.

All installed files are marked *unreviewed*. The importer never touches music
or the legacy 19 SFX, and never invents missing media.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import wave
import zipfile


REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "docs/audio/cc0_ccby_sources.json"
RECEIPTS = REPO / "docs/audio/cc_import_receipts.json"
CREDITS = REPO / "assets/audio/CREDITS_CC_AUDIO.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\\0" + data).hexdigest()


def safe_relative(name: str) -> Path:
    parts = PurePosixPath(name.replace("\\", "/"))
    if (parts.is_absolute() or not parts.parts or
            any(p in ("", ".", "..") for p in parts.parts) or
            ":" in parts.parts[0]):
        raise ValueError("Unsafe archive member or asset path: " + name)
    return Path(*parts.parts)


def fetch_bytes(url: str, *, limit: int = 75_000_000) -> bytes:
    if not url.startswith("https://"):
        raise ValueError("HTTPS is required for audio download")
    req = urllib.request.Request(url, headers={"User-Agent": "CyberCity2085-CC-Audio-Importer/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        chunks, length = [], 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            length += len(chunk)
            if length > limit:
                raise ValueError("Audio download exceeds size safety limit")
            chunks.append(chunk)
    result = b"".join(chunks)
    if not result:
        raise ValueError("Empty download")
    return result


def wav_info(path: Path) -> dict:
    with wave.open(str(path), "rb") as wf:
        channels, rate, width, frames = (
            wf.getnchannels(), wf.getframerate(), wf.getsampwidth(), wf.getnframes()
        )
        if (channels, rate, width) != (2, 48000, 2) or frames < 4800:
            raise ValueError(f"Unexpected WAV format/duration: {channels}, {rate}, {width}, {frames}")
        from array import array
        high = 0
        clipped = 0
        for _ in range(0, frames, 65536):
            raw = wf.readframes(65536)
            samples = array("h")
            samples.frombytes(raw)
            if sys.byteorder != "little":
                samples.byteswap()
            if samples:
                high = max(high, max(abs(int(x)) for x in samples))
                clipped += sum(abs(int(x)) >= 32767 for x in samples)
    return {
        "duration_seconds": round(frames / rate, 4),
        "channels": channels,
        "sample_rate_hz": rate,
        "bits_per_sample": width * 8,
        "peak_fraction": round(high / 32768, 6),
        "full_scale_samples": clipped,
        "technical_review_required": bool(clipped)
    }


def convert_audio(source: Path, destination: Path, *, overwrite: bool = False) -> dict:
    if destination.exists() and not overwrite:
        raise FileExistsError(str(destination))
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg required for lossless PCM WAV conversion")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cc_audio_") as tmpdir:
        scratch = Path(tmpdir) / "converted.wav"
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-i", str(source), "-map", "0:a:0", "-vn",
            "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(scratch)
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            raise ValueError("ffmpeg could not decode asset: " + proc.stderr.decode(errors="replace")[:500])
        meta = wav_info(scratch)
        shutil.move(str(scratch), str(destination))
    meta["output_sha256"] = sha256(destination)
    return meta


def candidate_audio_files(directory: Path) -> list[Path]:
    return sorted(
        (x for x in directory.rglob("*")
         if x.is_file() and x.suffix.lower() in (".ogg", ".wav", ".flac", ".m4a", ".mp3", ".aif", ".aiff")),
        key=lambda p: str(p).casefold()
    )


def unpack_archive(path: Path, target: Path) -> list[Path]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > 5000:
                raise ValueError("Too many archive entries")
            for item in members:
                safe_relative(item.filename)
                if not item.is_dir() and item.file_size > 100_000_000:
                    raise ValueError("Archive member too large")
                if (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Archive contains symbolic link")
            archive.extractall(target)
    elif path.suffix.lower() == ".7z":
        command = shutil.which("7z") or shutil.which("7zz")
        if not command:
            raise RuntimeError("7z/7zz required for the Thimras archive")
        subprocess.run([command, "x", "-y", f"-o{target}", str(path)],
                       check=True, capture_output=True)
        for extracted in target.rglob("*"):
            if extracted.is_symlink() or not extracted.resolve().is_relative_to(target.resolve()):
                raise ValueError("Unsafe extracted archive path")
    else:
        raise ValueError("Expected ZIP or 7z archive")
    return candidate_audio_files(target)


def load_receipts() -> dict:
    if RECEIPTS.is_file():
        return json.loads(RECEIPTS.read_text(encoding="utf-8"))
    return {"schema_version": 1, "assets": []}


def save_receipts(receipts: dict) -> None:
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS.write_text(json.dumps(receipts, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    lines = [
        "# CyberCity 2085 — Additional audio licenses and credits",
        "",
        "The source code is under AGPL-3.0. Audio files listed below retain their own licenses.",
        "The files below were actually converted and installed; entries not present here",
        "remain candidates in docs/audio/cc0_ccby_sources.json.",
        "",
    ]
    for asset in sorted(receipts["assets"], key=lambda x: x["path"]):
        lines += [
            f"## {asset['path']}",
            f"- Author: {asset['author']}",
            f"- License: {asset['license']}",
            f"- Source: {asset['source_page']}",
            f"- Adaptation: converted to 48 kHz / 16-bit / stereo PCM WAV using ffmpeg.",
            f"- Original/source SHA-256: {asset['source_sha256']}",
            f"- Distribution: independent licensed audio asset; not relicensed AGPL.",
            "- Audio review: pending; integration is a preview until approved.",
            "",
        ]
    CREDITS.parent.mkdir(parents=True, exist_ok=True)
    CREDITS.write_text("\\n".join(lines), encoding="utf-8")


def install_asset(source: Path, relative_target: str, source_record: dict,
                  receipts: dict, *, overwrite: bool = False) -> dict:
    relative = safe_relative(relative_target)
    if relative.suffix.lower() != ".wav":
        raise ValueError("Output must be WAV")
    target = REPO / "assets/audio/overhaul" / relative
    meta = convert_audio(source, target, overwrite=overwrite)
    receipt = {
        "path": str(target.relative_to(REPO)).replace(os.sep, "/"),
        "source_file": source.name,
        "source_sha256": sha256(source),
        "author": source_record["author"],
        "license": source_record["license"],
        "source_page": source_record["source_page"],
        "imported_date": dt.date.today().isoformat(),
        "status": "installed_unreviewed",
        "audition_status": "not_verified",
        **meta,
    }
    receipts["assets"] = [a for a in receipts["assets"] if a["path"] != receipt["path"]]
    receipts["assets"].append(receipt)
    return receipt


def import_kenney(catalog: dict, receipts: dict, *, overwrite: bool) -> list[dict]:
    installed = []
    for item in catalog["kenney_curated"]:
        with tempfile.TemporaryDirectory(prefix="kenney_src_") as tmp:
            data = fetch_bytes(item["source_url"])
            actual = git_blob_sha(data)
            if actual.lower() != item["source_blob_sha"].lower():
                raise ValueError(f"Git SHA mismatch for {item['source_path']}: {actual}")
            source = Path(tmp) / Path(item["source_path"]).name
            source.write_bytes(data)
            record = {
                "author": "Kenney",
                "license": "CC0-1.0",
                "source_page": item["license_source_page"],
            }
            target = item["relative_target"]
            full = REPO / catalog["output_root"] / safe_relative(target)
            if full.exists() and not overwrite:
                continue
            installed.append(install_asset(source, target, record, receipts, overwrite=overwrite))
            save_receipts(receipts)
            print("INSTALLED", target, installed[-1]["duration_seconds"], "s")
    return installed


def import_external(catalog: dict, receipts: dict, source_id: str, path: Path,
                    *, overwrite: bool) -> list[dict]:
    source_record = next((x for x in catalog["sources"] if x["id"] == source_id), None)
    if source_record is None:
        raise ValueError("Unrecognized source id: " + source_id)
    if source_record["license"] not in ("CC0-1.0", "CC-BY-4.0"):
        raise ValueError("Unapproved license")
    if not path.is_file():
        raise FileNotFoundError(str(path))
    targets = []
    with tempfile.TemporaryDirectory(prefix="cc_audio_unpack_") as tmp:
        if path.suffix.lower() in (".zip", ".7z"):
            candidates = unpack_archive(path, Path(tmp))
            if not candidates:
                raise ValueError("No decodable audio files in archive")
            candidates = candidates[:5]  # Curated subset, not the full archive.
            base = Path(source_record["proposed_target"])
            for i, source in enumerate(candidates, start=1):
                target = str(base.with_name(base.stem.rsplit("_", 1)[0] + f"_{i:02d}.wav"))
                full = REPO / catalog["output_root"] / safe_relative(target)
                if full.exists() and not overwrite:
                    continue
                targets.append(install_asset(source, target, source_record, receipts, overwrite=overwrite))
                save_receipts(receipts)
        else:
            target = source_record["proposed_target"]
            full = REPO / catalog["output_root"] / safe_relative(target)
            if not full.exists() or overwrite:
                targets.append(install_asset(path, target, source_record, receipts, overwrite=overwrite))
                save_receipts(receipts)
    return targets


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kenney", action="store_true", help="Download and convert pinned Kenney CC0 selection")
    p.add_argument("--external", nargs=2, metavar=("SOURCE_ID", "FILE"), help="Import downloaded Freesound/OGA audio or pack")
    p.add_argument("--fetch-direct", metavar="SOURCE_ID", help="Download documented direct OpenGameArt archive")
    p.add_argument("--overwrite", action="store_true", help="Replace target WAV of matching provenance")
    args = p.parse_args()
    if sum(bool(x) for x in (args.kenney, args.external, args.fetch_direct)) != 1:
        p.error("Select exactly one of --kenney, --external or --fetch-direct")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    receipts = load_receipts()
    try:
        if args.kenney:
            installed = import_kenney(catalog, receipts, overwrite=args.overwrite)
        elif args.external:
            installed = import_external(catalog, receipts, args.external[0],
                                        Path(args.external[1]).resolve(), overwrite=args.overwrite)
        else:
            record = next((s for s in catalog["sources"] if s["id"] == args.fetch_direct), None)
            if record is None or not record.get("download_url"):
                raise ValueError("Only documented direct archive downloads supported")
            with tempfile.TemporaryDirectory(prefix="cc_audio_download_") as tmp:
                suffix = Path(record["download_url"]).suffix
                path = Path(tmp) / ("source" + suffix)
                path.write_bytes(fetch_bytes(record["download_url"]))
                installed = import_external(catalog, receipts, record["id"], path,
                                            overwrite=args.overwrite)
        save_receipts(receipts)
        print(f"Installed {len(installed)} verified WAV files. Pending audition.")
        return 0
    except Exception as error:
        save_receipts(receipts)
        print("Import failed:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
