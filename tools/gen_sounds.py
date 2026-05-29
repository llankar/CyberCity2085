"""Generate synthesised sound effects and music for CyberCity 2085.

Run:
    python tools/gen_sounds.py

Writes 17 SFX WAV files to assets/audio/sfx/
and 3 music WAV files to assets/audio/music/.

Requires: numpy, scipy (already project dependencies).
No external encoder needed — output is raw 16-bit PCM WAV.
"""

from __future__ import annotations

import math
import os
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

RATE = 44_100  # samples per second
BIT_DEPTH = 16
AMP_MAX = 32_767

SFX_DIR   = Path("assets/audio/sfx")
MUSIC_DIR = Path("assets/audio/music")


# ── Low-level helpers ─────────────────────────────────────────────────────────

def _save(path: Path, sig: np.ndarray) -> None:
    sig = np.clip(sig, -1.0, 1.0)
    pcm = (sig * AMP_MAX).astype(np.int16)
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(pcm.tobytes())
    print(f"  wrote {path}  ({len(sig) / RATE:.2f}s)")


def _t(dur: float) -> np.ndarray:
    return np.linspace(0, dur, int(RATE * dur), endpoint=False)


def _sine(freq: float, dur: float) -> np.ndarray:
    return np.sin(2 * math.pi * freq * _t(dur))


def _sawtooth(freq: float, dur: float) -> np.ndarray:
    t = _t(dur)
    return 2.0 * (t * freq - np.floor(t * freq + 0.5))


def _noise(dur: float, seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).uniform(-1.0, 1.0, int(RATE * dur))


def _lpf(sig: np.ndarray, cutoff: int) -> np.ndarray:
    sos = butter(4, cutoff / (RATE / 2), btype="low", output="sos")
    return sosfilt(sos, sig)


def _hpf(sig: np.ndarray, cutoff: int) -> np.ndarray:
    sos = butter(2, cutoff / (RATE / 2), btype="high", output="sos")
    return sosfilt(sos, sig)


def _exp(n: int, tau: float = 0.10) -> np.ndarray:
    return np.exp(-np.arange(n) / (tau * RATE))


def _adsr(n: int, a: float = 0.05, d: float = 0.1, s: float = 0.7, r: float = 0.2) -> np.ndarray:
    env = np.ones(n)
    ai, di, ri = int(a * n), int(d * n), int(r * n)
    si = n - ai - di - ri
    if ai: env[:ai] = np.linspace(0, 1, ai)
    if di: env[ai:ai + di] = np.linspace(1, s, di)
    if si > 0: env[ai + di:ai + di + si] = s
    if ri: env[ai + di + si:] = np.linspace(s, 0, ri)
    return env


def _norm(sig: np.ndarray, peak: float = 0.92) -> np.ndarray:
    m = np.max(np.abs(sig))
    return sig / m * peak if m > 0 else sig


def _mix(*parts: tuple[np.ndarray, float]) -> np.ndarray:
    n = max(len(s) for s, _ in parts)
    out = np.zeros(n)
    for s, vol in parts:
        out[:len(s)] += s * vol
    return _norm(out)


# ── SFX generators ────────────────────────────────────────────────────────────

def _sfx_fire() -> np.ndarray:
    dur = 0.28
    nz = _lpf(_noise(dur, 1), 6_000) * _exp(int(RATE * dur), 0.04)
    bass = _sine(75, dur) * _exp(int(RATE * dur), 0.035)
    return _mix((nz, 0.85), (bass, 0.35))


def _sfx_melee() -> np.ndarray:
    dur = 0.20
    thump = _sine(110, dur) * _exp(int(RATE * dur), 0.06)
    crunch = _lpf(_noise(dur, 2), 900) * _exp(int(RATE * dur), 0.03)
    return _mix((thump, 0.70), (crunch, 0.55))


def _sfx_psi() -> np.ndarray:
    dur = 0.55
    t = _t(dur)
    freq = 300 + 1_100 * (t / dur) ** 2
    phase = 2 * math.pi * np.cumsum(freq) / RATE
    sweep = np.sin(phase)
    h2 = np.sin(2 * phase) * 0.28
    env = _adsr(len(sweep), a=0.04, d=0.20, s=0.60, r=0.30)
    return _norm((sweep + h2) * env) * 0.82


def _sfx_hit() -> np.ndarray:
    dur = 0.15
    nz = _hpf(_lpf(_noise(dur, 3), 5_000), 400) * _exp(int(RATE * dur), 0.04)
    tone = _sine(280, dur) * _exp(int(RATE * dur), 0.03)
    return _mix((nz, 0.80), (tone, 0.35))


def _sfx_miss() -> np.ndarray:
    dur = 0.18
    nz = _hpf(_lpf(_noise(dur, 4), 2_500), 500)
    env = _adsr(len(nz), a=0.20, d=0.10, s=0.45, r=0.50)
    return nz * env * 0.48


