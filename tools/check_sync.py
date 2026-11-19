#!/usr/bin/env python3
"""Check that a finished film's narration really sits where the timeline says it does.

A film is built from film.json: the picture and the subtitles are drawn from the scene times, and
out/mix.wav places each scene's voice at its `voice` second. If the timeline is rebuilt and the mix
is not, both files still look healthy on their own — the picture is the right length, the subtitles
are well formed — but the narration slides further and further out of step with the words on screen.
This catches that before anyone watches it.

  python tools/check_sync.py films/himiko                  # checks films/himiko/himiko.mp4
  python tools/check_sync.py films/himiko --media out.mp4 --n 10 --tol 0.2

Each sample takes the first seconds of one scene's voice/<id>.wav and looks for it in the film's own
audio, searching a window around where the timeline says it should be. Exit 0 if every sample lands
within --tol of its expected second, 1 if any drifts, 2 if the check could not run.
"""
import argparse, io, json, os, subprocess, sys

import numpy as np
import soundfile as sf
import soxr
from scipy.signal import fftconvolve

SR = 16000
CLIP = 3.0      # seconds of voice used as the needle
WINDOW = 40.0   # seconds searched either side of the expected position


def read_audio(media, t0, dur):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', media,
                        '-vn', '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'],
                       capture_output=True)
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError(f'cannot read audio from {media}: {p.stderr.decode()[-300:]}')
    w, _ = sf.read(io.BytesIO(p.stdout), dtype='float32')
    return w.mean(axis=1) if w.ndim > 1 else w


def find(hay, needle):
    """position of the best match of needle in hay, in samples, and how good it is (0-1)"""
    hay = (hay - hay.mean()).astype(np.float64); needle = (needle - needle.mean()).astype(np.float64)
    m = len(needle)
    c = fftconvolve(hay, needle[::-1], 'valid')                   # same as np.correlate, minutes faster
    cs = np.concatenate(([0.0], np.cumsum(hay ** 2)))
    energy = np.sqrt(np.maximum(cs[m:] - cs[:-m], 0.0))           # sliding window energy
    c = c / (energy + 1e-9) / (np.linalg.norm(needle) + 1e-9)
    k = int(np.argmax(c))
    return k, float(c[k])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('film', help='the film folder (the one holding film.json and voice/)')
    ap.add_argument('--media', help='the finished film to check (default: <folder name>.mp4 inside it)')
    ap.add_argument('--n', type=int, default=8, help='how many scenes to sample (default 8)')
    ap.add_argument('--tol', type=float, default=0.25, help='allowed drift in seconds (default 0.25)')
    ap.add_argument('--min-peak', type=float, default=0.35, help='below this the sample is inconclusive, not a failure')
    a = ap.parse_args()

    d = os.path.abspath(a.film)
    media = a.media or os.path.join(d, os.path.basename(d) + '.mp4')
    if not os.path.isfile(media):
        print(f'✗ no film to check at {media}', file=sys.stderr); return 2
    F = json.load(open(os.path.join(d, 'film.json'), encoding='utf-8'))
    SC = [s for s in F['scenes'] if os.path.isfile(os.path.join(d, 'voice', s['id'] + '.wav'))]
    if not SC:
        print('✗ no narration found to check against', file=sys.stderr); return 2

    picks = [SC[round(i * (len(SC) - 1) / max(1, a.n - 1))] for i in range(min(a.n, len(SC)))]
    worst, bad, weak = 0.0, 0, 0
    for s in picks:
        v, sr = sf.read(os.path.join(d, 'voice', s['id'] + '.wav'), dtype='float32')
        if v.ndim > 1: v = v.mean(axis=1)
        v = soxr.resample(v, sr, SR)[:int(CLIP * SR)]
        if len(v) < SR * 0.4:
            continue
        t0 = max(0.0, s['voice'] - WINDOW)
        hay = read_audio(media, t0, WINDOW * 2 + len(v) / SR)
        if len(hay) < len(v):
            continue
        k, peak = find(hay, v)
        drift = t0 + k / SR - s['voice']
        mark = '  ' if abs(drift) <= a.tol else '✗ '
        if peak < a.min_peak:
            mark, weak = '? ', weak + 1
        elif abs(drift) > a.tol:
            bad += 1; worst = max(worst, abs(drift))
        print(f'{mark}{s["id"]:>5}  台本 {s["voice"]:8.2f} s  実際 {t0 + k / SR:8.2f} s  ずれ {drift:+6.2f} s  一致度 {peak:.2f}')

    if bad:
        print(f'\n✗ 音声が映像とずれています（最大 {worst:.2f} 秒、{bad}/{len(picks)} 箇所）。'
              f'film.json を作り直したあとに mix.py を回していないときに起きます', file=sys.stderr)
        return 1
    if weak == len(picks):
        print('\n? どの箇所も照合できませんでした（音楽が大きすぎる、音声が無い）', file=sys.stderr)
        return 2
    print(f'\n✓ 音声・字幕・映像が一致しています（{len(picks) - weak} 箇所、ずれ {a.tol} 秒以内）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
