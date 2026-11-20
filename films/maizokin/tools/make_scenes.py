#!/usr/bin/env python3
"""Scene assignment for 徳川埋蔵金はどこにあるのか (handbook 11-3 step 2), written by Claude Code in the session.
One entry per sentence of script.txt, in order → scenes.json. Layouts: index.html `L.*`.
This film's board is the five places the gold is said to be; each is struck out as a yardstick rules it out.
`koban` (the three coins at their real size), `column` (the pack-horse train), `board` (the five places)
and `ratio` (gold against silver) are this film's own layouts.
The three yardsticks ride in the `mysteries` board, the same way the four questions did in the 大仏 film."""
import json, os, re, sys
from collections import Counter

# places (lat, lon); 概略 where the script itself says「あたり」
EDOJO = [35.68580, 139.75400]     # 江戸城 本丸跡（今の皇居）
TAMACHI = [35.64740, 139.74900]   # 田町の薩摩藩邸（港区、概略）
AKAGI = [36.54970, 139.18600]     # 赤城山 大沼
AKAGI_TOP = [36.55970, 139.19310] # 赤城山 黒檜山
TSUKUDA = [36.51900, 139.01500]   # 津久田原（渋川市赤城町津久田、概略）
GONDA = [36.36470, 138.84280]     # 権田（高崎市倉渕町権田、概略）
NIKKO = [36.75800, 139.59860]     # 日光東照宮
YOKOSUKA = [35.29200, 139.66560]  # 横須賀 第一号船渠
TOBA = [34.93200, 135.74800]      # 鳥羽・伏見（京都市伏見区、概略）
KYOTO = [35.01160, 135.76810]
TADA = [34.90440, 135.34860]      # 多田銀山（兵庫県猪名川町）
KAI = [35.66000, 138.56000]       # 甲斐（武田信玄、概略）
CHOSHU = [34.18500, 131.47100]    # 長州（山口、概略）
URAGA = [35.24700, 139.71800]     # 浦賀

PHOTO, WIKI_NAMES = {}, set()
for l in open('SOURCES.jsonl', encoding='utf-8'):
    r = json.loads(l)
    if r['source'].startswith('GSI tiles'):
        continue
    PHOTO[r['name'].split('/')[-1].rsplit('.', 1)[0]] = r['credit'].replace('Public domain', 'パブリックドメイン')
    if r['source'].startswith('Wikimedia'):
        WIKI_NAMES.add(re.sub(r'（.*', '', r['credit'].replace('写真：', '')).strip())
HAVE = set(PHOTO) | set(json.load(open('assets.json')))
GSI = '出典：国土地理院（地理院タイル）'
NE = '出典：Natural Earth（地図データ、パブリックドメイン）'

# views of the drawn map: centre (lat, lon) and degrees of longitude across the frame
JP = {'c': [36.0, 137.6], 'w': 17}; JPE = {'c': [35.6, 137.6], 'w': 10}
KANTO = {'c': [36.15, 139.45], 'w': 4.2}; KANTO2 = {'c': [36.12, 139.30], 'w': 2.8}
KINKI = {'c': [34.96, 135.70], 'w': 2.2}; PACIFIC = {'c': [35.0, 149.0], 'w': 30}

MYST = ['運べたのか', '幕府に金があったか', '場所を指す記録があるか']
CAND = ['赤城山', '日光', '権田村', '江戸城の中', '最初からなかった']
# the three koban at their real size (長径 mm, 短径 mm) and weight; the gold share as the script gives it
COINS = [{'label': '慶長小判', 'mm': [73, 41], 'g': '17.8'},
         {'label': '天保小判', 'mm': [63, 36], 'g': '11.2'},
         {'label': '万延小判', 'mm': [36, 21], 'g': '3.3'}]


def coins(show=None, fine=False, kicker='小判1枚の重さ', **kw):
    its = [{**c, **({'sub': s} if fine and (s := {'慶長小判': '金 86 %', '万延小判': '金 57 %'}.get(c['label'])) else {})}
           for c in COINS]
    return {'layout': 'koban', 'kicker': kicker, 'items': its, 'show': show, **kw}


def MAP(view, **kw): return {'layout': 'map', 'view': view, 'source': NE, **kw}
def P(img, at, span=(1500, 1350), **kw): return {'layout': 'photo', 'img': img, 'at': at, 'span': list(span), 'source': GSI, **kw}
def CARD(*lines, bg=None, **kw): return {'layout': 'card', 'lines': list(lines), 'bg': bg, **kw}
def CH(num, title, sub, bg=None): return {'layout': 'chapter', 'num': num, 'title': title, 'sub': sub, 'bg': bg}
def MY(status=(), marks=None, focus=None, reveal=None, kicker=None, bg=None):
    return {'layout': 'mysteries', 'names': MYST, 'status': list(status), 'marks': marks, 'focus': focus,
            'reveal': reveal, 'kicker': kicker, 'bg': bg}
def BD(status=(), focus=None, reveal=None, note=None, bg=None):
    return {'layout': 'board', 'names': CAND, 'status': list(status) or ['open'] * 5,
            'focus': focus, 'reveal': reveal, 'note': note, 'bg': bg}
