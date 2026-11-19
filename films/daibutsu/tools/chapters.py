#!/usr/bin/env python3
"""film.json → CHAPTERS.txt (YouTube chapter list; first line is 「◼︎目次」, first chapter must start at 0:00).
  python tools/chapters.py
Chapters are chosen by hand below: the sentence each section opens with."""
import json

CH = [
    ('s01', 'はじめに：500トンの銅と260万人の記録'),
    ('s12', '盧舎那仏と聖武天皇の時代'),
    ('s24', '知識寺の仏と、唐の龍門の仏'),
    ('s32', '草1本、土ひとにぎりでも — 大仏造立の詔'),
    ('s36', '紫香楽から東大寺へ'),
    ('s39', '752年 開眼供養の日'),
    ('s51', '今の大仏と大仏殿の大きさ'),
    ('s57', '今回の4つの謎'),
    ('s64', '謎1 何をどれだけ使ったか'),
    ('s69', '熟銅73万9560斤 ＝ 440〜500トン'),
    ('s76', '金440キロと水銀2.5トン'),
    ('s88', '謎2 材料はどこから来たか'),
    ('s91', '長登銅山 ― 奈良へ送られた銅'),
    ('s99', 'いちばん困ったのは金'),
    ('s106', '謎3 15メートルにどう流し込んだか'),
    ('s111', '土と木の原型、そして外型'),
    ('s120', '8回に分けて鋳込む'),
    ('s123', '土を盛って地面ごと高くする'),
    ('s136', '巻き毛と、工事を率いた技術者'),
    ('s152', '749年 陸奥の国で金が見つかる'),
    ('s162', '万葉集 大伴家持の歌'),
    ('s171', '謎4 何人が何年かけたか'),
    ('s177', '260万3638人の内訳'),
    ('s187', '1日あたり、およそ1000人'),
    ('s195', '42万人の寄進と、行基'),
    ('s209', '3つの弱点'),
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
