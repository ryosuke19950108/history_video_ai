#!/usr/bin/env python3
"""Assemble films/himiko-test: a ~1 minute cut of the real film that touches every layout,
so the whole pipeline (timeline → mix → checks → render → mux → srt → poster) is proved before the long render."""
import json, os, shutil

SRC = '/home/user/history_video_ai/films/himiko'
DST = '/home/user/history_video_ai/films/himiko-test'
# one sentence per layout, in script order
PICK = ['s12', 's14', 's37', 's46', 's49', 's54', 's106', 's146', 's147', 's161', 's167', 's215', 's228']

os.makedirs(DST, exist_ok=True)
for d in ('voice', 'out', 'fonts', 'assets', 'tools'):
    os.makedirs(f'{DST}/{d}', exist_ok=True)
for f in ('index.html', 'mix.py', 'assets.json', 'SOURCES.jsonl'):
    shutil.copy(f'{SRC}/{f}', f'{DST}/{f}')
for d in ('fonts', 'assets'):
    for f in os.listdir(f'{SRC}/{d}'):
        shutil.copy(f'{SRC}/{d}/{f}', f'{DST}/{d}/{f}')

lines = json.load(open(f'{SRC}/lines.json', encoding='utf-8'))
scenes_doc = json.load(open(f'{SRC}/scenes.json', encoding='utf-8'))
scenes = scenes_doc['scenes']
by_id = {l['id']: (l, s) for l, s in zip(lines, scenes)}

L2, S2 = [], []
for i, sid in enumerate(PICK):
    l, s = by_id[sid]
    l = dict(l); l['para'] = i          # each its own paragraph: full pause between picks
    s = {k: v for k, v in s.items() if k != 'cont'}   # no predecessor in this cut
    L2.append(l); S2.append(s)
json.dump(L2, open(f'{DST}/lines.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
out = dict(scenes_doc); out['title'] = '卑弥呼の正体（テスト）'; out['scenes'] = S2
json.dump(out, open(f'{DST}/scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

dur = json.load(open(f'{SRC}/voice/dur.json'))
tim = json.load(open(f'{SRC}/voice/timing.json'))
json.dump({k: dur[k] for k in PICK}, open(f'{DST}/voice/dur.json', 'w'), indent=1)
json.dump({k: tim[k] for k in PICK}, open(f'{DST}/voice/timing.json', 'w'), indent=1)
for sid in PICK:
    shutil.copy(f'{SRC}/voice/{sid}.wav', f'{DST}/voice/{sid}.wav')

sh = open(f'{SRC}/build.sh').read().replace('himiko', 'himiko-test')
open(f'{DST}/build.sh', 'w').write(sh)
print(f'{len(PICK)} scenes, narration {sum(dur[k] for k in PICK):.1f} s')
print('layouts:', sorted({s["layout"] for s in S2}))
