#!/usr/bin/env python3
"""
Distorsiona una risa para la Nutria Abismal y la convierte a .ogg mono (Minecraft).
Uso:  python3 tools/make_laugh.py <entrada.mp3> [salida.ogg]
Requiere ffmpeg (con libvorbis), numpy y scipy.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "otterfall",
    "sounds", "entity", "otter_horror_laugh.ogg")

tmp = tempfile.mkdtemp()
wav_in = os.path.join(tmp, "in.wav")
wav_out = os.path.join(tmp, "out.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), wav_in], check=True)
w = wave.open(wav_in)
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768

# recortar silencios
idx = np.where(np.abs(a) > 0.01)[0]
a = a[max(0, idx[0] - int(0.03 * SR)): min(len(a), idx[-1] + int(0.1 * SR))]


def resample(x, factor):
    """factor<1 = mas grave y mas lento."""
    n = int(len(x) / factor)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def pad(x, n):
    return np.pad(x, (0, max(0, n - len(x))))[:n]


deep = resample(a, 0.80)
sub = resample(a, 0.50)
n = max(len(deep), len(sub), len(a))
mix = pad(deep, n) * 0.85 + pad(sub, n) * 0.55 + pad(a, n) * 0.25

# vibrato lento + modulacion en anillo (voz demoniaca)
t = np.arange(n) / SR
mix = mix * (0.78 + 0.22 * np.sin(2 * np.pi * 6.5 * t))
ring = mix * np.sin(2 * np.pi * 47 * t)
mix = mix * 0.72 + ring * 0.38

# bitcrusher (muestreo reducido + cuantizacion)
hold = 3
crushed = np.repeat(mix[::hold], hold)[:n]
crushed = np.round(crushed * 48) / 48
mix = mix * 0.55 + crushed * 0.45

# saturacion
mix = np.tanh(mix * 3.2) * 0.8

# filtros
mix = sosfilt(butter(4, 55, "highpass", fs=SR, output="sos"), mix)
mix = sosfilt(butter(4, 7500, "lowpass", fs=SR, output="sos"), mix)

# reverberacion de cueva (impulso de ruido decreciente)
rng = np.random.default_rng(7)
ir_len = int(1.1 * SR)
ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.28 * SR))
ir[0] = 1.0
wet = np.pad(fftconvolve(mix, ir * 0.06), (0, 2))[: n + ir_len]
dry = np.pad(mix, (0, ir_len))
res = dry * 0.8 + wet * 0.55

# normalizar y fundidos
res = res / np.max(np.abs(res)) * 0.9
fi, fo = int(0.02 * SR), int(0.35 * SR)
res[:fi] *= np.linspace(0, 1, fi)
res[-fo:] *= np.linspace(1, 0, fo)

pcm = (np.clip(res, -1, 1) * 32767).astype(np.int16)
with wave.open(wav_out, "wb") as o:
    o.setnchannels(1)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_out, "-c:a", "libvorbis", "-q:a", "5", "-ac", "1", out], check=True)
print("OK", out, round(len(res) / SR, 2), "s")
