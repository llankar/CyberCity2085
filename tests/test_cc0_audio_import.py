"""Offline import safety tests; these do not claim listening or game-engine playback."""
import importlib.util
import json
import shutil
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "tools" / "import_cc0_audio.py"
spec = importlib.util.spec_from_file_location("import_cc0_audio", MODULE)
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


class ImportSafetyTests(unittest.TestCase):
    def test_git_blob_sha_is_git_compatible(self):
        self.assertEqual(audio.git_blob_sha(b"abc"), "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")

    def test_reject_absolute_and_traversal(self):
        for value in ("../hack.wav", "/tmp/hack.wav", "a/../../hack.wav", "C:/hack.wav"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    audio.safe_relative(value)
        self.assertEqual(audio.safe_relative("a/b.wav").as_posix(), "a/b.wav")

    def test_catalog_has_18_unique_cc0_sources_and_uninstalled_status(self):
        manifest = json.loads((MODULE.parents[1] / "docs/audio/cc0_ccby_sources.json").read_text())
        curated = manifest["kenney_curated"]
        self.assertEqual(len(curated), 18)
        self.assertEqual(len({x["relative_target"] for x in curated}), 18)
        for item in curated:
            self.assertEqual(item["license"], "CC0-1.0")
            self.assertEqual(item["distribution_status"], "not_yet_converted")
            self.assertEqual(len(item["source_blob_sha"]), 40)
        by_source = {x["id"]: x for x in manifest["sources"]}
        self.assertEqual(by_source["laboratory_tommasomotteran"]["license"], "CC-BY-4.0")

    def test_safe_zip_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.zip"
            import zipfile
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../evil.wav", b"corrupt")
            with self.assertRaises(ValueError):
                audio.unpack_archive(path, Path(tmp) / "out")

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg required")
    def test_convert_a_fixture_and_register_only_actual_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            src = folder / "input.wav"
            with wave.open(str(src), "wb") as wf:
                wf.setnchannels(1)
                wf.setframerate(44100)
                wf.setsampwidth(2)
                wf.writeframes(struct.pack("<h", 1000) * 22050)
            target = folder / "assets/audio/overhaul/technology/fixture.wav"
            with patch.object(audio, "REPO", folder), patch.object(audio, "RECEIPTS", folder / "receipts.json"), patch.object(audio, "CREDITS", folder / "credits.md"):
                receipts = audio.load_receipts()
                record = audio.install_asset(src, "technology/fixture.wav",
                                             {"author": "fixture", "license": "CC0-1.0", "source_page": "https://example.test/fixture"},
                                             receipts)
                self.assertTrue(target.is_file())
                self.assertEqual(record["sample_rate_hz"], 48000)
                self.assertEqual(record["channels"], 2)
                self.assertAlmostEqual(record["duration_seconds"], 0.5, places=2)
                self.assertEqual(record["status"], "installed_unreviewed")
                audio.save_receipts(receipts)
                self.assertIn("fixture", (folder / "credits.md").read_text())
                with self.assertRaises(FileExistsError):
                    audio.install_asset(src, "technology/fixture.wav",
                                        {"author": "fixture", "license": "CC0-1.0", "source_page": "https://example.test/fixture"},
                                        receipts)


if __name__ == "__main__":
    unittest.main()
