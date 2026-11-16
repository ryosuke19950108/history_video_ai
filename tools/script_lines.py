#!/usr/bin/env python3
"""Plain-text script → narration lines (handbook 6-2: one sentence = one scene).

  python tools/script_lines.py script.txt lines.json [--scenes scenes.json]

Splits on line breaks and on 。！？ (a closing 」 stays with its sentence); headings, numbering and speaker labels are not expected.
Warns when a sentence falls outside conditions.scene_chars_range in config/style.json. `say` (what VOICEVOX reads) and `asr`
(what the speech check should expect) come from scenes.json when given (same order)."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lo, hi = json.load(open(os.path.join(ROOT, 'config/style.json')))['conditions']['scene_chars_range']
src, dst = sys.argv[1], sys.argv[2]
scenes = json.load(open(sys.argv[sys.argv.index('--scenes') + 1], encoding='utf-8'))['scenes'] if '--scenes' in sys.argv else []
sents = []
for line in open(src, encoding='utf-8'):
    line = line.strip()
    if line:
        sents += [s for s in re.findall(r'[^。！？]+[。！？]?」?', line) if s.strip()]
lines = []
for i, s in enumerate(sents):
    ln = {'id': f's{i+1:02d}', 'text': s}
    for k in ('say', 'asr', 'speed'):
        if i < len(scenes) and scenes[i].get(k):
            ln[k] = scenes[i][k]
    n = len(s)
    if not lo <= n <= hi:
        print(f'! {ln["id"]} has {n} characters (aim for {lo}-{hi}): {s}')
    lines.append(ln)
json.dump(lines, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(lines)} sentences → {dst}')
