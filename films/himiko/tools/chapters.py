#!/usr/bin/env python3
"""film.json → CHAPTERS.txt (YouTube chapter list; first line is 「◼︎目次」, first chapter must start at 0:00).
  python tools/chapters.py
Chapters are chosen by hand below: the sentence each section opens with."""
import json

CH = [
    ('s01', 'はじめに：卑弥呼の名は日本の歴史書にない'),
    ('s14', '魏志倭人伝というたった2000字の記録'),
    ('s18', '帯方郡から邪馬台国への道のり'),
    ('s22', '倭の国の乱と、女王の登場'),
    ('s36', '239年 魏への使いと親魏倭王の金印'),
    ('s50', '狗奴国との争いと、13歳の壹与'),
    ('s57', '日本の記録には1行も出てこない'),
    ('s59', '300年続いた論争の歴史'),
    ('s75', '2つのルールと4つの物差し'),
    ('s84', '候補1 天照大神'),
    ('s102', '天照大神 12点'),
    ('s106', '候補2 神功皇后'),
    ('s110', '日本書紀が引用していた魏志'),
    ('s124', '120年のずれ 七支刀が示すもの'),
    ('s137', '神功皇后 13点'),
    ('s142', '候補3 九州の女王'),
    ('s149', '平原遺跡と吉野ヶ里遺跡'),
    ('s164', '九州の女王 13点'),
    ('s177', '候補4 倭迹迹日百襲姫'),
    ('s205', '纒向遺跡と2700個の桃の種'),
    ('s217', '箸墓古墳は3世紀の中ごろ'),
    ('s223', '倭迹迹日百襲姫 15点'),
    ('s225', '最終的な採点と3つの弱点'),
    ('s239', '結論：卑弥呼に最も近い人物'),
]

F = json.load(open('film.json', encoding='utf-8'))
at = {s['id']: s['t0'] for s in F['scenes']}
out = ['◼︎目次']
for i, (sid, title) in enumerate(CH):
    t = 0 if i == 0 else int(at[sid])
    out.append(f'{t // 60}:{t % 60:02d} {title}')
open('CHAPTERS.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
