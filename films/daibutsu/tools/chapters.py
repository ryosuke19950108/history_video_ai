#!/usr/bin/env python3
"""film.json → CHAPTERS.txt (YouTube chapter list; first line is 「◼︎目次」, first chapter must start at 0:00).
  python tools/chapters.py
Chapters are chosen by hand below: the sentence each section opens with."""
import json

CH = [
    ('s01', 'はじめに：500トンの銅と260万人の記録'),
    ('s12', '聖武天皇と、大仏造立の詔'),
    ('s39', '752年 開眼供養の日'),
    ('s51', '今の大仏の大きさと、4つの謎'),
    ('s64', '謎1 何をどれだけ使ったか'),
    ('s88', '謎2 材料はどこから来たか'),
    ('s106', '謎3 15メートルにどう流し込んだか'),
    ('s171', '謎4 何人が何年かけたか'),
    ('s217', '今の大仏はいつのものか'),
    ('s227', '結論：土の山に埋めながら、8回で'),
]

F = json.load(open('film.json', encoding='utf-8'))
at = {s['id']: s['t0'] for s in F['scenes']}
out = ['◼︎目次']
for i, (sid, title) in enumerate(CH):
    t = 0 if i == 0 else int(at[sid])
    out.append(f'{t // 60}:{t % 60:02d} {title}')
open('CHAPTERS.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