def _sfx_death() -> np.ndarray:
    dur = 0.78
    nz = _lpf(_noise(0.14, 5), 3_500) * _exp(int(RATE * 0.14), 0.04)
    t = _t(dur)
    freq = 420 * np.exp(-t * 2.2)
    phase = 2 * math.pi * np.cumsum(freq) / RATE
    tone = np.sin(phase) * _exp(len(phase), 0.22)
    buf = np.zeros(int(RATE * dur))
    buf[:len(nz)] += nz * 0.80
    buf[:len(tone)] += tone * 0.60
    return _norm(buf) * 0.88


def _sfx_overwatch() -> np.ndarray:
    dur = 0.42
    t = _t(dur)
    freq = 200 + 420 * (t / dur)
    phase = 2 * math.pi * np.cumsum(freq) / RATE
    sig = np.sin(phase)
    tremolo = 1.0 + 0.14 * np.sin(2 * math.pi * 11 * t)
    env = _adsr(len(sig), a=0.04, d=0.08, s=0.82, r=0.22)
    return _norm(sig * tremolo * env) * 0.75


def _sfx_move() -> np.ndarray:
    dur = 0.09
    nz = _hpf(_lpf(_noise(dur, 6), 1_800), 180) * _exp(int(RATE * dur), 0.018)
    tone = _sine(190, dur) * _exp(int(RATE * dur), 0.022)
    return _mix((nz, 0.62), (tone, 0.42)) * 0.68


def _beep(freq: float, dur: float, wave: str = "sine") -> np.ndarray:
    n = int(RATE * dur)
    env = _adsr(n, a=0.03, d=0.10, s=0.80, r=0.35)
    base = _sine(freq, dur) if wave == "sine" else _sawtooth(freq, dur)
    return base * env


def _sfx_turn_player() -> np.ndarray:
    b1 = _beep(523.25, 0.10)   # C5
    b2 = _beep(659.25, 0.10)   # E5
    gap = np.zeros(int(RATE * 0.04))
    return np.concatenate([b1, gap, b2]) * 0.58


def _sfx_turn_enemy() -> np.ndarray:
    b1 = (_sawtooth(220, 0.12) * 0.38 + _sine(220, 0.12) * 0.62) * _adsr(int(RATE * 0.12), r=0.30)
    b2 = (_sawtooth(174.61, 0.12) * 0.38 + _sine(174.61, 0.12) * 0.62) * _adsr(int(RATE * 0.12), r=0.30)
    gap = np.zeros(int(RATE * 0.04))
    return np.concatenate([b1, gap, b2]) * 0.52


def _sfx_victory() -> np.ndarray:
    notes = [261.63, 329.63, 392.00, 523.25]  # C4 E4 G4 C5
    parts = [_beep(f, 0.16) for f in notes]
    chord_dur = 0.62
    nc = int(RATE * chord_dur)
    env_c = _adsr(nc, a=0.02, d=0.14, s=0.72, r=0.40)
    chord = sum(_sine(f, chord_dur) for f in notes) / 4 * env_c
    full = np.concatenate(parts + [chord])
    return _norm(full) * 0.84


def _sfx_defeat() -> np.ndarray:
    notes = [523.25, 392.00, 311.13, 261.63]  # C5 G4 Eb4 C4
    parts = [
        (_sawtooth(f, 0.17) * 0.28 + _sine(f, 0.17) * 0.72) * _adsr(int(RATE * 0.17), r=0.30)
        for f in notes
    ]
    final_n = int(RATE * 0.72)
    final_env = _adsr(final_n, a=0.03, d=0.30, s=0.38, r=0.42)
    final = _sine(130.81, 0.72) * final_env
    full = np.concatenate(parts + [final])
    return _norm(full) * 0.78


def _sfx_ui_click() -> np.ndarray:
    dur = 0.05
    return _sine(1_200, dur) * _adsr(int(RATE * dur), a=0.01, d=0.20, s=0.30, r=0.50) * 0.48


def _sfx_deploy() -> np.ndarray:
    b1 = _beep(440.00, 0.12)   # A4
    b2 = _beep(880.00, 0.15)   # A5
    gap = np.zeros(int(RATE * 0.04))
    return np.concatenate([b1, gap, b2]) * 0.60


def _sfx_reinforce() -> np.ndarray:
    dur = 0.62
    t = _t(dur)
    freq = 600 + 200 * np.sin(2 * math.pi * 4.5 * t)
    phase = 2 * math.pi * np.cumsum(freq) / RATE
    sig = np.sin(phase)
    env = np.ones(len(sig))
    fa, fr = int(0.02 * RATE), len(sig) - int(0.56 * RATE)
    env[:fa] = np.linspace(0, 1, fa)
    env[int(0.56 * RATE):] = np.linspace(1, 0, fr)
    return _norm(sig * env) * 0.74


