#!/usr/bin/env python3
"""Long-form mix → out/mix.wav (48 kHz stereo). Timings from film.json, levels from config/style.json (sound.*).
Score (synthesized, no samples): a warm drone whose chord changes at every chapter card, a slow two-note figure that
breathes under long stretches, bells when a mystery is settled, paper on document cards, a low thump after the short
near-silence before each chapter card. Narration from VOICEVOX, music about sound.music_below_voice_db under it."""
import json, os, sys
import numpy as np, soundfile as sf, soxr
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get('LIB') or os.path.expanduser('~/lemo-opuscar'))
from core.audio.sfx import SR, add, bp, hp, lp, noise, t_, thump, compress, limit

F = json.load(open(os.path.join(D, 'film.json'), encoding='utf-8')); SND = F['style']['sound']; SC = F['scenes']
DUR = F['dur']; N = int(DUR * SR); tt = np.arange(N, dtype=np.float64) / SR
mus = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); voc = np.zeros(N, np.float32)

# ── chord plan: one chord per chapter (D minor → F → B♭ → G minor → D), changes on chapter cards ──
chap = [0.0] + [s['t0'] for s in SC if s['layout'] == 'chapter'] + [F['end']['t0']]
chords = [(73.42, 110.0, 146.83), (87.31, 130.81, 174.61), (58.27, 87.31, 116.54), (98.0, 146.83, 196.0), (73.42, 110.0, 146.83), (73.42, 110.0, 146.83)]
def tone(f, lo, hi):
    n0, n1 = int(lo * SR), min(N, int(hi * SR)); t = tt[n0:n1]; ph = 2 * np.pi * f * t
    w = np.sin(ph) + .3 * np.sin(2 * ph) + .1 * np.sin(3 * ph); env = np.clip((t - lo) / 3, 0, 1) * np.clip((hi - t) / 3, 0, 1)
    out = np.zeros(N); out[n0:n1] = w * env; return out
dr = np.zeros(N)
for i in range(len(chap) - 1):
    for j, f in enumerate(chords[i % len(chords)]):
        dr += tone(f, max(0, chap[i] - 1.5), chap[i + 1] + 1.5) * (.55, .4, .22)[j]
dr = lp(dr, 900) * (0.85 + 0.15 * np.sin(2 * np.pi * tt / 11.0))
# near-silence 1.2 s before each chapter card, returning with the card
dip = np.ones(N)
for c in chap[1:-1]:
    dip *= 1 - .9 * np.clip((tt - (c - 1.4)) / .5, 0, 1) * np.clip((c + .25 - tt) / .25, 0, 1)
fade = np.clip(tt / 3, 0, 1) * np.clip((DUR - tt) / 4, 0, 1)
dr = dr * dip * fade
# a slow two-note figure (fifth above the root) every 8 s, very soft, so long stretches breathe
fig = np.zeros(N)
for i in range(len(chap) - 1):
    root = chords[i % len(chords)][0] * 4
    for k, t0 in enumerate(np.arange(chap[i] + 4, chap[i + 1] - 4, 8.0)):
        for f, dt in ((root, 0), (root * 1.5, .9)):
            d = 2.4; t = t_(d); g = np.sin(2 * np.pi * f * t) * np.exp(-t / .8) * np.minimum(1, t / .01)
            n0 = int((t0 + dt) * SR); fig[n0:n0 + len(g)] += g[:max(0, N - n0)] * .16
fig = fig * dip * fade
mus[:, 0] += (dr + fig * .8).astype(np.float32); mus[:, 1] += (dr * .95 + fig).astype(np.float32)

def bell(f=587.33, v=1.0, d=3.5):
    t = t_(d); return v * (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.4) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .5)
                         + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .2)) * np.minimum(1, t / .004)
def paper(v=1.0):
    d = .45; t = t_(d); return v * bp(noise(d), 1800, 7000) * np.exp(-t / .12) * (1 + .6 * np.sin(2 * np.pi * 23 * t))
for s in SC:
    if s['layout'] == 'mysteries' and s.get('reveal') is not None: add(fx, bell(659.25, .14), s['t0'] + .3, 1.0, .1)
    if s['layout'] == 'chapter': add(fx, thump(.5, 55), s['t0'] + .05, 1.0, 0); add(fx, bell(440.0, .08), s['t0'] + .3, 1.0, -.1)
    if s['layout'] == 'doc': add(fx, paper(.16), s['t0'] + .1, 1.0, -.15)
    if s['layout'] == 'photo' and s.get('outline'): add(fx, bell(587.33, .05), s['t0'] + .5, 1.0, .2)
    d = .9; t = t_(d); add(fx, lp(noise(d), 700) * np.sin(np.pi * t / d) * .03, s['t1'] - .45, 1.0, 0)

for s in SC:
    w, sr = sf.read(os.path.join(D, 'voice', s['id'] + '.wav'), dtype='float32')
    if w.ndim > 1: w = w.mean(axis=1)
    w = hp(soxr.resample(w, sr, SR), 80); n0 = int(s['voice'] * SR); voc[n0:n0 + len(w)] += w[:max(0, N - n0)]
voc = compress(voc, thr=.18, ratio=3.0)

speak = np.abs(voc) > 1e-4
env = np.convolve(speak.astype(np.float32), np.ones(int(.25 * SR), np.float32) / int(.25 * SR), 'same')
rms = lambda a, m: float(np.sqrt(np.mean(a[m].astype(np.float64) ** 2))) if m.any() else 0.0
vr, mr = rms(voc, speak), rms(mus[:, 0], speak)
g = (vr / max(mr, 1e-9)) * 10 ** (-SND['music_below_voice_db'] / 20)
duck = 1 - (1 - 10 ** (-3 / 20)) * np.clip(env * 1.5, 0, 1)
out = mus * (g * duck)[:, None] + fx + voc[:, None]
out = limit(out / max(float(np.abs(out).max()), 1e-9) * .89, .9)
os.makedirs(os.path.join(D, 'out'), exist_ok=True)
sf.write(os.path.join(D, 'out', 'mix.wav'), out.astype(np.float32), SR, subtype='PCM_24')
print(f'mix.wav {DUR:.1f} s · music gain {20*np.log10(g):.1f} dB · voice/music while speaking {20*np.log10(vr/max(mr*g,1e-9)):.1f} dB')
