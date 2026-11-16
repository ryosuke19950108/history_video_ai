#!/usr/bin/env python3
"""Mix for 箸墓古墳は誰の墓か → out/mix.wav (48 kHz stereo). All timings from film.json; levels from config/style.json (sound.*).
Layers: warm drone (fifths, synthesized) → bells on each finding → paper / air foley → VOICEVOX narration (music ducked).
Uses Lemo-Opuscar core/audio/sfx.py (procedural, no downloads). A near-silence sits before the question (s04); the first
sound after it is a low thump under the voice (DIRECTOR.md §6)."""
import json, os, sys
import numpy as np, soundfile as sf, soxr
D = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ.get('LIB') or os.path.expanduser('~/lemo-opuscar')
sys.path.insert(0, LIB)
from core.audio.sfx import SR, add, bp, hp, lp, noise, env_exp, t_, thump, compress, limit, norm

F = json.load(open(os.path.join(D, 'film.json'), encoding='utf-8')); SND = F['style']['sound']
DUR = F['dur']; N = int(DUR * SR)
mus = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); voc = np.zeros((N, 2), np.float32)
sc = {s['layout'] + ('' if s['layout'] != 'theories' else str(s['step'])): s for s in F['scenes']}
q = sc['question']
tt = np.arange(N) / SR

# ── drone: D2 + A2 + D3, soft saw low-passed, slow breathing; dips to near-silence before the question ──
def voice_(f, det=0.0):
    ph = 2 * np.pi * f * (1 + det) * tt
    return np.sin(ph) + .3 * np.sin(2 * ph) + .12 * np.sin(3 * ph)
dr = .55 * voice_(73.42) + .4 * voice_(110.0, .0015) + .22 * voice_(146.83, -.001)
dr = lp(dr, 900) * (0.85 + 0.15 * np.sin(2 * np.pi * tt / 9.0))
envd = np.clip(tt / 2.5, 0, 1) * np.clip((DUR - tt) / 3.0, 0, 1)
dip = 1 - .92 * np.clip((tt - (q['t0'] - .6)) / .5, 0, 1) * np.clip((q['voice'] + .05 - tt) / .3, 0, 1)
dr = dr * envd * dip
mus[:, 0] += dr * .9; mus[:, 1] += dr * .9
# a second, higher layer (A3/E4) from the measured photo onward, a lift for the findings
hi = (np.sin(2 * np.pi * 220 * tt) + .6 * np.sin(2 * np.pi * 329.63 * tt)) * np.clip((tt - sc['measured_outline']['t0']) / 3, 0, 1) * envd * dip
hi = lp(hi, 1500) * .12
mus[:, 0] += hi * .7; mus[:, 1] += hi

# ── bells on findings: a soft struck tone (inharmonic partials, long decay) ──
def bell(f=587.33, v=1.0, d=3.5):
    t = t_(d); return v * (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.4) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .5)
                         + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .2)) * np.minimum(1, t / .004)
for at, f, v in [(sc['measured_outline']['t0'] + 2.4, 587.33, .22), (sc['source_meets_measure']['t0'] + .7, 659.25, .2),
                 (sc['year_band']['t0'] + .5, 587.33, .2), (sc['map_locator']['t0'] + .8, 440.0, .16)]:
    add(fx, bell(f, v * .5), at, 1.0, .1)
# paper on the document cards
def paper(v=1.0):
    d = .45; t = t_(d); return v * bp(noise(d), 1800, 7000) * np.exp(-t / .12) * (1 + .6 * np.sin(2 * np.pi * 23 * t))
for s in F['scenes']:
    if s['layout'] in ('document_highlight', 'source_meets_measure'):
        add(fx, paper(.18), s['t0'] + .2, 1.0, -.15)
# the thump after the silence
add(fx, thump(.55, 55), q['voice'] - .02, 1.0, 0)
# air on every lamp-dim dissolve (very quiet)
for s in F['scenes']:
    d = .9; t = t_(d); air = lp(noise(d), 700) * np.sin(np.pi * t / d) * .035
    add(fx, air, s['t1'] - .45, 1.0, 0)

# ── narration ──
for s in F['scenes']:
    w, sr = sf.read(os.path.join(D, 'voice', s['id'] + '.wav'), dtype='float32')
    if w.ndim > 1: w = w.mean(axis=1)
    w = soxr.resample(w, sr, SR); w = hp(w, 80)
    add(voc, w, s['voice'], 1.0, 0)
v = voc[:, 0]; v = compress(v, thr=.18, ratio=3.0); voc[:, 0] = v; voc[:, 1] = v

# ── balance: music about sound.music_below_voice_db under the voice (RMS while speaking), ducked a further 3 dB under speech ──
speak = np.abs(voc[:, 0]) > 1e-4
env = np.convolve(speak.astype(np.float32), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
rms = lambda a, m: float(np.sqrt(np.mean(a[m] ** 2))) if m.any() else 0.0
vr = rms(voc[:, 0], speak); mr = rms(mus[:, 0], speak)
g = (vr / max(mr, 1e-9)) * 10 ** (-SND['music_below_voice_db'] / 20)
duck = 1 - (1 - 10 ** (-3 / 20)) * np.clip(env * 1.5, 0, 1)
out = mus * (g * duck)[:, None] + fx + voc
out = limit(out / max(np.abs(out).max(), 1e-9) * .89, .9)
os.makedirs(os.path.join(D, 'out'), exist_ok=True)
sf.write(os.path.join(D, 'out', 'mix.wav'), out.astype(np.float32), SR, subtype='PCM_24')
print(f'mix.wav {DUR:.2f} s · music gain {20*np.log10(g):.1f} dB · voice/music while speaking {20*np.log10(vr/max(mr*g,1e-9)):.1f} dB')