def _sfx_stun() -> np.ndarray:
    dur = 0.28
    thump = _sine(78, dur) * _exp(int(RATE * dur), 0.05)
    buzz = (_sawtooth(58, dur) * 0.3) * _exp(int(RATE * dur), 0.08)
    nz = _lpf(_noise(dur, 7), 700) * _exp(int(RATE * dur), 0.04) * 0.38
    return _mix((thump, 0.72), (buzz, 0.55), (nz, 0.45))


def _sfx_bleed() -> np.ndarray:
    dur = 0.09
    nz = _hpf(_lpf(_noise(dur, 8), 1_000), 90) * _exp(int(RATE * dur), 0.022)
    tone = _sine(175, dur) * _exp(int(RATE * dur), 0.026)
    return _mix((nz, 0.52), (tone, 0.60)) * 0.58


# ── Drum kit ──────────────────────────────────────────────────────────────────

def _kick(dur: float = 0.26) -> np.ndarray:
    t = _t(dur)
    freq = 120 * np.exp(-t * 28)
    phase = 2 * math.pi * np.cumsum(freq) / RATE
    tone = np.sin(phase) * _exp(len(phase), 0.09)
    nz = _lpf(_noise(dur, 10), 350) * _exp(int(RATE * dur), 0.012)
    return _mix((tone, 0.88), (nz, 0.22))


def _snare(dur: float = 0.16) -> np.ndarray:
    nz = _hpf(_lpf(_noise(dur, 11), 9_000), 180) * _exp(int(RATE * dur), 0.055)
    tone = _sine(195, dur) * _exp(int(RATE * dur), 0.022)
    return _mix((nz, 0.72), (tone, 0.32))


def _hihat(dur: float = 0.06, opn: bool = False) -> np.ndarray:
    nz = _hpf(_noise(dur, 12), 9_000)
    nz *= _exp(int(RATE * dur), 0.065 if opn else 0.016)
    return nz * 0.38


def _bass_note(freq: float, dur: float) -> np.ndarray:
    n = int(RATE * dur)
    tone = _lpf(_sawtooth(freq, dur) * 0.5 + _sine(freq, dur) * 0.5, 500)
    return tone * _adsr(n, a=0.02, d=0.14, s=0.58, r=0.22) * 0.62


def _stab(freqs: list[float], dur: float) -> np.ndarray:
    n = int(RATE * dur)
    combined = sum(_sawtooth(f, dur) for f in freqs) / len(freqs)
    return _lpf(combined, 2_500) * _adsr(n, a=0.02, d=0.10, s=0.55, r=0.25) * 0.38


# ── Music generators ──────────────────────────────────────────────────────────

