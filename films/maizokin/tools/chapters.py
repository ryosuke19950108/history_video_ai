#!/usr/bin/env python3
"""film.json → CHAPTERS.txt (YouTube chapter list; first line is 「◼︎目次」, first chapter must start at 0:00).
  python tools/chapters.py
Chapters are chosen by hand below: the sentence each section opens with."""
import json

CH = [
    ('s01', 'はじめに：12トンか、64トンか'),
    ('s17', '1868年 江戸城が明け渡される'),
    ('s32', '疑われた小栗上野介'),
    ('s44', '赤城山を掘り続けた水野家'),
    ('s68', '5つの候補と3つの物差し'),
    ('s77', '物差し1 360万両を運べたのか'),
    ('s119', '物差し2 幕府に金はあったのか'),
    ('s170', '物差し3 場所を指す記録はあるのか'),
    ('s207', 'この結論の弱点'),
    ('s217', '結論：山の中ではなく海の外'),
]

F = json.load(open('film.json', encoding='utf-8'))
at = {s['id']: s['t0'] for s in F['scenes']}
out = ['◼︎目次']
for i, (sid, title) in enumerate(CH):
    t = 0 if i == 0 else int(at[sid])
    out.append(f'{t // 60}:{t % 60:02d} {title}')
open('CHAPTERS.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
