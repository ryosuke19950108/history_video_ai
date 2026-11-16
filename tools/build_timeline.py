#!/usr/bin/env python3
"""scenes.json + lines.json + voice/dur.json (+ voice/timing.json) + config/style.json → film.json and cues.json.

  python tools/build_timeline.py <film_dir> [--end 5.0]

One sentence = one scene; the scene lasts exactly as long as its voice plus the lead-in and tail from config/style.json
(handbook 6-2: "the real length of the audio is the length of the scene"). Subtitles: one line per cue, never wider than
type.subtitle_safe_width; a longer sentence is split at the 、 nearest its middle and the time is shared by spoken length.
Every cue holds at least 1.8 s and at least speech + 0.6 s when the next line leaves room (DIRECTOR.md §7)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
film = sys.argv[1]
END = float(sys.argv[sys.argv.index('--end') + 1]) if '--end' in sys.argv else 5.0
ST = json.load(open(os.path.join(ROOT, 'config/style.json')))
SC = json.load(open(os.path.join(film, 'scenes.json'), encoding='utf-8'))
LN = json.load(open(os.path.join(film, 'lines.json'), encoding='utf-8'))
DU = json.load(open(os.path.join(film, 'voice/dur.json')))
lead, tail = ST['motion']['lead_in_s'], ST['motion']['tail_s']
# inside a paragraph the pause between sentences is shorter (motion.gap_in_paragraph_s split as lead/tail)
gin = ST['motion'].get('gap_in_paragraph_s')
px, safe = ST['type']['subtitle_px'], ST['type']['subtitle_safe_width']
assert len(SC['scenes']) == len(LN), f'{len(SC["scenes"])} scenes for {len(LN)} sentences'


def width(s):  # estimated rendered width: CJK full width, digits/latin about 0.58 em
    return sum(px * (0.58 if ord(c) < 0x2E80 else 1.0) for c in s)


def split(text):
    """Split into parts that fit the safe width, at 、 (then 。」 ) closest to the middle."""
    if width(text) <= safe:
        return [text]
    cands = [i + 1 for i, c in enumerate(text[:-1]) if c in '、，']
    if not cands:
        cands = [len(text) // 2]
    ok = [i for i in cands if min(width(text[:i]), width(text[i:])) >= .3 * width(text)]   # no tiny fragments
    if not ok:   # no comma near the middle: break after a particle in the middle third instead
        ok = [i for i in range(1, len(text) - 1) if text[i - 1] in 'はがをにでともへや' and text[i] not in '、。」）'
              and .33 * width(text) <= width(text[:i]) <= .67 * width(text)]
    mid = min(ok or cands, key=lambda i: abs(width(text[:i]) - width(text) / 2))
    return split(text[:mid]) + split(text[mid:])


t, scenes, cues = 0.0, [], []
for i, (sc, ln) in enumerate(zip(SC['scenes'], LN)):
    d = DU[ln['id']]
    prev_same = i > 0 and gin is not None and LN[i - 1].get('para') == ln.get('para') is not None
    next_same = i + 1 < len(LN) and gin is not None and LN[i + 1].get('para') == ln.get('para') is not None
    t0 = t; v = t0 + (0.3 if i == 0 else (gin / 2 if prev_same else lead)); t1 = v + d + (gin / 2 if next_same else tail)
    scenes.append({**sc, 'id': ln['id'], 'line': ln['text'], 't0': round(t0, 3), 't1': round(t1, 3), 'voice': round(v, 3), 'vdur': d})
    parts = split(ln['text']); tot = sum(len(p) for p in parts); a = v
    for j, p in enumerate(parts):
        b = a + d * len(p) / tot
        cues.append({'t0': round(a, 3), 'speech_end': round(b, 3), 'text': p.strip()})
        a = b
    t = t1
# hold times: ≥ 1.8 s and ≥ speech + 0.6 s where the next cue leaves room
for k, c in enumerate(cues):
    nxt = cues[k + 1]['t0'] if k + 1 < len(cues) else t
    want = max(c['t0'] + 1.8, c['speech_end'] + 0.6)
    c['t1'] = round(min(want, nxt) if k + 1 < len(cues) else min(want, t), 3)
    if c['t1'] - c['t0'] < 1.8:
        print(f'! cue {k} holds only {c["t1"]-c["t0"]:.2f} s: {c["text"]}')
end = {'t0': round(t, 3), 't1': round(t + END, 3)}
out = {'title': SC.get('title', ''), 'title_en': SC.get('title_en', ''), 'dur': end['t1'], 'fps': ST['frame']['fps'],
       'scenes': scenes, 'end': end, 'subs': [[c['t0'], c['t1'], c['text']] for c in cues], 'style': ST,
       **{k: v for k, v in SC.items() if k not in ('scenes', '_about', 'title', 'title_en')}}   # film-wide extras (e.g. mysteries, credits)
json.dump(out, open(os.path.join(film, 'film.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([{'t0': c['t0'], 't1': c['t1'], 'text': c['text']} for c in cues], open(os.path.join(film, 'cues.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(scenes)} scenes, {len(cues)} cues, {out["dur"]:.2f} s → {film}/film.json')
for s in scenes:
    print(f'  {s["id"]} {s["t0"]:6.2f}–{s["t1"]:6.2f}  {s["layout"]:<22} {s["line"][:24]}')