def _music_battle() -> np.ndarray:
    """120 BPM, C minor, 4 bars = 8 s."""
    bpm = 120
    beat = 60.0 / bpm         # 0.5 s
    bar  = beat * 4            # 2.0 s
    bars = 4
    total = bar * bars         # 8.0 s
    n = int(RATE * total)
    tr = np.zeros(n)

    kk = _kick()
    sn = _snare()
    hh = _hihat()
    oh = _hihat(0.14, opn=True)

    for bi in range(bars):
        bs = int(bi * bar * RATE)
        for beat_i in range(4):
            bst = bs + int(beat_i * beat * RATE)
            hst = bst + int(beat * RATE // 2)
            if beat_i in (0, 2):
                end = bst + len(kk); ns = min(len(kk), n - bst)
                tr[bst:bst + ns] += kk[:ns]
            if beat_i in (1, 3):
                ns = min(len(sn), n - bst)
                tr[bst:bst + ns] += sn[:ns]
            ns = min(len(hh), n - bst)
            tr[bst:bst + ns] += hh[:ns]
            if hst < n:
                ns = min(len(oh), n - hst)
                tr[hst:hst + ns] += oh[:ns]

    # Bass line: C1 C1 Eb1 G1 per bar
    bass_freqs = [32.70, 32.70, 38.89, 49.00]
    for bi in range(bars):
        for beat_i in range(4):
            f = bass_freqs[beat_i]
            st = int((bi * bar + beat_i * beat) * RATE)
            note = _bass_note(f, beat * 0.88)
            ns = min(len(note), n - st)
            if st < n:
                tr[st:st + ns] += note[:ns]

    # Chord stabs on bars 2 and 4
    cm_freqs  = [261.63, 311.13, 392.00]  # Cm
    am_freqs  = [220.00, 261.63, 329.63]  # Am fragment
    for bi in (1, 3):
        st1 = int(bi * bar * RATE)
        ch1 = _stab(cm_freqs, beat * 0.45)
        ns = min(len(ch1), n - st1)
        tr[st1:st1 + ns] += ch1[:ns]
        st2 = int((bi * bar + 2 * beat) * RATE)
        ch2 = _stab(am_freqs, beat * 0.35)
        ns = min(len(ch2), n - st2)
        if st2 < n:
            tr[st2:st2 + ns] += ch2[:ns]

    return _norm(tr) * 0.74


def _music_briefing() -> np.ndarray:
    """Slow Cm pad with LFO, low pulse, 6 s."""
    dur = 6.0
    n = int(RATE * dur)
    tr = np.zeros(n)
    rng = np.random.default_rng(42)

    # Cm pad — C3 Eb3 G3 C4
    for freq in [130.81, 155.56, 196.00, 261.63]:
        t = _t(dur)
        det = 1.0 + rng.uniform(-0.006, 0.006)
        lfo = 1.0 + 0.06 * np.sin(2 * math.pi * 0.28 * t)
        wave = np.sin(2 * math.pi * freq * det * t) * lfo
        env = np.ones(n)
        fa, fr = int(0.9 * RATE), int(0.9 * RATE)
        env[:fa] = np.linspace(0, 1, fa)
        env[n - fr:] = np.linspace(1, 0, fr)
        tr += wave * env * 0.18

    # Low pulse C2
    t = _t(dur)
    pulse = np.sin(2 * math.pi * 65.41 * t)
    pulse_env = 0.48 + 0.48 * np.sin(2 * math.pi * 0.48 * t)
    tr += pulse * pulse_env * 0.28

    return _norm(tr) * 0.60


def _music_debrief() -> np.ndarray:
    """C major pad + gentle arpeggio, 5 s."""
    dur = 5.0
    n = int(RATE * dur)
    tr = np.zeros(n)
    rng = np.random.default_rng(7)

    # C major pad — C3 E3 G3 C4
    for freq in [130.81, 164.81, 196.00, 261.63]:
        t = _t(dur)
        det = 1.0 + rng.uniform(-0.005, 0.005)
        wave = np.sin(2 * math.pi * freq * det * t) + np.sin(4 * math.pi * freq * det * t) * 0.28
        env = np.ones(n)
        fa, fr = int(0.55 * RATE), int(1.1 * RATE)
        env[:fa] = np.linspace(0, 1, fa)
        env[n - fr:] = np.linspace(1, 0, fr)
        tr += wave * env * 0.14

    # Arpeggio C4 E4 G4 C5
    arp = [261.63, 329.63, 392.00, 523.25]
    note_dur = dur / len(arp)
    for i, freq in enumerate(arp):
        st = int(i * note_dur * RATE)
        nt = int(note_dur * RATE * 0.78)
        env = np.ones(nt)
        fa = int(0.05 * RATE)
        env[:fa] = np.linspace(0, 1, min(fa, nt))
        env[int(0.80 * nt):] = np.linspace(1, 0, nt - int(0.80 * nt))
        note_sig = np.sin(2 * math.pi * freq * np.arange(nt) / RATE) * env
        ns = min(nt, n - st)
        if st < n:
            tr[st:st + ns] += note_sig[:ns] * 0.38

    return _norm(tr) * 0.64


# ── Entry point ───────────────────────────────────────────────────────────────

_SFX_MAP = {
    "sfx_fire":         _sfx_fire,
    "sfx_melee":        _sfx_melee,
    "sfx_psi":          _sfx_psi,
    "sfx_hit":          _sfx_hit,
    "sfx_miss":         _sfx_miss,
    "sfx_death":        _sfx_death,
    "sfx_overwatch":    _sfx_overwatch,
    "sfx_move":         _sfx_move,
    "sfx_turn_player":  _sfx_turn_player,
    "sfx_turn_enemy":   _sfx_turn_enemy,
    "sfx_victory":      _sfx_victory,
    "sfx_defeat":       _sfx_defeat,
    "sfx_ui_click":     _sfx_ui_click,
    "sfx_deploy":       _sfx_deploy,
    "sfx_reinforce":    _sfx_reinforce,
    "sfx_stun":         _sfx_stun,
    "sfx_bleed":        _sfx_bleed,
}

_MUSIC_MAP = {
    "music_battle":    _music_battle,
    "music_briefing":  _music_briefing,
    "music_debrief":   _music_debrief,
}


def main() -> None:
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating SFX …")
    for name, fn in _SFX_MAP.items():
        _save(SFX_DIR / f"{name}.wav", fn())

    print("Generating music …")
    for name, fn in _MUSIC_MAP.items():
        _save(MUSIC_DIR / f"{name}.wav", fn())

    print(f"\nDone — {len(_SFX_MAP)} SFX + {len(_MUSIC_MAP)} music tracks.")


if __name__ == "__main__":
    main()