def BARS(kicker, items, bg=None, **kw): return {'layout': 'bars', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def CALC(kicker, rows, bg=None, **kw): return {'layout': 'calc', 'kicker': kicker, 'rows': rows, 'bg': bg, **kw}
def ROWS(kicker, rows, bg=None, **kw): return {'layout': 'rows', 'kicker': kicker,
    'rows': [r if isinstance(r, dict) else {'k': r[0], 'v': r[1] if len(r) > 1 else '', 'hi': len(r) > 2} for r in rows], 'bg': bg, **kw}
def THEO(kicker, items, bg=None, **kw): return {'layout': 'theories', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def COMMENT(text, sub=None, bg=None): return {'layout': 'comment', 'text': text, 'sub': sub, 'bg': bg}
def DOTS(kicker, groups, per=1, unit='人', bg=None, **kw):
    return {'layout': 'dots', 'kicker': kicker, 'per': per, 'unit': unit, 'cols': 30, 'gap': 46, 'r': 16,
            'y0': 360, 'ly': 800, 'lgap': 430, 'groups': groups, 'bg': bg, **kw}
def TL(events, axis=(1825, 1875), step=10, bg=None, **kw):
    return {'layout': 'timeline', 'axis': list(axis), 'step': step, 'events': events, 'bg': bg, **kw}
def COL(items, bg=None, **kw): return {'layout': 'column', 'items': items, 'bg': bg, **kw}
def RT(rows, bg=None, **kw): return {'layout': 'ratio', 'rows': rows, 'bg': bg, **kw}
def B(img, at, span, a=.20): return {'img': img, 'at': at, 'span': span, 'a': a} if img in HAVE else None


BG_AKAGI = B('akagi_hill_z13', AKAGI, 12000, .18); BG_AKAGI_P = B('akagi_z15', AKAGI, 4000, .15)
BG_EDO = B('edojo_z16', EDOJO, 2400, .13); BG_KANTO = B('kanto_hill_z10', [36.12, 139.42], 160000, .14)
BG_GONDA = B('gonda_z16', GONDA, 2400, .13); BG_NIKKO = B('nikko_z17', NIKKO, 900, .13)
BG_TSUKUDA = B('tsukuda_z16', TSUKUDA, 2400, .13); BG_YOKO = B('yokosuka_z16', YOKOSUKA, 2400, .13)

S = [
 # ── はじめに：重さの食い違い ──
 CARD('360万両の重さは', '12トンにも、64トンにも', kicker='徳川埋蔵金', sub='どの小判で数えるかによって', bg=BG_AKAGI, fs=72),                        # s01
 BARS('360万両の重さ', [{'label': '万延小判', 'value': 12, 'text': '12 t'}, {'label': '天保小判', 'value': 40, 'text': '40 t'},
                   {'label': '慶長小判', 'value': 64, 'text': '64 t', 'hi': True}], note='小判1枚＝1両として計算', bg=BG_AKAGI),                # s02
 CARD('160年近く', '誰も見つけていない', kicker='この食い違いの中に', bg=BG_AKAGI),                                                            # s03
 P('edojo_z16', EDOJO, (2600, 2200), rings=[{'at': EDOJO, 'm': 420, 'label': '江戸城', 'sub': '御用金はここにあった'}],
   text={'kicker': '言い伝え', 'title': '城の金は山へ'}, scale=500),                                                                      # s04
 P('akagi_z15', AKAGI, (5000, 4000), rings=[{'at': AKAGI, 'm': 900, 'label': '赤城山', 'sub': '群馬県'}],
   text={'kicker': '明治から今まで', 'title': '掘り続けてきた'}, scale=1000),                                                               # s05
 P('akagi_z15', AKAGI, (5000, 4000), text={'kicker': '1990年', 'title': '重機が入った'}),                                               # s06
 P('akagi_z15', AKAGI, (5000, 4000), text={'kicker': '1990年', 'title': '重機が入った', 'note': 'テレビ番組の大がかりな発掘'}),                   # s07
 CARD('小判は1枚も', '見つかっていない', kicker='それでも', gold=1, bg=BG_AKAGI),                                                           # s08
 CARD('徳川埋蔵金は', 'どこにあるのか', center=True, bg=BG_AKAGI),                                                                       # s09
 ROWS('今回やったこと', [('小判1枚の重さを計算する', '慶長・天保・万延')], bg=BG_AKAGI),                                                      # s10
 ROWS('今回やったこと', [('小判1枚の重さを計算する', '慶長・天保・万延'), ('幕末の記録と突き合わせる', '幕府の財政')], bg=BG_AKAGI),                 # s11
 ROWS('今回やったこと', [('小判1枚の重さを計算する', '慶長・天保・万延'), ('幕末の記録と突き合わせる', '幕府の財政'),
                   ('行方を確かめる', '山の中ではなかった', 1)], bg=BG_AKAGI),                                                           # s12
 COMMENT('あなたの予想は？', sub='コメント欄にひとことお願いします', bg=BG_AKAGI),                                                           # s13
 COMMENT('赤城山？ 日光？ それとも別の場所？', bg=BG_AKAGI),                                                                            # s14
 COMMENT('最後に、答え合わせをしましょう', bg=BG_AKAGI),                                                                               # s15
 CARD('この言い伝えは', 'どこから生まれたのか', center=True, bg=BG_AKAGI),                                                               # s16

 # ── 1868年 江戸城明け渡し ──
 CARD('1868年の春', kicker='江戸幕府の終わり', sub='265年続いた幕府が終わろうとしていた', bg=BG_EDO),                                         # s17
 MAP(KINKI, places=[{'at': KYOTO, 'label': '京都', 'r': 9}, {'at': TOBA, 'label': '鳥羽・伏見', 'sub': '幕府の軍が敗れる', 'ring': 34, 'col': 'red', 'side': -1}],
     text={'kicker': '1868年 初め', 'title': '鳥羽・伏見'}),                                                                         # s18
 MAP(JPE, places=[{'at': KYOTO, 'label': '京都', 'r': 8, 'side': -1}, {'at': EDOJO, 'label': '江戸', 'r': 10}],
     routes=[{'pts': [KYOTO, [35.1, 137.0], [35.3, 138.6], EDOJO], 'label': '新政府の軍', 'col': 'red', 'ly': 44}]),                   # s19
 CARD('総攻めは', '3月15日と決まっていた', kicker='江戸の町へ', bg=BG_EDO),                                                              # s20
 THEO('江戸城を明け渡す話し合い', [{'k': '幕府', 'name': '勝海舟', 'sub': '陸軍総裁'}, {'k': '新政府', 'name': '西郷隆盛', 'sub': '東征大総督府参謀'}],
      bg=BG_EDO),                                                                                                                # s21
 P('edojo_z16', EDOJO, (2600, 2200), rings=[{'at': EDOJO, 'm': 420, 'label': '江戸城'}],
   text={'kicker': '話し合いの結果', 'title': '戦わずに明け渡す'}),                                                                     # s22
 P('edojo_z16', EDOJO, (2600, 2200), rings=[{'at': EDOJO, 'm': 420, 'label': '江戸城'}],
   text={'kicker': '1868年4月11日', 'title': '新政府へ引き渡し'}),                                                                    # s23
 CARD('100万人の暮らしが', '守られた', kicker='江戸の町は戦火を免れ', gold=0, bg=BG_EDO),                                                 # s24

 # ── 空っぽだった御金蔵 ──
 P('edojo_z16', EDOJO, (1500, 1300), rings=[{'at': EDOJO, 'm': 220, 'label': '御金蔵', 'sub': 'この一帯（概略）'}],
   text={'kicker': '江戸城のなか', 'title': '幕府の金の蔵'}, scale=300),                                                                # s25
 ROWS('御金蔵破り（1855年）', [('盗まれた小判', '4000両', 1), ('それでも', '厳重に守られた蔵だった')], bg=BG_EDO),                             # s26
 ROWS('御金蔵破り（1855年）', [('盗まれた小判', '4000両', 1), ('それでも', '厳重に守られた蔵だった')], bg=BG_EDO),                             # s27
 CARD('城に入った新政府は', 'ある事実に驚いた', bg=BG_EDO),                                                                             # s28
 CARD('御金蔵は', 'ほとんど空っぽだった', gold=1, bg=BG_EDO),                                                                          # s29
 ROWS('新政府の見込み', [('御用金を', '新しい国づくりの金に充てる')], bg=BG_EDO),                                                          # s30
 ROWS('新政府の見込み', [('御用金を', '新しい国づくりの金に充てる'), ('見当たらない', '誰かが隠したに違いない', 1)], bg=BG_EDO),                   # s31

 # ── 疑われた小栗上野介 ──
 CARD('小栗上野介', kicker='疑いの目が向けられた', sub='幕府の勘定奉行', bg=BG_GONDA, fs=92),                                              # s32
 ROWS('勘定奉行とは', [('役目', '幕府の財政をあずかる'), ('今でいえば', '国の財務大臣', 1)], bg=BG_GONDA),                                   # s33
 CARD('最後まで', '戦うべきだと訴えた', kicker='小栗は', bg=BG_GONDA),                                                                 # s34
 P('gonda_z16', GONDA, (2600, 2200), rings=[{'at': GONDA, 'm': 420, 'label': '権田村', 'sub': '今の高崎市倉渕町'}],
   text={'kicker': '1868年 初め 役を解かれ', 'title': '権田村へ移る'}, scale=500),                                                      # s35
 P('gonda_z16', GONDA, (2600, 2200), rings=[{'at': GONDA, 'm': 420, 'label': '権田村'}],
   text={'kicker': '村へ移るとき', 'title': 'たくさんの荷物'}),                                                                        # s36
 CARD('その荷物こそ', '幕府の御用金ではないか', kicker='噂', bg=BG_GONDA),                                                              # s37
 CARD('小栗は', '表舞台から姿を消した', bg=BG_GONDA),                                                                                # s38
 CARD('残ったのは', '噂だけだった', bg=BG_GONDA),                                                                                   # s39

 # ── 360万両という数字 ──
 CARD('噂は', '具体的な数字を持ちはじめた', bg=BG_AKAGI),                                                                            # s40
 ROWS('語られてきた額', [('よく語られる額', '360万両', 1), ('資料によっては', '400万両')], bg=BG_AKAGI),                                   # s41
 ROWS('語られてきた額', [('よく語られる額', '360万両', 1), ('資料によっては', '400万両'), ('出どころの記録', 'はっきりしない')], bg=BG_AKAGI),     # s42
 CARD('幕府の帳簿に', 'そう書かれていたわけではない', bg=BG_AKAGI),                                                                     # s43

 # ── 赤城山を掘り続けた水野家 ──
 CARD('人生をかけて', '掘り続けた一家があった', bg=BG_TSUKUDA),                                                                       # s44
 P('tsukuda_z16', TSUKUDA, (2600, 2200), rings=[{'at': TSUKUDA, 'm': 420, 'label': '赤城山のふもと', 'sub': '水野家の発掘地（概略）'}],
   text={'kicker': '明治から3代', 'title': '水野家'}, scale=500),                                                                    # s45
 CARD('なぜ赤城山だったのか', center=True, bg=BG_AKAGI),                                                                            # s46
 P('kanto_hill_z10', [36.12, 139.42], (150000, 140000),
   rings=[{'at': EDOJO, 'm': 6000, 'label': '江戸', 'side': -1}, {'at': AKAGI, 'm': 6000, 'label': '赤城山', 'sub': '江戸から北へ約100 km'}],
   text={'kicker': '上州', 'title': '江戸から100キロ'}, scale=20000),                                                                # s47
 P('kanto_hill_z10', [36.12, 139.42], (150000, 140000),
   rings=[{'at': EDOJO, 'm': 6000, 'label': '江戸', 'side': -1}, {'at': AKAGI, 'm': 6000, 'label': '赤城山'}],
   text={'kicker': '上州', 'title': '幕府の土地が多い', 'note': '江戸から街道で数日'}),                                                   # s48
 CARD('江戸に近くて', '幕府の目の届く山', kicker='隠すなら', bg=BG_KANTO),                                                             # s49
 CARD('初代 水野智義', kicker='1851年 生まれる', sub='幕府の家臣の家に', bg=BG_TSUKUDA, fs=84),                                          # s50
 CARD('義理の父から', '打ち明けられた', kicker='赤城山に御用金がある', bg=BG_TSUKUDA),                                                    # s51
 P('tsukuda_z16', TSUKUDA, (2400, 2000), rings=[{'at': TSUKUDA, 'm': 380, 'label': '津久田原', 'sub': '赤城山の西のふもと'}],
   text={'kicker': '明治の初めごろ', 'title': 'ここを掘り始めた'}, scale=500),                                                          # s52
 P('tsukuda_z16', TSUKUDA, (2400, 2000), rings=[{'at': TSUKUDA, 'm': 380, 'label': '津久田原', 'sub': '今の渋川市赤城町のあたり'}],
   text={'kicker': '明治の初めごろ', 'title': 'ここを掘り始めた'}),                                                                     # s53
 CARD('家の財産の多くを', 'この発掘につぎ込んだ', bg=BG_TSUKUDA),                                                                      # s54
 TL([{'y': 1851, 'label': '初代 智義 生まれる', 'side': 1}, {'y': 1890, 'label': '黄金の家康像', 'side': -1},
     {'y': 1990, 'label': 'テレビの大発掘', 'sub': '3代目が力を貸す', 'hi': True, 'side': 1}],
    axis=(1850, 2000), step=25, kicker='3代、100年を超えて', bg=BG_TSUKUDA),                                                        # s55
 TL([{'y': 1851, 'label': '初代 智義 生まれる', 'side': 1}, {'y': 1890, 'label': '黄金の家康像', 'side': -1},
     {'y': 1990, 'label': 'テレビの大発掘', 'sub': '3代目が力を貸す', 'hi': True, 'side': 1}],
    axis=(1850, 2000), step=25, kicker='3代、100年を超えて', bg=BG_TSUKUDA),                                                        # s56
 CARD('黄金の家康像', kicker='1890年 掘り当てたという話', bg=BG_TSUKUDA, fs=92),                                                       # s57
 ROWS('黄金の家康像', [('伝わる話', '1890年に掘り当てた'), ('今どこにあるか', '行方が分からない'), ('本当に金だったか', '確かめられていない', 1)],
      bg=BG_TSUKUDA),                                                                                                            # s58

 # ── 1990年 テレビの大発掘 ──
 CARD('1990年', 'テレビ番組が挑んだ', bg=BG_AKAGI_P),                                                                              # s59
 ROWS('1990年の発掘', [('隊長', '糸井重里'), ('加わった', '建設会社'), ('使った道具', '巨大な重機と地中を探る機械')], bg=BG_AKAGI_P),            # s60
 ROWS('1990年の発掘', [('隊長', '糸井重里'), ('加わった', '建設会社'), ('使った道具', '巨大な重機と地中を探る機械'),
                   ('発掘の回数', '10回'), ('視聴率', '20パーセント前後', 1)], bg=BG_AKAGI_P, gap=112),                                 # s61
 ROWS('1990年の発掘', [('隊長', '糸井重里'), ('加わった', '建設会社'), ('使った道具', '巨大な重機と地中を探る機械'),
                   ('発掘の回数', '10回'), ('視聴率', '20パーセント前後', 1), ('番組のあとも', '特別番組として続いた')], bg=BG_AKAGI_P, gap=98),  # s62
 CARD('小判は1枚も', '出てこなかった', gold=1, bg=BG_AKAGI_P),                                                                       # s63
 CARD('なぜ、これほど掘っても', '見つからないのか', center=True, bg=BG_AKAGI_P),                                                       # s64

 # ── 5つの候補と3つの物差し ──
 MAP(JP, places=[{'at': AKAGI, 'label': '赤城山', 'sub': '徳川', 'col': 'red', 'r': 10, 'side': 1}],
     text={'kicker': '日本の埋蔵金伝説', 'title': '数百か所'}),                                                                       # s65
 MAP(JP, places=[{'at': AKAGI, 'label': '赤城山', 'sub': '徳川', 'col': 'red', 'r': 10, 'side': 1},
                 {'at': KAI, 'label': '甲斐', 'sub': '武田信玄', 'r': 8, 'side': -1, 'col': 'teal'},
                 {'at': TADA, 'label': '多田銀山', 'sub': '豊臣秀吉', 'r': 8, 'side': -1, 'col': 'teal'}],
     text={'kicker': '日本の埋蔵金伝説', 'title': '数百か所'}),                                                                       # s66
 CARD('金額の大きさと', 'テレビで掘り続けられた歴史', kicker='群を抜いて有名', bg=BG_AKAGI),                                              # s67
 BD(note='この5つを1つずつ確かめる', bg=BG_AKAGI),                                                                                  # s68
 BD(focus=0, bg=BG_AKAGI),                                                                                                      # s69
 BD(focus=4, bg=BG_AKAGI),                                                                                                      # s70
 MY(bg=BG_AKAGI),                                                                                                               # s71
 MY(focus=0, bg=BG_AKAGI),                                                                                                      # s72
 MY(focus=1, bg=BG_AKAGI),                                                                                                      # s73
 MY(focus=2, bg=BG_AKAGI),                                                                                                      # s74
 MY(bg=BG_AKAGI),                                                                                                               # s75
 BD(note='消えた数は、その都度お伝えします', bg=BG_AKAGI),                                                                           # s76

 # ── 物差し1 運べたのか ──
 CH('1', '運べたのか', '360万両を山まで運べたか', bg=BG_KANTO),                                                                      # s77
 CARD('小判1枚の重さを', '計算してみる', bg=BG_KANTO),                                                                              # s78
 coins(show=[0], kicker='小判は何度も作り直された'),                                                                                # s79
 coins(show=[0], kicker='小判は何度も作り直された'),                                                                                # s80
 coins(show=[0], kicker='小判は何度も作り直された', note='徳川家康の時代の慶長小判'),                                                    # s81
 coins(show=[0, 1], kicker='小判は何度も作り直された', note='幕末に近い天保小判'),                                                      # s82
 coins(show=[0, 1, 2], kicker='小判は何度も作り直された', note='幕府が最後に作った万延小判'),                                             # s83
 coins(show=[0, 1, 2], kicker='小判は何度も作り直された', note='万延小判は慶長小判のおよそ5分の1の重さ'),                                   # s84
 coins(show=[0, 1, 2], kicker='小判は何度も作り直された', note='変わったのは重さだけではない'),                                           # s85
 coins(show=[0, 1, 2], fine=True, kicker='小判は何度も作り直された', note='金の割合も 86 % から 57 % へ'),                              # s86
 CALC('360万両の重さ', [['17.8 g × 360万枚', '']], bg=BG_KANTO),                                                                  # s87
 CALC('360万両の重さ', [['慶長 17.8 g × 360万枚', '64 t']], bg=BG_KANTO),                                                     # s88
 CALC('360万両の重さ', [['慶長 17.8 g × 360万枚', '64 t'], ['天保 11.2 g × 360万枚', '40 t'],
                   ['万延  3.3 g × 360万枚', '12 t']], bg=BG_KANTO),                                                        # s89
 BARS('360万両の重さ', [{'label': '万延小判', 'value': 12, 'text': '12 t'}, {'label': '天保小判', 'value': 40, 'text': '40 t'},
                   {'label': '慶長小判', 'value': 64, 'text': '64 t', 'hi': True}], note='冒頭の12トンから64トンはここから', bg=BG_KANTO),  # s90
 CARD('中の金だけで比べると', '差はさらに広がる', bg=BG_KANTO),                                                                       # s91
 BARS('中に含まれる金だけ', [{'label': '万延小判', 'value': 7, 'text': '7 t'},
                     {'label': '慶長小判', 'value': 55, 'text': '55 t', 'hi': True}], gap=200, bg=BG_KANTO),                      # s92

 # ── 千両箱と馬 ──
 CARD('これを運ぶには', '何が必要だったのか', center=True, bg=BG_KANTO),                                                             # s93
 ROWS('千両箱', [('中に入れる小判', '1000両ずつ')], bg=BG_KANTO),                                                                   # s94
 ROWS('千両箱', [('中に入れる小判', '1000両ずつ'), ('作り', '木の箱に鉄の帯を巻く'), ('箱そのものにも', '重さがあった')], bg=BG_KANTO),         # s95
 DOTS('360万両＝千両箱 3600箱', [{'n': 3600, 'label': '千両箱 3600箱', 'col': 'gold'}], per=50, unit='箱', bg=BG_KANTO),             # s96
 ROWS('千両箱1箱の小判の重さ', [('万延小判', '3.3 kg'), ('慶長小判', '17.8 kg', 1)], bg=BG_KANTO),                                     # s97
 ROWS('馬1頭に積める荷', [('当時の決まり', '40貫まで'), ('今の重さなら', 'およそ150 kgまで', 1)], bg=BG_KANTO),                           # s98
 CALC('必要な馬の数', [['箱の重さは除いて、小判だけで', '']], bg=BG_KANTO),                                                            # s99
 CALC('必要な馬の数', [['万延 12 t ÷ 150 kg', '80 頭']], bg=BG_KANTO),                                                        # s100
 CALC('必要な馬の数', [['万延 12 t ÷ 150 kg', '80 頭'], ['天保 40 t ÷ 150 kg', '270 頭'],
                  ['慶長 64 t ÷ 150 kg', '430 頭']], bg=BG_KANTO),                                                         # s101
 COL([{'label': '万延小判', 'n': 80, 'm': 400, 'text': '400 m'}, {'label': '天保小判', 'n': 270, 'm': 1350, 'text': '1.35 km'},
      {'label': '慶長小判', 'n': 430, 'm': 2150, 'text': '2.15 km', 'hi': True}], kicker='馬の行列の長さ', bg=BG_KANTO),             # s102
 COL([{'label': '万延小判', 'n': 80, 'm': 400, 'text': '400 m'}, {'label': '天保小判', 'n': 270, 'm': 1350, 'text': '1.35 km'},
      {'label': '慶長小判', 'n': 430, 'm': 2150, 'text': '2.15 km', 'hi': True}], kicker='馬の行列の長さ',
     note='馬1頭あたり5メートルで計算', bg=BG_KANTO),                                                                              # s103
 COL([{'label': '万延小判', 'n': 80, 'm': 400, 'text': '400 m'}, {'label': '天保小判', 'n': 270, 'm': 1350, 'text': '1.35 km'},
      {'label': '慶長小判', 'n': 430, 'm': 2150, 'text': '2.15 km', 'hi': True}], kicker='馬の行列の長さ',
     note='80頭で400メートル、430頭で2キロを超える', bg=BG_KANTO),                                                                 # s104
 ROWS('行列に必要なもの', [('馬', '80〜430頭'), ('引き手', '馬と同じ数の人', 1)], bg=BG_KANTO),                                        # s105
 MAP(KANTO, places=[{'at': EDOJO, 'label': '江戸', 'r': 10, 'side': -1}, {'at': AKAGI, 'label': '赤城山', 'r': 10}],
     routes=[{'pts': [EDOJO, [36.0, 139.52], [36.35, 139.25], AKAGI], 'label': '約100 km・3日以上', 'ly': 40, 'lx': -60}]),       # s106
 MAP(KANTO, places=[{'at': EDOJO, 'label': '江戸', 'r': 10, 'side': -1}, {'at': AKAGI, 'label': '赤城山', 'r': 10}],
     routes=[{'pts': [EDOJO, [36.0, 139.52], [36.35, 139.25], AKAGI], 'label': '約100 km・3日以上', 'ly': 40, 'lx': -60}],
     regions=[{'at': [36.0, 139.6], 'rx': .85, 'ry': .55, 'col': 'red', 'label': '新政府の軍が街道を押さえていた', 'ls': 28, 'ly': 150}]),  # s107
 CARD('誰の目にも留まらずに', '山へ向かうのは難しい', kicker='何百頭もの行列が', bg=BG_KANTO),                                            # s108

 # ── 江戸城の中が消える ──
 BD(bg=BG_EDO),                                                                                                                 # s109
 BD(focus=3, bg=BG_EDO),                                                                                                        # s110
 P('edojo_z16', EDOJO, (2600, 2200), rings=[{'at': EDOJO, 'm': 420, 'label': '江戸城'}],
   text={'kicker': '城を受け取ったあと', 'title': '中を調べている'}),                                                                  # s111
 P('edojo_z16', EDOJO, (2600, 2200), rings=[{'at': EDOJO, 'm': 420, 'label': '東京城', 'sub': '翌年から天皇のお住まい'}],
   text={'kicker': '1868年のうちに', 'title': '東京城と改める'}),                                                                    # s112
 P('edojo_z16', EDOJO, (2600, 2200), rings=[{'at': EDOJO, 'm': 420, 'label': '皇居'}],
   text={'kicker': 'それから150年以上', 'title': '建て替えも工事も'}),                                                                # s113
 CARD('大量の小判が', '見つかったという記録はない', bg=BG_EDO),                                                                       # s114
 CARD('城の中にあれば', '運び出す必要さえなかった', bg=BG_EDO),                                                                       # s115
 CARD('城に残っていた', '可能性は低い', bg=BG_EDO),                                                                                 # s116
 BD(status=['open', 'open', 'open', 'out', 'open'], reveal=3, focus=3, note='5つのうち 1つが消えた', bg=BG_EDO),                     # s117
 BD(status=['open', 'open', 'open', 'out', 'open'], note='残るのは4つ', bg=BG_EDO),                                               # s118

 # ── 物差し2 幕府に金があったか ──
 CH('2', '幕府に金があったか', '360万両が本当にあったか', bg=BG_EDO),                                                                 # s119
 CARD('360万両は', '本当にあったのか', center=True, bg=BG_EDO),                                                                     # s120
 CARD('小栗上野介', kicker='意外な形で、もう一度', bg=BG_GONDA, fs=92),                                                             # s121
 ROWS('小栗上野介', [('幕府の金のこと', '誰よりもよく知っていた', 1)], bg=BG_GONDA),                                                   # s122
 TL([{'y': 1827, 'label': '江戸の旗本の家に生まれる', 'side': 1}, {'y': 1860, 'label': 'アメリカへ渡る', 'hi': True, 'side': -1},
     {'y': 1868, 'label': '権田村へ', 'side': 1}], axis=(1825, 1875), step=10, kicker='小栗上野介', bg=BG_GONDA),                   # s123
 TL([{'y': 1827, 'label': '江戸の旗本の家に生まれる', 'side': 1}, {'y': 1860, 'label': 'アメリカへ渡る', 'hi': True, 'side': -1},
     {'y': 1868, 'label': '権田村へ', 'side': 1}], axis=(1825, 1875), step=10, kicker='小栗上野介', bg=BG_GONDA),                   # s124
 MAP(PACIFIC, places=[{'at': URAGA, 'label': '浦賀', 'r': 8, 'side': -1}],
     routes=[{'pts': [URAGA, [36.0, 152.0], [37.0, 160.0]], 'label': 'アメリカへ', 'ly': -40, 'lx': -120}],
     text={'kicker': '1860年', 'title': '幕府の使節'}),                                                                           # s125
 MAP(PACIFIC, places=[{'at': URAGA, 'label': '浦賀', 'r': 8, 'side': -1}],
     routes=[{'pts': [URAGA, [36.0, 152.0], [37.0, 160.0]], 'label': 'アメリカへ', 'ly': -40, 'lx': -120},
             {'pts': [URAGA, [34.0, 152.0], [33.2, 160.0]], 'label': '咸臨丸', 'col': 'teal', 'ly': 44, 'lx': -80, 't': .9}],
     text={'kicker': '1860年', 'title': '幕府の使節'}),                                                                           # s126
 THEO('1860年 同じ海を渡った二人', [{'k': '咸臨丸', 'name': '勝海舟', 'sub': '8年後、江戸城を明け渡す話し合いへ'},
                          {'k': '幕府の使節', 'name': '小栗上野介', 'sub': '8年後、御用金を隠したと疑われる'}], bg=BG_KANTO),             # s127
 CARD('小判とアメリカの金貨を', '溶かして比べさせた', kicker='フィラデルフィア造幣局', bg=BG_KANTO),                                        # s128
 CARD('なぜ、そんなことを', center=True, bg=BG_KANTO),                                                                             # s129
 CARD('1858年', '外国との取り引きが始まる', bg=BG_KANTO),                                                                           # s130
 RT([{'label': '外国', 'n': 15, 'text': '金1 ＝ 銀15'}], kicker='金と銀の値打ちの比べ方', bg=BG_KANTO),                                # s131
 RT([{'label': '外国', 'n': 15, 'text': '金1 ＝ 銀15'}, {'label': '日本', 'n': 5, 'text': '金1 ＝ 銀5', 'hi': True}],
    kicker='金と銀の値打ちの比べ方', note='同じ金1枚に、外国では銀15枚、日本では銀5枚', bg=BG_KANTO),                                      # s132
 CALC('銀の増え方', [['銀15を日本へ持ち込む', '小判（金3）']], bg=BG_KANTO),                                                           # s133
 CALC('銀の増え方', [['銀15を日本へ持ち込む', '小判（金3）'], ['その小判を外国で売る', '銀45'],
                 ['はじめの銀15が', '3倍']], bg=BG_KANTO),                                                                        # s134
 MAP(JPE, places=[{'at': URAGA, 'label': '開港地', 'r': 8, 'side': -1}],
     routes=[{'pts': [URAGA, [34.8, 140.9], [34.3, 141.7]], 'label': '小判が海の外へ', 'ly': 40, 'lx': -40}],
     text={'kicker': 'こうして', 'title': '小判が流れ出た'}),                                                                       # s135
 ROWS('流れ出た金の量', [('ある研究', '10万両あまり'), ('別の見方', '数十万両'), ('見方は', '分かれている')], bg=BG_KANTO),                  # s136
 CARD('1860年', '小判を作り直す', kicker='幕府はこれを止めるため', bg=BG_KANTO),                                                      # s137
 coins(show=[0, 2], kicker='万延小判（1860年）', note='慶長小判とくらべて'),                                                         # s138
 coins(show=[0, 2], kicker='万延小判（1860年）', note='1枚の重さを3分の1ほどにして、外国との差を埋めた'),                                 # s139
 CARD('国の中では', 'お金の値打ちが下がった', bg=BG_KANTO),                                                                          # s140
 CARD('物の値段が上がり', '暮らしは苦しくなった', bg=BG_KANTO),                                                                       # s141
 CARD('物価への不満も', '幕府から心が離れる理由になった', bg=BG_KANTO),                                                               # s142
 CARD('最後の小判が小さいのは', '金が海外へ流れ出たから', bg=BG_KANTO),                                                               # s143
 CARD('山に埋められる前に', '海の向こうへ消えていた', gold=1, bg=BG_KANTO),                                                           # s144
 ROWS('幕末の幕府の出費', [('長州への出兵', '2度')], bg=BG_YOKO),                                                                   # s145
 ROWS('幕末の幕府の出費', [('長州への出兵', '2度'), ('横須賀の製鉄所', 'フランスの力を借りて着工')], bg=BG_YOKO),                          # s146
 ROWS('幕末の幕府の出費', [('長州への出兵', '2度'), ('横須賀の製鉄所', 'フランスの力を借りて着工'), ('懐の苦しさを示す話', 'もう1つある')],
      bg=BG_YOKO),                                                                                                              # s147
 ROWS('幕末の幕府の出費', [('長州への出兵', '2度'), ('横須賀の製鉄所', 'フランスの力を借りて着工'), ('懐の苦しさを示す話', 'もう1つある'),
                    ('フランスからの借り入れ', '600万ドル（実現せず）', 1)], bg=BG_YOKO),                                             # s148
 CARD('借りようとしていた幕府が', '360万両を蓄えていたとは考えにくい', bg=BG_YOKO, fs=64),                                              # s149
 CARD('ワシントンの造船所を', '見学した', kicker='アメリカで小栗は', bg=BG_YOKO),                                                      # s150
 CARD('持ち帰った1本のねじ', kicker='今も群馬県の寺に', bg=BG_YOKO, fs=84),                                                         # s151
 CARD('日本で同じものを', '作れるようにならなければ', bg=BG_YOKO),                                                                   # s152
 P('yokosuka_z16', YOKOSUKA, (2400, 2000), rings=[{'at': YOKOSUKA, 'm': 320, 'label': '横須賀', 'sub': '幕府が造った製鉄所'}],
   text={'kicker': 'この経験が', 'title': '横須賀につながる'}, scale=500),                                                          # s153
 P('yokosuka_z16', YOKOSUKA, (2400, 2000), rings=[{'at': YOKOSUKA, 'm': 320, 'label': '横須賀'}],
   text={'kicker': '進めたのも', 'title': '小栗上野介'}),                                                                          # s154
 CARD('土蔵付きの売り家として', '残るだろう', kicker='小栗の言葉', bg=BG_YOKO),                                                       # s155
 P('yokosuka_z16', YOKOSUKA, (2200, 1800), rings=[{'at': YOKOSUKA, 'm': 320, 'label': '横須賀', 'sub': '明治の新政府へ引き継がれた'}],
   text={'kicker': '小栗の言葉どおり', 'title': '近代の造船を支えた'}, scale=500),                                                    # s156
 P('yokosuka_z16', YOKOSUKA, (2200, 1800), rings=[{'at': YOKOSUKA, 'm': 320, 'label': '石造りのドック', 'sub': '1871年完成・今も使われている'}],
   text={'kicker': '小栗の言葉どおり', 'title': '近代の造船を支えた'}),                                                              # s157
 CARD('小栗の子孫を招いて', 'お礼を述べた', kicker='東郷平八郎', bg=BG_YOKO),                                                        # s158
 CARD('勝てたのは', '小栗が製鉄所を造ってくれたおかげ', bg=BG_YOKO, fs=64),                                                          # s159
 CARD('埋めた小判ではなく', '未来へ渡した工場', gold=1, bg=BG_YOKO),                                                               # s160
 MY(status=['solved', 'solved', 'open'], marks=['運べない', '金がない', '？'], reveal=1, focus=1, bg=BG_YOKO),                      # s161
 MY(status=['solved', 'solved', 'open'], marks=['運べない', '金がない', '？'], bg=BG_YOKO),                                        # s162
 ROWS('両から円へ（1871年）', [('1両', '1円と定められた')], bg=BG_EDO),                                                             # s163
 ROWS('両から円へ（1871年）', [('1両', '1円と定められた'), ('360万両', '360万円にあたる額', 1)], bg=BG_EDO),                           # s164
 COMMENT('次に確かめるテーマは、コメントから決めています', bg=BG_AKAGI),                                                              # s165
 COMMENT('埋蔵金でも、ほかの日本史の謎でも', bg=BG_AKAGI),                                                                         # s166
 COMMENT('確かめてほしい謎を教えてください', bg=BG_AKAGI),                                                                         # s167
 CARD('記録と数字で', '1つずつ確かめています', kicker='このチャンネルでは', bg=BG_AKAGI),                                              # s168
 CARD('次の検証を見逃さないよう', 'チャンネル登録を', bg=BG_AKAGI),                                                                  # s169

 # ── 物差し3 記録があるか ──
 CH('3', '記録があるか', '場所を指す記録があるか', bg=BG_NIKKO),                                                                     # s170
 BD(status=['open', 'open', 'open', 'out', 'open'], bg=BG_NIKKO),                                                               # s171
 BD(status=['open', 'open', 'open', 'out', 'open'], focus=1, bg=BG_NIKKO),                                                      # s172
 P('nikko_z17', NIKKO, (900, 760), rings=[{'at': NIKKO, 'm': 150, 'label': '東照宮', 'sub': '1617年 徳川家康をまつる'}],
   text={'kicker': '日光', 'title': '家康が眠る'}, scale=200),                                                                     # s173
 P('nikko_z17', NIKKO, (900, 760), rings=[{'at': NIKKO, 'm': 150, 'label': '東照宮'}],
   text={'kicker': '託すなら日光しかない', 'title': 'そこから生まれた説'}),                                                            # s174
 P('nikko_z17', NIKKO, (1200, 1000), rings=[{'at': NIKKO, 'm': 150, 'label': '東照宮'}],
   text={'kicker': '1868年の春', 'title': '幕府の兵が立てこもる'}, scale=300),                                                       # s175
 CARD('東照宮を戦火から守るため', '退くよう説いた', kicker='新政府の軍 板垣退助', bg=BG_NIKKO, fs=64),                                   # s176
 CARD('兵たちは日光を離れ', '東照宮は戦火を免れた', bg=BG_NIKKO),                                                                    # s177
 CARD('御用金があったなら', 'そう簡単に手放さなかったはず', bg=BG_NIKKO),                                                             # s178
 CARD('日光へ運ばれたことを示す', '記録は見つかっていない', bg=BG_NIKKO),                                                            # s179
 CARD('場所の意味から', 'あとで組み立てられた説', bg=BG_NIKKO),                                                                     # s180
 BD(status=['open', 'out', 'open', 'out', 'open'], reveal=1, focus=1, note='5つのうち 2つが消えた', bg=BG_NIKKO),                   # s181
 BD(status=['open', 'out', 'open', 'out', 'open'], note='5つのうち 2つが消えた', bg=BG_NIKKO),                                     # s182
 BD(status=['open', 'out', 'open', 'out', 'open'], focus=2, bg=BG_GONDA),                                                       # s183
 P('gonda_z16', GONDA, (2600, 2200), rings=[{'at': GONDA, 'm': 420, 'label': '権田村', 'sub': '今の高崎市倉渕町'}],
   text={'kicker': '小栗が移り住んだ村', 'title': '権田村'}, scale=500),                                                            # s184
 P('gonda_z16', GONDA, (2600, 2200), rings=[{'at': GONDA, 'm': 420, 'label': '権田村'}],
   text={'kicker': '小栗が運んだ荷物', 'title': '新政府が調べた'}),                                                                  # s185
 CARD('大量の小判が出てきた', 'という記録はない', bg=BG_GONDA),                                                                     # s186
 CARD('村で静かに暮らすつもりで', '家を建てる準備を始めていた', bg=BG_GONDA, fs=64),                                                   # s187
 CARD('隠した人物が', '人目のある村に住むとは考えにくい', bg=BG_GONDA, fs=64),                                                        # s188
 BD(status=['open', 'out', 'out', 'out', 'open'], reveal=2, focus=2, note='5つのうち 3つが消えた', bg=BG_GONDA),                    # s189
 BD(status=['open', 'out', 'out', 'out', 'open'], note='5つのうち 3つが消えた', bg=BG_GONDA),                                      # s190
 BD(status=['left', 'out', 'out', 'out', 'left'], note='残ったのは2つ', bg=BG_AKAGI),                                             # s191
 COMMENT('最初の予想は、まだ残っていますか', bg=BG_AKAGI),                                                                         # s192
 P('akagi_z15', AKAGI, (5000, 4000), rings=[{'at': AKAGI, 'm': 900, 'label': '赤城山'}],
   text={'kicker': '調べ直した', 'title': '言い伝えの出どころ'}, scale=1000),                                                        # s193
 ROWS('赤城山説の出どころ', [('始まり', '初代が義理の父から聞いた話')], bg=BG_AKAGI_P),                                                # s194
 ROWS('赤城山説の出どころ', [('始まり', '初代が義理の父から聞いた話'), ('その父', '幕府の役人だったという'),
                     ('裏付ける幕府の記録', '見つかっていない', 1)], bg=BG_AKAGI_P),                                                # s195
 ROWS('赤城山説の出どころ', [('始まり', '初代が義理の父から聞いた話'), ('その父', '幕府の役人だったという'),
                     ('裏付ける幕府の記録', '見つかっていない', 1), ('手がかり', '銅板の暗号・黄金の家康像')], bg=BG_AKAGI_P),           # s196
 ROWS('赤城山説の出どころ', [('始まり', '初代が義理の父から聞いた話'), ('その父', '幕府の役人だったという'),
                     ('裏付ける幕府の記録', '見つかっていない', 1), ('手がかり', '銅板の暗号・黄金の家康像'),
                     ('1990年代', '大学の研究者が資料を調べた')], bg=BG_AKAGI_P, gap=112),                                        # s197
 ROWS('赤城山説の出どころ', [('始まり', '初代が義理の父から聞いた話'), ('その父', '幕府の役人だったという'),
                     ('裏付ける幕府の記録', '見つかっていない', 1), ('手がかり', '銅板の暗号・黄金の家康像'),
                     ('1990年代', '大学の研究者が資料を調べた'), ('黄金の家康像', '金ではなかったのでは', 1)],
      bg=BG_AKAGI_P, gap=98),                                                                                                    # s198
 CARD('すべて言い伝えか', '出どころの分からない品', kicker='赤城山を指す記録は', bg=BG_AKAGI_P),                                         # s199

 # ── 3つの物差しの答え ──
 MY(status=['solved', 'solved', 'solved'], marks=['運べない', '金がない', '記録がない'], reveal=2, bg=BG_AKAGI),                     # s200
 MY(status=['solved', 'solved', 'solved'], marks=['運べない', '金がない', '記録がない'], focus=0, bg=BG_AKAGI),                      # s201
 MY(status=['solved', 'solved', 'solved'], marks=['運べない', '金がない', '記録がない'], focus=1, bg=BG_AKAGI),                      # s202
 MY(status=['solved', 'solved', 'solved'], marks=['運べない', '金がない', '記録がない'], focus=2, bg=BG_AKAGI),                      # s203
 BD(status=['out', 'out', 'out', 'out', 'left'], reveal=0, focus=0, note='5つのうち 4つが消えた', bg=BG_AKAGI),                     # s204
 CARD('どの物差しに当てても', '筋書きは成り立たなかった', bg=BG_AKAGI, fs=64),                                                        # s205
 BD(status=['out', 'out', 'out', 'out', 'left'], focus=4, note='残ったのは「最初からなかった」', bg=BG_AKAGI),                       # s206

 # ── 弱点 ──
 CARD('この結論には', 'はっきりした弱点がある', bg=BG_AKAGI),                                                                       # s207
 THEO('この結論の弱点', [{'k': '弱点 1', 'name': '記録の\n空白'}, {'k': '弱点 2', 'name': '小さな\n御用金'},
                   {'k': '弱点 3', 'name': '大判や\n延べ棒'}], bg=BG_AKAGI),                                                     # s208
 ROWS('弱点1　記録の空白', [('幕末の幕府のお金の記録', '空白が多い', 1)], bg=BG_AKAGI),                                              # s209
 ROWS('弱点1　記録の空白', [('幕末の幕府のお金の記録', '空白が多い', 1), ('帳簿の多く', '失われ、持ち出された')], bg=BG_AKAGI),               # s210
 ROWS('弱点1　記録の空白', [('幕末の幕府のお金の記録', '空白が多い', 1), ('帳簿の多く', '失われ、持ち出された'),
                   ('1923年 関東大震災', '火事でさらに失われた')], bg=BG_AKAGI),                                                  # s211
 CARD('なかったことを', '証明することもできない', bg=BG_AKAGI),                                                                     # s212
 ROWS('弱点2　小さな御用金', [('360万両より小さければ', '隠された可能性は残る', 1)], bg=BG_AKAGI),                                      # s213
 ROWS('弱点2　小さな御用金', [('360万両より小さければ', '隠された可能性は残る', 1), ('江戸時代の小判', '工事現場や床下から見つかった例も')],
      bg=BG_AKAGI),                                                                                                            # s214
 ROWS('弱点3　大判や延べ棒', [('今回の計算は', '1枚1両の小判の場合', 1)], bg=BG_AKAGI),                                              # s215
 ROWS('弱点3　大判や延べ棒', [('今回の計算は', '1枚1両の小判の場合', 1), ('大判や延べ棒なら', '必要な馬の数は変わる')], bg=BG_AKAGI),       # s216

 # ── 結論 ──
 CARD('今ある記録から考える限り', '答えは1つ', bg=BG_AKAGI),                                                                       # s217
 CARD('そのままの形で山に眠る', '可能性は低い', kicker='360万両の御用金が', bg=BG_AKAGI),                                             # s218
 ROWS('幕府の金はどこへ行ったか', [('開国のあと', '海の向こうへ流れ出た')], bg=BG_YOKO),                                               # s219
 ROWS('幕府の金はどこへ行ったか', [('開国のあと', '海の向こうへ流れ出た'), ('最後の数年', '長州への出兵・横須賀の製鉄所'),
                        ('山に埋めた分', 'それを示す記録はない', 1)], bg=BG_YOKO),                                                 # s220
 CARD('山の中ではなく', '海の外', kicker='徳川埋蔵金はどこにあるのか', gold=1, center=True, bg=BG_YOKO),                              # s221

 # ── エピローグ ──
 CARD('なぜ160年近くも', '消えずに残ってきたのか', center=True, bg=BG_AKAGI),                                                       # s222
 CARD('何かがどこかに', '残されていてほしかった', bg=BG_AKAGI),                                                                     # s223
 CARD('260年続いた幕府が', '何も残さずに消えたとは', bg=BG_AKAGI),                                                                  # s224
 P('tsukuda_z16', TSUKUDA, (2400, 2000), rings=[{'at': TSUKUDA, 'm': 380, 'label': '水野家の発掘地', 'sub': '3代・100年以上'}],
   text={'kicker': 'その願いを', 'title': '100年以上掘り続けた'}, scale=500),                                                       # s225
 CARD('重機が土を掘り返すたび', '今度こそと身を乗り出した', bg=BG_AKAGI_P, fs=64),                                                    # s226
 CARD('小判が出たら何を買おうかと', '笑い合った夜', bg=BG_AKAGI_P, fs=64),                                                          # s227
 CARD('埋蔵金は見つからなくても', 'あの時間は確かにあった', gold=1, bg=BG_AKAGI_P),                                                   # s228
 P('tsukuda_z16', TSUKUDA, (2000, 1700), rings=[{'at': TSUKUDA, 'm': 300, 'label': 'ここに立っていた'}],
   text={'kicker': '明治の初め ある冬の朝', 'title': 'つるはしを担いだ男'}, scale=500),                                               # s229
 P('tsukuda_z16', TSUKUDA, (2000, 1700), rings=[{'at': TSUKUDA, 'm': 300, 'label': 'ここに立っていた'}],
   text={'kicker': 'その穴は', 'title': '孫の代まで続いた'}),                                                                      # s230
 CARD('小判は1枚も', '見つからなかった', bg=BG_TSUKUDA),                                                                           # s231
 CARD('その穴の深さは', '時代の終わりを惜しんだ深さ', bg=BG_TSUKUDA, fs=64),                                                         # s232
 COMMENT('まだどこかに眠っていると思いますか', bg=BG_AKAGI),                                                                       # s233
 COMMENT('それとも、最初からなかったと思いますか', bg=BG_AKAGI),                                                                   # s234
 COMMENT('ぜひコメント欄で教えてください', bg=BG_AKAGI),                                                                          # s235
 COMMENT('最初に書いていただいた予想とも比べてみてください', bg=BG_AKAGI),                                                          # s236
 CARD('記録と数字で', '1つずつ確かめていきます', kicker='次回も', bg=BG_AKAGI),                                                      # s237
 CARD('最後までご覧いただき', 'ありがとうございました', center=True, bg=BG_AKAGI),                                                   # s238
]

lines = json.load(open('lines.json', encoding='utf-8'))
if len(S) != len(lines):
    sys.exit(f'✗ {len(S)} scenes for {len(lines)} sentences — they must match one to one')

# readings VOICEVOX cannot get from the written sentence
SAY = {'s98': lambda t: t.replace('40貫', 'よんじゅっかん'),
       's148': lambda t: t.replace('600万ドル', '600まんドル')}

for s, l in zip(S, lines):
    s['id'] = l['id']
    say = SAY[l['id']](l['text']) if l['id'] in SAY else l['text']
    if say != l['text']: s['say'] = say
    if s.get('img') and s['img'] not in HAVE: sys.exit(f'✗ {l["id"]}: 素材 {s["img"]} がありません')
    for k in [k for k, v in s.items() if v is None]: s.pop(k)

# Same picture, next sentence: continue the shot (cont) instead of cutting to an identical frame
ALWAYS = {'mysteries', 'board', 'timeline', 'bars', 'doc', 'stack', 'koban', 'column', 'ratio'}
def same_picture(a, b):
    if a['layout'] != b['layout']: return False
    if a['layout'] == 'photo': return a['img'] == b['img'] and a['at'] == b['at']
    if a['layout'] == 'map': return a['view'] == b['view']
    if a['layout'] in ALWAYS: return a.get('axis') == b.get('axis') and a.get('kicker') == b.get('kicker')
    if a['layout'] in ('rows', 'calc', 'theories'): return a.get('kicker') == b.get('kicker')
    if a['layout'] == 'comment': return False
    return False
for a, b in zip(S, S[1:]):
    if same_picture(a, b):
        b['cont'] = True
        if 'bg' in a: b['bg'] = a['bg']
        elif 'bg' in b: b.pop('bg')
        if a.get('source') and not b.get('source'): b['source'] = a['source']

out = {'_about': 'One entry per sentence (same order as script.txt); generated by tools/make_scenes.py (Claude Code). Layouts: index.html L.*.',
       'title': '徳川埋蔵金はどこにあるのか', 'title_en': 'Where the Tokugawa Gold Went',
       'mysteries': MYST, 'candidates': CAND,
       'board': {'kicker': '5つの候補', 'solved': '答えが出た', 'out': '消えた', 'left': '残り'},
       'chapter_label': 'YARDSTICK',
       'credits': ['地図　Natural Earth（パブリックドメイン）をもとに作図　空中写真・陰影起伏図　出典：国土地理院（地理院タイル）',
                   '小判の重さと金の割合　慶長小判・天保小判・万延小判の計量値にもとづく（小判は実寸で作図）',
                   '数字　360万両を1枚1両として計算。馬1頭の積載は40貫（約150 kg）として計算',
                   *(['写真　' + '、'.join(sorted(WIKI_NAMES)) + '（Wikimedia Commons、パブリックドメイン・CC0）'] if WIKI_NAMES else []),
                   '音声　VOICEVOX:青山龍星',
                   '地図上の位置の一部（御金蔵・津久田原・権田村・田町の薩摩藩邸）は概略です。'],
       'scenes': S}
json.dump(out, open('scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'scenes', dict(Counter(s['layout'] for s in S)), sum(1 for s in S if s.get('cont')), 'cont')
