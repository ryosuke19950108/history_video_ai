#!/usr/bin/env python3
"""Assemble films/himiko-test: the real opening of the film, from the first sentence, as a ~1 minute cut.
Paragraph structure and continued shots are kept exactly as in the full film, so the pacing is what the
finished video will have."""
import json, os, shutil

SRC = '/home/user/history_video_ai/films/himiko'
DST = '/home/user/history_video_ai/films/himiko-test'
N = 12   # s01 … s12 — the opening block, ending on 「最後に答え合わせをしましょう。」

shutil.rmtree(DST, ignore_errors=True)
for d in ('voice', 'out', 'fonts', 'assets', 'tools'):
    os.makedirs(f'{DST}/{d}', exist_ok=True)
for f in ('index.html', 'mix.py', 'assets.json', 'SOURCES.jsonl'):
    shutil.copy(f'{SRC}/{f}', f'{DST}/{f}')
for d in ('fonts', 'assets'):
    for f in os.listdir(f'{SRC}/{d}'):
        shutil.copy(f'{SRC}/{d}/{f}', f'{DST}/{d}/{f}')

lines = json.load(open(f'{SRC}/lines.json', encoding='utf-8'))[:N]
scenes_doc = json.load(open(f'{SRC}/scenes.json', encoding='utf-8'))
scenes = [dict(s) for s in scenes_doc['scenes'][:N]]
scenes[0].pop('cont', None)          # nothing precedes the first shot
ids = [l['id'] for l in lines]

json.dump(lines, open(f'{DST}/lines.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
out = dict(scenes_doc); out['title'] = '卑弥呼の正体（冒頭・テスト）'; out['scenes'] = scenes
json.dump(out, open(f'{DST}/scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

dur = json.load(open(f'{SRC}/voice/dur.json'))
tim = json.load(open(f'{SRC}/voice/timing.json'))
json.dump({k: dur[k] for k in ids}, open(f'{DST}/voice/dur.json', 'w'), indent=1)
json.dump({k: tim[k] for k in ids}, open(f'{DST}/voice/timing.json', 'w'), indent=1)
for sid in ids:
    shutil.copy(f'{SRC}/voice/{sid}.wav', f'{DST}/voice/{sid}.wav')

open(f'{DST}/build.sh', 'w').write(open(f'{SRC}/build.sh').read().replace('himiko', 'himiko-test'))
print(f'{len(ids)} scenes ({ids[0]}–{ids[-1]}), narration {sum(dur[k] for k in ids):.1f} s')
for l, s in zip(lines, scenes):
    print(f"  {l['id']} {s['layout']:10s} {l['text'][:38]}")
