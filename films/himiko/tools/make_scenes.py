#!/usr/bin/env python3
"""Scene assignment for 卑弥呼の正体 (handbook 11-3 step 2), written by Claude Code in the session.
One entry per sentence of script.txt, in order → scenes.json. Layouts: index.html `L.*`.
This film's board (mysteries) is a scoreboard: candidate 4 stays 「？」 until the script names it (s177)."""
import json, os, re, sys

# places (lat, lon); 概略 where the site has no single point. Nara values agree with 箸墓古墳 from daisen-kofun.
TAIHO = [37.57, 126.98]        # 帯方郡（今のソウル付近、位置は概略）
TSUSHIMA = [34.30, 129.33]; IKI = [33.78, 129.72]; MATSURO = [33.45, 129.97]
ITO = [33.5590, 130.2070]      # 伊都国・平原遺跡（福岡県糸島市）
NAKOKU = [33.5900, 130.4000]   # 奴国（福岡平野、概略）
SHIKA = [33.6650, 130.3040]    # 志賀島（金印公園）
YOSHI = [33.3250, 130.3818]    # 吉野ヶ里遺跡
YAMATO_K = [33.1700, 130.4600] # 山門（福岡県みやま市、概略）
MAKI = [34.5398, 135.8338]     # 纒向遺跡（大型建物跡）
HASHI = [34.53926, 135.84123]  # 箸墓古墳
MIWA = [34.5330, 135.8600]     # 三輪山
OMIWA = [34.5286, 135.8527]    # 大神神社
ISO = [34.5985, 135.8520]      # 石上神宮
KAMBARA = [35.2960, 132.9050]  # 神原神社古墳（島根県雲南市、概略）
LUOYANG = [34.6200, 112.4500]  # 魏の都 洛陽
RYOTO = [41.2700, 123.1700]    # 遼東（遼陽）
KUNA = [32.6000, 130.9000]     # 狗奴国（南の国、位置は不明・模式図）
TOKAI = [35.10, 136.90]; HOKURIKU = [36.60, 136.65]; SANIN = [35.47, 133.05]; KIBI = [34.67, 133.93]

LAYER = {k: 'seamlessphoto' for k in ('makimuku_z17', 'makimuku_z15', 'miwa_z15', 'omiwa_z17', 'isonokami_z17',
                                      'shikanoshima_z16', 'hirabaru_z17', 'yamato_z15', 'hashihaka_z17', 'yoshinogari_z16')}
PHOTO = {}        # filled from SOURCES.jsonl (public domain / CC0 pictures: Wikimedia Commons, Art Institute of Chicago)
WIKI_NAMES = set() # photographers, for the closing credits
AIC_WORKS = []     # 作者「題」（年）, for the closing credits
for l in open('SOURCES.jsonl', encoding='utf-8'):
    r = json.loads(l)
    if r['source'].startswith('GSI tiles'): continue
    PHOTO[r['name'].split('/')[-1].rsplit('.', 1)[0]] = r['credit'].replace('Public domain', 'パブリックドメイン')
    if r['source'].startswith('Wikimedia'):
        WIKI_NAMES.update(n for n in re.sub(r'（.*', '', r['credit'].replace('写真：', '')).split('、') if n)
    elif r['source'].startswith('Art Institute'):
        AIC_WORKS.append(r['name'].split('/')[-1].rsplit('.', 1)[0])   # resolved to Japanese titles below
NE = '出典：Natural Earth（地図データ、パブリックドメイン）'
# the museum catalogues these in English; on screen they read in Japanese
JP_TITLE = {'mirror_deities': '神獣鏡（後漢・2〜3世紀）', 'mirror_tlv': '方格規矩鏡（後漢・1世紀ごろ）',
            'mirror_dragon': '竜文鏡（前漢）', 'susanoo': '鳥居清倍「素戔嗚尊 八岐大蛇退治」（1748年）',
            'jingu': '勝川春英「神功皇后と武内宿禰」（1780年代）', 'takenouchi': '魚屋北渓「応神天皇を抱く武内宿禰」（1830年ごろ）'}
for k, v in JP_TITLE.items():
    if k in PHOTO: PHOTO[k] = f'画像：{v}（シカゴ美術館、パブリックドメイン・CC0）'

# views of the drawn map: centre (lat, lon) and degrees of longitude across the frame
EA = {'c': [36, 122], 'w': 46}; EA2 = {'c': [36.5, 125], 'w': 34}; ROUTE = {'c': [35.2, 129.6], 'w': 14}
JP = {'c': [34.3, 133.0], 'w': 24}; JPW = {'c': [34.6, 134.5], 'w': 30}; KYU = {'c': [33.4, 130.4], 'w': 5.4}
KYU2 = {'c': [33.5, 130.3], 'w': 3.2}; NARAV = {'c': [34.55, 135.845], 'w': 0.9}; WIDE = {'c': [33, 120], 'w': 56}

def MAP(view, **kw): return {'layout': 'map', 'view': view, 'source': NE, **kw}
def P(img, at, span=(1500, 1350), **kw): return {'layout': 'photo', 'img': img, 'at': at, 'span': list(span), **kw}
def CARD(*lines, bg=None, **kw): return {'layout': 'card', 'lines': list(lines), 'bg': bg, **kw}
def CH(num, title, sub, bg=None): return {'layout': 'chapter', 'num': num, 'title': title, 'sub': sub, 'bg': bg}
def MY(status=(), marks=None, names=None, focus=None, reveal=None, kicker=None, bg=None):
    return {'layout': 'mysteries', 'status': list(status), 'marks': marks, 'names': names, 'focus': focus,
            'reveal': reveal, 'kicker': kicker, 'bg': bg}
def BARS(kicker, items, bg=None, **kw): return {'layout': 'bars', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def CALC(kicker, rows, bg=None, **kw): return {'layout': 'calc', 'kicker': kicker, 'rows': rows, 'bg': bg, **kw}
def ROWS(kicker, rows, bg=None, **kw): return {'layout': 'rows', 'kicker': kicker,
    'rows': [r if isinstance(r, dict) else {'k': r[0], 'v': r[1] if len(r) > 1 else '', 'hi': len(r) > 2} for r in rows], 'bg': bg, **kw}
def THEO(kicker, items, bg=None, **kw): return {'layout': 'theories', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def COMMENT(text, sub=None, bg=None): return {'layout': 'comment', 'text': text, 'sub': sub, 'bg': bg}
def DOTS(kicker, groups, per=1, unit='人', bg=None, **kw):
    return {'layout': 'dots', 'kicker': kicker, 'per': per, 'unit': unit, 'cols': 25, 'gap': 54, 'r': 19,
            'y0': 380, 'ly': 760, 'lgap': 430, 'groups': groups, 'bg': bg, **kw}
def DOC(doc, lines, hl, source, bg=None, fs=58): return {'layout': 'doc', 'doc': doc, 'lines': lines, 'hl': hl, 'fs': fs, 'source': source, 'bg': bg}
def B(img, at, span, a=.22): return {'img': img, 'at': at, 'span': span, 'a': a}

# backdrops (aerials of the places named; alpha kept low so the type stays readable)
BG_MAKI = B('makimuku_z15', MAKI, 2600, .22); BG_MAKI17 = B('makimuku_z17', MAKI, 900, .22)
BG_HASHI = B('hashihaka_z17', HASHI, 1000, .22); BG_YOSHI = B('yoshinogari_z16', YOSHI, 2600, .24)
BG_MIWA = B('miwa_z15', MIWA, 4200, .22); BG_OMIWA = B('omiwa_z17', OMIWA, 900, .22)
BG_ISO = B('isonokami_z17', ISO, 900, .22); BG_SHIKA = B('shikanoshima_z16', SHIKA, 2200, .22)
BG_HIRA = B('hirabaru_z17', ITO, 900, .22); BG_YAMATO = B('yamato_z15', YAMATO_K, 4200, .22)
BG_YP = B('yoshinogari_photo', [960, 620, 0], 1800, .26)
# pictures of the things the script is talking about (public domain / CC0, Art Institute of Chicago).
# The mirrors are Han-dynasty Chinese bronzes of the very kind 卑弥呼 was sent in 239 — her own era's object.
BG_MIR = B('mirror_deities', [800, 1040, 0], 1300, .34)    # 後漢 2〜3世紀の神獣鏡
# 卑弥呼その人の姿。同時代の絵も、著作権の切れた肖像も無いので、本作のために描き起こした
# （横顔・鏡・勾玉。顔立ちは誰も知らないため、逆光の影として描いている）
BG_HIMI = B('himiko_figure', [1200, 675, 0], 2400, .20)
BG_MIR2 = B('mirror_tlv', [886, 726, 0], 1350, .26)        # 後漢の方格規矩鏡
BG_MIR3 = B('mirror_dragon', [408, 425, 0], 850, .26)      # 前漢の鏡
BG_SUSA = B('susanoo', [417, 884, 0], 950, .26)            # 素戔嗚尊（天照大神の弟）
BG_JINGU = B('jingu', [844, 576, 0], 1700, .26)            # 神功皇后と武内宿禰
BG_TAKE = B('takenouchi', [840, 963, 0], 1750, .24)        # 武内宿禰

# the spine: four candidates, scored out of 20. Candidate 4 is withheld until the script names it.
CAND = ['天照大神', '神功皇后', '九州の女王', '？']
CAND_ALL = ['天照大神', '神功皇后', '九州の女王', '倭迹迹日百襲姫']
OPEN4 = ['open'] * 4
def MARKS(*v): return [f'{x}点' if isinstance(x, int) else x for x in v]

# the four measures, 5 points each
CRIT = {'time': '時代が合うか', 'place': '女性が国の中心か', 'rite': '祭り・まじない', 'rec': '記録の裏付け'}
def SCORE(kicker, got, note=None, bg=None):
    items = [{'label': CRIT[k], 'value': v, 'text': f'{v}点', 'hi': v >= 4} for k, v in got]
    return BARS(kicker, items, bg=bg, max=5, gap=140, note=note)

# the route of the 魏志倭人伝 (schematic), and the sea it runs into if the distances are read literally
ROUTE_PTS = [TAIHO, [35.6, 126.6], [34.9, 129.0], TSUSHIMA, IKI, MATSURO, [33.50, 130.10], NAKOKU]
RT = lambda **kw: [{'pts': ROUTE_PTS, 'col': 'gold', 'wd': 5, 'dashed': True, **kw}]
SEA = [{'pts': [NAKOKU, [32.2, 130.9], [30.0, 131.4], [28.0, 131.8]], 'col': 'red', 'wd': 5, 'dashed': True,
        'label': '海の上に出てしまう', 'lat': [29.0, 133.4]}]
WEI = [{'pts': [NAKOKU, [33.9, 129.2], [35.0, 126.6], TAIHO, [38.6, 122.2], [36.8, 117.4], LUOYANG], 'col': 'teal',
        'wd': 5, 'dashed': True, 'label': '239年 魏へ', 'lat': [38.2, 118.6]}]
SITES_RT = [{'at': TSUSHIMA, 'label': '対馬', 'side': -1, 'col': 'gold', 'r': 10},
            {'at': IKI, 'label': '壱岐', 'side': 1, 'col': 'gold', 'r': 10},
            {'at': NAKOKU, 'label': '九州に上陸', 'side': 1, 'col': 'gold', 'r': 10}]
TOKI = [{'pts': [TOKAI, [34.9, 136.2], MAKI], 'col': 'teal', 'wd': 4, 'dashed': True},
        {'pts': [HOKURIKU, [35.6, 136.0], MAKI], 'col': 'teal', 'wd': 4, 'dashed': True},
        {'pts': [SANIN, [34.9, 134.5], MAKI], 'col': 'teal', 'wd': 4, 'dashed': True},
        {'pts': [KIBI, [34.6, 134.8], MAKI], 'col': 'teal', 'wd': 4, 'dashed': True}]
TOKI_S = [{'at': TOKAI, 'label': '東海', 'side': 1, 'col': 'teal', 'r': 9}, {'at': HOKURIKU, 'label': '北陸', 'side': -1, 'col': 'teal', 'r': 9},
          {'at': SANIN, 'label': '山陰', 'side': -1, 'col': 'teal', 'r': 9}, {'at': KIBI, 'label': '吉備', 'side': 1, 'col': 'teal', 'r': 9},
          {'at': MAKI, 'label': '纒向', 'sub': '奈良県桜井市', 'side': 1, 'col': 'gold', 'r': 13}]

# timelines
TLD = lambda ev, **kw: {'layout': 'timeline', 'kicker': '卑弥呼論争の300年', 'axis': [1700, 2050], 'step': 50, 'events': ev, **kw}
TLW = lambda ev, **kw: {'layout': 'timeline', 'kicker': '倭の国のできごと', 'axis': [100, 300], 'step': 50, 'events': ev, **kw}
TLM = lambda ev, **kw: {'layout': 'timeline', 'kicker': '纒向で測られた年代', 'axis': [100, 300], 'step': 50, 'events': ev, **kw}

S = [
    # ───── 導入（s01–s13）
    P('himiko_figure', [1200, 675, 0], (2400, 2180),
      text={'kicker': '日本で最も有名な古代の女王', 'title': '卑弥呼', 'ts': 150,
            'caption': 'その名は、日本の歴史書に1度も出てこない'}),
    ROWS('卑弥呼という名前', [('日本書紀　720年', '記載なし', True), ('古事記　712年', '記載なし', True)], bg=BG_HIMI),
    THEO('卑弥呼を伝えているのは', [{'k': '日本の記録', 'name': '日本書紀・古事記', 'sub': '名前が出てこない'},
                                    {'k': '中国の記録', 'name': '魏志倭人伝', 'sub': 'すべてここから'}], hi=[1], bg=BG_HIMI),
    CARD('中国の記録の「倭の女王」は', '日本の側では誰だったのか', center=True, bg=BG_HIMI),
    TLD([{'y': 1716, 'label': '江戸時代に始まる', 'side': 1}, {'y': 2026, 'label': '今も決着せず', 'side': -1, 'hi': True}],
        spans=[{'from': 1716, 'to': 2026, 'label': '300年以上', 'hi': True}]),
    THEO('記録を1行ずつ突き合わせる', [{'k': '中国', 'name': '魏志倭人伝', 'sub': '3世紀の記録'},
                                      {'k': '日本', 'name': '日本書紀', 'sub': '720年の記録'}], bg=BG_MIR),
    CARD('記録と', '最新の年代測定で', '正体を確かめる', kicker='今回の検証', bg=BG_MIR),
    MY(OPEN4, kicker='候補は4人にしぼられた', bg=BG_MIR),
    MY(OPEN4, focus=3, kicker='最後に浮かび上がった1人', bg=BG_MIR),
    COMMENT('あなたの予想は？', '動画を見る前に、コメント欄へ一言', bg=BG_MIR),
    THEO('どれだと思いますか', [{'k': '候補 1', 'name': '天照大神'}, {'k': '候補 2', 'name': '神功皇后'},
                                {'k': '？', 'name': '別の誰か'}], bg=BG_MIR),
    COMMENT('最後に答え合わせを', bg=BG_MIR),
    CARD('まずは', '確かに分かっていることから', kicker='検証のはじめに', bg=BG_YOSHI),

    # ───── 魏志倭人伝（s14–s21）
    DOC('『三国志』魏書 東夷伝 倭人条', ['倭人在帶方', '東南大海之中', '依山㠀爲國邑'], hl=[0],
        source='史料：『三国志』魏書 東夷伝 倭人条（原文・新字体）', bg=BG_MIR3),
    ROWS('魏志倭人伝とは', [('正しくは', '『三国志』魏書 東夷伝 倭人条'), ('長さ', '2000字ほど', True)], bg=BG_MIR3),
    ROWS('書いたのは', [('陳寿', '中国の役人'), ('まとめられた', '3世紀の終わりごろ', True)], bg=BG_MIR3),
    CALC('卑弥呼の時代との隔たり', [['3世紀の終わり − 卑弥呼の時代', '50年ほど', True]], bg=BG_MIR3),
    MAP(ROUTE, routes=RT(label='帯方郡から倭の国へ', lat=[36.3, 127.6]),
        places=[{'at': TAIHO, 'label': '帯方郡', 'sub': '朝鮮半島（位置は概略）', 'side': 1, 'col': 'gold', 'r': 12}],
        text={'kicker': '魏志倭人伝が書いた道のり'}),
    MAP(ROUTE, routes=RT(), places=SITES_RT, text={'kicker': '対馬と壱岐を渡って九州へ'},
        note='邪馬台国へは、さらにいくつもの国を通る'),
    MAP(JP, routes=RT() + SEA, places=[{'at': NAKOKU, 'label': '九州', 'side': -1, 'col': 'faint', 'r': 9}],
        text={'kicker': '書かれた距離と方角のとおりに進むと'}, note='九州のはるか南の海の上（模式図）'),
    THEO('ここから生まれた2つの論争', [{'k': '場所', 'name': '邪馬台国はどこか'},
                                      {'k': '人物', 'name': '卑弥呼は誰か'}], hi=[1], bg=BG_YOSHI),

    # ───── 倭国の乱と卑弥呼（s22–s31）
    CARD('もともとは', '男の王が立っていた', kicker='魏志倭人伝によると', bg=BG_YOSHI),
    TLW([{'y': 170, 'label': '国々が争う', 'sub': '70〜80年ののち', 'side': 1, 'hi': True}],
        spans=[{'from': 146, 'to': 189, 'label': '長いあいだの乱れ', 'hi': True}]),
    CARD('国々は話し合い', '1人の女性を王に立てた', bg=BG_YOSHI),
    CARD('その女性こそが', '卑弥呼', gold=1, center=True, bg=BG_YOSHI),
    TLW([{'y': 146, 'label': '後漢書が書く乱れ', 'sub': '146年〜189年の皇帝の時代', 'side': 1, 'hi': True}],
        spans=[{'from': 146, 'to': 189, 'label': '倭の国の乱れ', 'hi': True}]),
    TLW([{'y': 146, 'label': '後漢書が書く乱れ', 'sub': '146年〜189年', 'side': 1},
         {'y': 190, 'label': '卑弥呼が王に立つ', 'sub': '2世紀の終わりごろ', 'side': -1, 'hi': True}],
        spans=[{'from': 146, 'to': 189, 'label': '倭の国の乱れ'}]),
    ROWS('卑弥呼について', [('鬼道', 'まじないを行う', True), ('人々の心', 'よくつかんでいた')], bg=BG_YOSHI),
    ROWS('239年の時点で', [('年', 'すでにかなり上'), ('夫', 'いなかった')], bg=BG_YOSHI),
    CALC('在位の長さ', [['239年 − 2世紀の終わり', '40年を超える', True]], bg=BG_YOSHI),
    CARD('長い乱れを鎮めた女王は', 'それほど長く支えられていた', bg=BG_YOSHI),

    # ───── 政治と住まい（s32–s35）
    ROWS('卑弥呼の政治', [('政治を実際に助けたのは', '弟', True)], bg=BG_YOSHI),
    DOTS('王になってからは、姿を見た者がほとんどいない', [{'n': 1000, 'label': '身の回りに仕えた女性 1000人', 'col': 'gold'}],
         per=10, bg=BG_YOSHI),
    ROWS('住まい', [('宮殿と高い物見やぐら', '周りを柵で囲む'), ('守り', 'いつも兵がいた', True)], bg=BG_YP),
    ROWS('取り次ぎ', [('食事を運ぶ', 'ただ1人の男性', True), ('卑弥呼の言葉', 'その男性が取り次ぐ')], bg=BG_YP),

    # ───── 魏への使いと金印（s36–s49）
    MAP(EA, routes=WEI, places=[{'at': LUOYANG, 'label': '魏', 'sub': '中国', 'side': 1, 'col': 'teal', 'r': 12}],
        text={'kicker': '239年 魏へ使いを送る'}, note='使者の名は難升米'),
    MAP(EA, routes=WEI, places=[{'at': LUOYANG, 'label': '魏', 'side': 1, 'col': 'teal', 'r': 12},
                                {'at': RYOTO, 'label': '遼東', 'sub': '魏が手に入れた前年', 'side': -1, 'col': 'gold', 'r': 11}],
        text={'kicker': '遼東を手に入れた、すぐ翌年'}),
    CARD('海の向こうの大国の動きを', '素早くつかみ、すぐに使いを出した', bg=BG_YOSHI),
    CARD('卑弥呼の国には', '外の世界の情報を集める力があった', bg=BG_YOSHI),
    ROWS('魏の皇帝から授かったもの', [('称号', '親魏倭王', True), ('印', '金の印', True)], bg=BG_SHIKA),
    ROWS('一緒に贈られた品', [('絹の織物', ''), ('真珠・赤い顔料', ''), ('銅の鏡', '100枚', True)], bg=BG_MIR),
    CARD('この金の印は', '今もまだ見つかっていない', bg=BG_SHIKA),
    CARD('もし見つかれば', 'そこが卑弥呼の国だという', '何よりの証拠になる', bg=BG_SHIKA),
    P('shikanoshima_z16', SHIKA, (1900, 1700),
      rings=[{'at': SHIKA, 'r': 28, 'label': '志賀島', 'sub': '福岡県（金印公園のあたり）', 'side': 1}],
      text={'kicker': '1784年　農民が掘り当てた', 'caption': '「漢委奴国王」と刻まれた金の印'}),
    ROWS('2つの金の印', [('漢委奴国王', '志賀島で見つかった'), ('親魏倭王', '今もどこかの土の中', True)], bg=BG_SHIKA),
    DOTS('贈られた鏡は、どれなのか', [{'n': 100, 'label': '魏から贈られた銅の鏡 100枚', 'col': 'gold'}],
         per=1, unit='枚', bg=BG_MIR),
    BARS('三角縁神獣鏡の出土', [{'label': '日本', 'value': 500, 'text': '500枚を超える', 'hi': True},
                               {'label': '中国', 'value': 0, 'text': '1枚も出ていない', 'col': 'teal'}], max=600, bg=BG_MIR),
    ROWS('島根県の古墳から', [('1972年', '景初3年と刻まれた鏡', True)], bg=BG_MIR2),
    CALC('景初3年とは', [['景初3年', '西暦239年', True]], note='卑弥呼が魏へ使いを送った、まさにその年', bg=BG_MIR2),

    # ───── 狗奴国と壹与（s50–s56）
    MAP(JP, places=[{'at': NAKOKU, 'label': '倭の国々', 'side': -1, 'col': 'gold', 'r': 10},
                    {'at': KUNA, 'label': '狗奴国', 'sub': '南にあった国（位置は不明・模式図）', 'side': 1, 'col': 'red', 'r': 10}],
        text={'kicker': '魏との行き来と、南の国との争い'}),
    ROWS('卑弥呼の時代が終わると', [('まず男の王が立つ', '国々は従わず'), ('ふたたび', '乱れた', True)], bg=BG_YOSHI),
    CARD('選ばれたのは', '13歳の少女 壹与', kicker='卑弥呼の一族から', bg=BG_YOSHI),
    CARD('壹与が女王に立つと', '国はようやく落ち着いた', bg=BG_YOSHI),
    THEO('国が治まったのは', [{'k': '男の王', 'name': '治まらない', 'dashed': True},
                              {'k': '13歳の少女', 'name': '治まった'}], hi=[1], bg=BG_YOSHI),
    CARD('まとめていたのは', '力の強い王ではなく', '神の言葉を伝える女性', gold=2, bg=BG_YOSHI),
    COMMENT('この点が、最後に効いてきます', bg=BG_YOSHI),

    # ───── 論争史（s57–s74）
    ROWS('この有名な話', [('日本の側の記録には', '1行も出てこない', True)], bg=BG_MAKI),
    CARD('日本の歴史書は', '卑弥呼を本当に知らなかったのか', center=True, bg=BG_MAKI),
    CARD('ここから', '長い論争が始まります', bg=BG_MAKI),
    CARD('最初に取り組んだのは', '江戸時代の学者たち', bg=BG_MAKI),
    TLD([{'y': 1716, 'label': '新井白石', 'sub': '卑弥呼の国は大和', 'side': 1, 'hi': True}]),
    MAP(JPW, places=[{'at': YAMATO_K, 'label': '山門', 'sub': '九州・筑後', 'side': 1, 'col': 'gold', 'r': 12},
                     {'at': MAKI, 'label': '大和', 'side': -1, 'col': 'faint', 'r': 10}],
        text={'kicker': '白石は、のちに考えを変えた'}),
    TLD([{'y': 1716, 'label': '新井白石', 'sub': '大和、のち九州', 'side': 1},
         {'y': 1780, 'label': '本居宣長', 'sub': 'まったく別の答え', 'side': -1, 'hi': True}]),
    CARD('卑弥呼は九州の女性の首長', '大和の女帝の名を名乗って使いを送った', kicker='本居宣長の説', bg=BG_YAMATO),
    TLD([{'y': 1716, 'label': '新井白石', 'side': 1}, {'y': 1780, 'label': '本居宣長', 'side': -1},
         {'y': 1910, 'label': '2人の大学者', 'sub': '同じ年に正反対の説', 'side': 1, 'hi': True}]),
    THEO('1910年の対立', [{'k': '京都　内藤湖南', 'name': '大和'}, {'k': '東京　白鳥庫吉', 'name': '九州'}], bg=BG_MAKI),
    ROWS('それから100年以上', [('候補に挙がった人物', '10人を超える', True)], bg=BG_MAKI),
    CARD('決着がつかない理由は', 'はっきりしています', bg=BG_MAKI),
    THEO('2つの記録のすれ違い', [{'k': '中国の記録', 'name': '日本名が書かれていない'},
                                 {'k': '日本の記録', 'name': '卑弥呼の名が出てこない'}], show=[0], bg=BG_MAKI),
    THEO('2つの記録のすれ違い', [{'k': '中国の記録', 'name': '日本名が書かれていない'},
                                 {'k': '日本の記録', 'name': '卑弥呼の名が出てこない'}], show=[0, 1], bg=BG_MAKI),
    ROWS('日本書紀とは', [('作られた目的', '天皇が治める国の成り立ちを示す', True)], bg=BG_MAKI),
    ROWS('研究者の見方', [('中国から王の位を授かった女性', 'そのままは書きにくかった', True)], bg=BG_MAKI),
    CARD('2つの記録をつなぐ橋が', 'どこにもない', bg=BG_MAKI),
    CARD('今回は', 'その橋を記録の中から探していきます', bg=BG_MAKI),

    # ───── 検証のルールと物差し（s75–s83）
    CARD('確かめるにあたって', '2つのルールを決めました', bg=BG_MAKI17),
    ROWS('2つのルール', [('ルール 1', '同じ時代に近い記録ほど重く見る', True)], bg=BG_MAKI17),
    ROWS('2つのルール', [('ルール 1', '同じ時代に近い記録ほど重く見る'),
                         ('ルール 2', 'どの候補にも同じ物差しを当てる', True)], bg=BG_MAKI17),
    CARD('好きな説に甘くなれば', '答えは最初から決まってしまう', bg=BG_MAKI17),
    CARD('物差しは', '4つあります', center=True, bg=BG_MAKI17),
    ROWS('4つの物差し', [('1　時代', '卑弥呼の時代と合うか', True), ('2　立場', '女性が国の中心にいたか', True)], bg=BG_MAKI17),
    ROWS('4つの物差し', [('1　時代', '卑弥呼の時代と合うか'), ('2　立場', '女性が国の中心にいたか'),
                         ('3　祭り', '祭りやまじないを担ったか', True), ('4　記録', '記録の裏付けがあるか', True)], bg=BG_MAKI17),
    CALC('採点のしかた', [['5点 × 4つの物差し', '20点満点', True]], note='4人の候補を1人ずつ採点していきます', bg=BG_MAKI17),
    COMMENT('どの候補が勝ちそうか', '予想しながらご覧ください', bg=BG_MAKI),

    # ───── 候補1 天照大神（s84–s103）
    CH('01', '天照大神', '1人目の候補', bg=BG_MIWA),
    CARD('日本の神話で最も尊い', '太陽の女神', bg=BG_MIWA),
    ROWS('この説を唱えた代表', [('白鳥庫吉', '東京の大学者', True)], bg=BG_MIWA),
    ROWS('出発点', [('卑弥呼', '日の巫女・日の御子と読める', True)], bg=BG_MIWA),
    CARD('太陽を祭る女性なら', '天照大神とぴったり重なる', bg=BG_MIWA),
    ROWS('日本書紀が記す別の名', [('大日孁貴', '天照大神の別名', True), ('「孁」の字', '太陽に仕える女性を表すとも')], bg=BG_MIWA),
    ROWS('天照大神には', [('弟', '素戔嗚尊', True)], bg=BG_SUSA),
    ROWS('卑弥呼にも', [('政治を助ける', '弟', True)], bg=BG_SUSA),
    THEO('形まで、よく似ている', [{'k': '神話', 'name': '天照大神', 'sub': '弟　素戔嗚尊'},
                                  {'k': '魏志倭人伝', 'name': '卑弥呼', 'sub': '政治を助ける弟'}], bg=BG_SUSA),
    CARD('では、4つの物差しを', '当ててみます', bg=BG_MIWA),
    SCORE('天照大神の採点', [('rite', 5)], bg=BG_MIWA),
    SCORE('天照大神の採点', [('rite', 5), ('place', 4)], bg=BG_MIWA),
    CARD('ところが、時代が合うかで', '大きくつまずきます', bg=BG_MIWA),
    ROWS('天照大神の時代', [('神話の中の存在', '日本書紀にも年代がない', True)], bg=BG_MIWA),
    THEO('同じ物差しでは重ねられない', [{'k': '239年', 'name': '魏へ使いを送った人物'},
                                        {'k': '年代なし', 'name': '神話の神'}], hi=[1], bg=BG_MIWA),
    SCORE('天照大神の採点', [('rite', 5), ('place', 4), ('time', 1)], bg=BG_MIWA),
    SCORE('天照大神の採点', [('rite', 5), ('place', 4), ('time', 1), ('rec', 2)], bg=BG_MIWA),
    ROWS('記録の裏付け', [('名前の読みと弟の存在', '似ている'), ('それ以上の手がかり', '記録にない', True)], bg=BG_MIWA),
    MY(['solved'] + ['open'] * 3, marks=MARKS(12, '？', '？', '？'), focus=0, kicker='1人目の採点が出ました', bg=BG_MIWA),
    CARD('姿はよく似ているものの', '記録の上では時代がつながらない', bg=BG_MIWA),

    # ───── 候補2 神功皇后（s104–s139）
    CARD('日本書紀そのものは', '卑弥呼を誰だと考えていたのか', center=True, bg=BG_JINGU),
    CARD('2人目の候補が', 'その答えにあたります', bg=BG_JINGU),
    CH('02', '神功皇后', '2人目の候補', bg=BG_JINGU),
    ROWS('神功皇后', [('仲哀天皇の皇后', '夫に代わって国を治めた'), ('その長さ', '69年', True)], bg=BG_JINGU),
    ROWS('1881年', [('日本で初めて人の顔を描いたお札', '選ばれたのは神功皇后', True)], bg=BG_JINGU),
    ROWS('描いたのは', [('イタリアから招かれた版画家', '顔立ちはどこか西洋風', True)], bg=BG_JINGU),
    CARD('神功皇后の巻には', '驚くべきことが書かれています', bg=BG_TAKE),
    ROWS('日本書紀の編者は', [('中国の魏志を', 'わざわざ引用している', True)], bg=BG_JINGU),
    DOC('『日本書紀』神功皇后 三十九年条', ['魏志云、倭女王', '遣大夫難斗米等', '詣郡、求詣天子', '朝獻。'], hl=[0, 1],
        source='史料：『日本書紀』巻第九 神功皇后紀（原文・新字体）', bg=BG_JINGU, fs=54),
    ROWS('引用された条', [('39年の条', '倭の女王が魏へ使いを送る'), ('40年・43年の条', '魏との使いのやり取り', True)], bg=BG_JINGU),
    ROWS('引用された条', [('39年の条', '倭の女王が魏へ使いを送る'), ('40年・43年の条', '魏との使いのやり取り'),
                         ('66年の条', '中国の晋の記録から', True)], bg=BG_JINGU),
    ROWS('66年の条は', [('倭の女王の使い', '壹与の使いと考えられている', True)], bg=BG_JINGU),
    CARD('日本書紀の編者は', '魏志の倭の女王を', '神功皇后の時代に置いた', bg=BG_JINGU),
    CARD('720年の時点で', '朝廷は卑弥呼の記録を確かに読んでいた', bg=BG_JINGU),
    THEO('2つの歴史書', [{'k': '日本書紀　720年', 'name': '中国の記録を引用'},
                         {'k': '古事記　712年', 'name': '引用は1つもない'}], hi=[0], bg=BG_JINGU),
    CARD('外国の記録まで持ち出して', '年代を合わせようとしたのは日本書紀だけ', bg=BG_JINGU),
    CARD('これは', '強い証拠に見えます', bg=BG_TAKE),
    SCORE('神功皇后の採点', [('place', 5)], bg=BG_JINGU),
    SCORE('神功皇后の採点', [('place', 5), ('rite', 4)], bg=BG_JINGU),
    SCORE('神功皇后の採点', [('place', 5), ('rite', 4), ('rec', 3)], bg=BG_JINGU),
    CARD('ところが、ここで', '大きな問題が出てきます', bg=BG_JINGU),
    ROWS('年代を確かめると', [('神功皇后の記事', '100年以上ずれている', True)], bg=BG_JINGU),
    ROWS('日本書紀は', [('同じ時代の百済の記事も', '引用している', True)], bg=BG_JINGU),
    CALC('百済の王たちの年代', [['日本書紀 − 朝鮮の歴史書', 'およそ120年早い', True]], bg=BG_JINGU),
    P('isonokami_z17', ISO, (900, 820),
      rings=[{'at': ISO, 'r': 26, 'label': '石上神宮', 'sub': '奈良県天理市', 'side': 1}],
      text={'kicker': '分かりやすい例', 'caption': 'ここに伝わる七支刀'}),
    ROWS('七支刀', [('刀に刻まれた年', '369年', True)], bg=BG_ISO),
    ROWS('七支刀', [('刀に刻まれた年', '369年'), ('日本書紀が置く年', '252年にあたる年', True)], bg=BG_ISO),
    CALC('120年を足すと', [['252年 ＋ 120年', '372年', True], ['刀が作られた369年の', '3年後にぴたりと収まる']], bg=BG_ISO),
    CALC('120年とは', [['60年で一回りする干支', 'ちょうど2回り分', True]], bg=BG_ISO),
    ROWS('研究者の多くは', [('神功皇后の実際の時代', '4世紀の後半とみる', True)], bg=BG_JINGU),
    CARD('卑弥呼の記事を神功皇后に合わせるため', '年代を引き延ばした可能性がある', bg=BG_JINGU),
    CARD('そうだとすれば', '引用そのものが重ね合わせの跡', bg=BG_JINGU),
    SCORE('神功皇后の採点', [('place', 5), ('rite', 4), ('rec', 3), ('time', 1)], bg=BG_JINGU),
    SCORE('神功皇后 合計 13点', [('place', 5), ('rite', 4), ('rec', 3), ('time', 1)], note='20点満点', bg=BG_JINGU),
    MY(['solved', 'solved', 'open', 'open'], marks=MARKS(12, 13, '？', '？'), kicker='ここまでの採点', bg=BG_JINGU),
    MY(['solved', 'solved', 'open', 'open'], marks=MARKS(12, 13, '？', '？'), focus=1,
       kicker='日本書紀が推した候補が、わずか1点差で先頭', bg=BG_JINGU),

    # ───── 候補3 九州の女王（s140–s167）
    CARD('では、本居宣長が唱えた', '九州の女王はどうでしょうか', center=True, bg=BG_YAMATO),
    CARD('3人目の候補を', '見ていきます', bg=BG_YAMATO),
    CH('03', '九州の女王', '3人目の候補｜名前は残っていない', bg=BG_YAMATO),
    ROWS('本居宣長の説', [('卑弥呼は大和の女帝ではなく', '九州の女性の首長', True)], bg=BG_YAMATO),
    CARD('この説を支える記事が', '実は日本書紀の中にあります', bg=BG_YAMATO),
    ROWS('神功皇后が九州を進んだとき', [('筑後の山門という土地に', '田油津媛という女性の首長', True)], bg=BG_YAMATO),
    ROWS('山門', [('読み', 'やまと', True)], bg=BG_YAMATO),
    P('yamato_z15', YAMATO_K, (4200, 3700),
      rings=[{'at': YAMATO_K, 'r': 26, 'label': '山門', 'sub': '今の福岡県みやま市（概略）', 'side': 1}],
      text={'kicker': '筑後の山門'}),
    THEO('どちらも、やまと', [{'k': '筑後', 'name': '山門', 'sub': 'やまと'},
                              {'k': '魏志倭人伝', 'name': '邪馬台国', 'sub': 'やまとと読む説'}], bg=BG_YAMATO),
    P('hirabaru_z17', ITO, (900, 820),
      rings=[{'at': ITO, 'r': 26, 'label': '平原遺跡', 'sub': '福岡県糸島市', 'side': 1}],
      text={'kicker': '日本最大の銅の鏡', 'title': '直径 46.5 cm', 'ts': 76}),
    ROWS('平原遺跡', [('ここに眠るのは女性か', 'そう考える研究者もいる', True)], bg=BG_HIRA),
    CARD('九州の考古学の発見も', 'この説を後押ししてきた', bg=BG_YOSHI),
    P('yoshinogari_z16', YOSHI, (2600, 2300),
      rings=[{'at': YOSHI, 'r': 30, 'label': '吉野ヶ里遺跡', 'sub': '佐賀県', 'side': 1}],
      text={'kicker': '深い堀に囲まれた大きな集落', 'caption': '高い物見やぐらの跡'}),
    ROWS('1989年', [('大きく報じられると', '全国から見学のかたが押し寄せた', True)], bg=BG_YP),
    CARD('卑弥呼の時代のクニが', 'よみがえった', bg=BG_YP),
    THEO('魏志倭人伝の住まいと', [{'k': '記録', 'name': '宮殿・物見やぐら・柵'},
                                  {'k': '吉野ヶ里', 'name': '堀と物見やぐらの跡'}], bg=BG_YOSHI),
    MAP(KYU, places=[{'at': ITO, 'label': '糸島', 'side': -1, 'col': 'gold', 'r': 10},
                     {'at': NAKOKU, 'label': '福岡', 'side': 1, 'col': 'gold', 'r': 10},
                     {'at': YOSHI, 'label': '吉野ヶ里', 'side': 1, 'col': 'gold', 'r': 10}],
        text={'kicker': '中国に近い玄界灘の沿岸'}, note='鏡や鉄の道具も数多く見つかっている'),
    CARD('では、物差しを', '当ててみます', bg=BG_YOSHI),
    SCORE('九州の女王の採点', [('time', 4)], bg=BG_YOSHI),
    SCORE('九州の女王の採点', [('time', 4), ('place', 4)], bg=BG_YOSHI),
    ROWS('祭りやまじない', [('田油津媛がどんな祭りを担ったか', '記録にない', True)], bg=BG_YOSHI),
    SCORE('九州の女王の採点', [('time', 4), ('place', 4), ('rite', 2)], bg=BG_YOSHI),
    SCORE('九州の女王の採点', [('time', 4), ('place', 4), ('rite', 2), ('rec', 3)], bg=BG_YOSHI),
    ROWS('記録の裏付け', [('九州の遺跡', '卑弥呼の時代と重なる'), ('その中心にいた人物の名', '分からない', True)], bg=BG_YOSHI),
    SCORE('九州の女王 合計 13点', [('time', 4), ('place', 4), ('rite', 2), ('rec', 3)], note='20点満点', bg=BG_YOSHI),
    MY(['solved'] * 3 + ['open'], marks=MARKS(12, 13, 13, '？'), focus=2, kicker='神功皇后と並んで同点', bg=BG_YOSHI),
    MY(['solved'] * 3 + ['open'], marks=MARKS(12, 13, 13, '？'), kicker='ここまでの採点', bg=BG_YOSHI),
    MY(['solved'] * 3 + ['open'], marks=MARKS(12, 13, 13, '？'), kicker='3人が1点の中に', bg=BG_YOSHI),

    # ───── チャンネル・4人目へ（s168–s176）
    COMMENT('次に確かめるテーマは', 'いただいたコメントから決めています', bg=BG_MAKI),
    COMMENT('卑弥呼のことでも', 'ほかの日本史の謎でもかまいません', bg=BG_MAKI),
    COMMENT('確かめてほしい謎は？', 'ぜひコメントで教えてください', bg=BG_MAKI),
    CARD('日本の歴史の謎を', '記録と数字で1つずつ', bg=BG_MAKI),
    COMMENT('次の検証を見逃さないよう', 'チャンネル登録をしておいてください', bg=BG_MAKI),
    COMMENT('最初に書いていただいた予想を', '思い出してください', bg=BG_MAKI),
    MY(['solved'] * 3 + ['open'], marks=MARKS(12, 13, 13, '？'), focus=3,
       kicker='残る候補はあと1人　まだ1度も名前が出ていない', bg=BG_MAKI),
    CARD('では', '最後の候補です', center=True, bg=BG_MAKI),
    CARD('ここで私たちは', '物差しの1つを見直すことになりました', bg=BG_MAKI),

    # ───── 候補4 倭迹迹日百襲姫（s177–s224）
    CH('04', '倭迹迹日百襲姫', '4人目の候補', bg=BG_MAKI),
    ROWS('倭迹迹日百襲姫', [('日本書紀に登場する', '孝霊天皇の皇女', True)], bg=BG_MAKI),
    ROWS('この説を唱えたのは', [('1924年', '笠井新也という研究者', True)], bg=BG_MAKI),
    CARD('名前を聞いても', 'ほとんどのかたがご存じない', bg=BG_MAKI),
    ROWS('日本書紀によると', [('活躍したのは', '崇神天皇の時代', True)], bg=BG_MAKI),
    ROWS('崇神天皇', [('呼び名の意味', '初めて国を治めた天皇', True)], bg=BG_MAKI),
    CARD('ある日、道ばたで', '少女が不思議な歌を歌っていた', bg=BG_MAKI17),
    ROWS('百襲姫は', [('歌の意味を読み解き', '皇族が都を攻めようとしていると見抜いた', True)], bg=BG_MAKI17),
    ROWS('崇神天皇の時代', [('はやり病が広がり', '国が大きく乱れた', True)], bg=BG_MAKI17),
    CARD('このとき神が乗り移ったのが', '百襲姫', bg=BG_MAKI17),
    P('miwa_z15', MIWA, (4200, 3700),
      rings=[{'at': MIWA, 'r': 30, 'label': '三輪山', 'sub': '奈良県桜井市', 'side': -1}],
      text={'kicker': '百襲姫の口を借りた神は告げた', 'caption': '三輪山の大物主神を祭れば、国は治まる'}),
    P('omiwa_z17', OMIWA, (900, 820),
      rings=[{'at': OMIWA, 'r': 26, 'label': '大神神社', 'sub': '大物主神を祭る', 'side': 1}],
      text={'kicker': '天皇がそのとおりに祭ると', 'caption': 'はやり病はおさまり、国は落ち着いた'}),
    ROWS('さらに百襲姫は', [('大物主神の', '妻になったと書かれている', True)], bg=BG_OMIWA),
    CARD('神のお告げを受けて神と結ばれた', 'まさに祭りとまじないの中心にいた女性', bg=BG_OMIWA),
    SCORE('倭迹迹日百襲姫の採点', [('rite', 5)], bg=BG_OMIWA),
    CARD('ところが、女性が国の中心にいたかで', 'つまずくように見えます', bg=BG_MAKI),
    ROWS('日本書紀では', [('国を治めていたのは', '崇神天皇'), ('百襲姫は', '女王ではない', True)], bg=BG_MAKI),
    CARD('ここで私たちは', '魏志倭人伝をもう1度読み直しました', bg=BG_YOSHI),
    ROWS('魏志倭人伝には', [('政治を助けていたのは', '卑弥呼の弟', True)], bg=BG_YOSHI),
    ROWS('魏志倭人伝には', [('政治を助けていたのは', '卑弥呼の弟'), ('王になってから', 'ほとんど人前に姿を見せない', True)], bg=BG_YOSHI),
    ROWS('卑弥呼の次', [('男の王', '国が治まらない'), ('13歳の少女', '治まった', True)], bg=BG_YOSHI),
    CARD('まとめていたのは王の力ではなく', '神の言葉を伝える女性の存在だった', bg=BG_YOSHI),
    THEO('もう1つの読み方', [{'k': '実際に国を動かす', 'name': '男性'},
                             {'k': '奥で神の言葉を伝える', 'name': '卑弥呼'}], hi=[1], bg=BG_YOSHI),
    CARD('女王という呼び名は', '使いを迎えた中国の側からの', '見方だったのかもしれない', bg=BG_YOSHI),
    THEO('ぴたりと重なる', [{'k': '魏志倭人伝', 'name': '奥で神の言葉を', 'sub': '伝える'},
                            {'k': '日本書紀', 'name': '天皇のそばで', 'sub': '神の言葉を伝える'}], hi=[0, 1], bg=BG_MAKI),
    SCORE('倭迹迹日百襲姫の採点', [('rite', 5), ('place', 4)], bg=BG_MAKI),
    CARD('次に', '時代が合うかです', bg=BG_MAKI),
    ROWS('崇神天皇の時代', [('多くの研究者がみる年代', '3世紀の後半から4世紀の初めごろ', True)], bg=BG_MAKI),
    P('makimuku_z15', MAKI, (2600, 2300),
      rings=[{'at': MAKI, 'r': 30, 'label': '纒向遺跡', 'sub': '奈良県桜井市', 'side': 1}],
      text={'kicker': '百襲姫の名前と結びついた場所'}),
    P('makimuku_z15', MAKI, (2600, 2300),
      rings=[{'at': MAKI, 'r': 30, 'label': '纒向遺跡', 'sub': '東西2キロ・南北1.5キロ', 'side': 1}],
      text={'kicker': '3世紀の大きな都の跡', 'caption': '東西2キロ、南北1.5キロ'}),
    MAP(JPW, routes=TOKI, places=TOKI_S, text={'kicker': 'よその土地で作られた土器が集まる'}),
    CARD('各地から人が集まる', '当時の列島の中心だったと考えられている', bg=BG_MAKI),
    P('makimuku_z17', MAKI, (900, 820),
      rings=[{'at': MAKI, 'r': 26, 'label': '大型建物跡', 'sub': '2009年に見つかった', 'side': 1}],
      text={'kicker': '3世紀前半の大きな建物の跡'}),
    ROWS('大型建物', [('南北', '19メートルあまり'), ('東西', '12メートルあまり'),
                     ('当時としては', '飛び抜けた大きさ', True)], bg=BG_MAKI17),
    ROWS('その近くの穴から', [('桃の種', '2700個を超える', True)], bg=BG_MAKI17),
    ROWS('桃とは', [('古代の中国で', '悪いものを払う特別な果物', True)], bg=BG_MAKI17),
    ROWS('2018年', [('名古屋大学などのチーム', '12個の種の年代を測定', True)], bg=BG_MAKI17),
    TLM([], spans=[{'from': 135, 'to': 230, 'label': '桃が実ったのは 西暦135〜230年', 'hi': True}]),
    TLM([{'y': 190, 'label': '卑弥呼が王に立つ', 'sub': '2世紀の終わりごろ', 'side': -1, 'hi': True}],
        spans=[{'from': 135, 'to': 230, 'label': '桃が実った年代', 'hi': True}]),
    CARD('纒向では、桃を大量に使う祭りが', 'まさに卑弥呼の時代に行われていた', bg=BG_MAKI17),
    P('hashihaka_z17', HASHI, (1000, 900),
      rings=[{'at': HASHI, 'r': 30, 'label': '箸墓古墳', 'sub': '宮内庁が百襲姫の古墳として管理', 'side': 1}],
      text={'kicker': '長さ280メートルの前方後円墳'}),
    ROWS('日本書紀が伝える', [('昼は', '人が造り'), ('夜は', '神が造った', True)], bg=BG_HASHI),
    TLM([{'y': 190, 'label': '卑弥呼が王に立つ', 'side': -1},
         {'y': 250, 'label': '箸墓古墳ができる', 'sub': '3世紀の中ごろ（2009年 国立歴史民俗博物館）', 'side': 1, 'hi': True}],
        spans=[{'from': 135, 'to': 230, 'label': '桃が実った年代'}]),
    CARD('卑弥呼の時代の終わりと', 'ほぼ重なる年代', bg=BG_HASHI),
    SCORE('倭迹迹日百襲姫の採点', [('rite', 5), ('place', 4), ('time', 4)], bg=BG_MAKI),
    SCORE('倭迹迹日百襲姫の採点', [('rite', 5), ('place', 4), ('time', 4), ('rec', 2)],
          note='日本書紀の記事と纒向の発掘を直接つなぐ文字がない', bg=BG_MAKI),
    SCORE('倭迹迹日百襲姫 合計 15点', [('rite', 5), ('place', 4), ('time', 4), ('rec', 2)], note='20点満点', bg=BG_MAKI),
    MY(['solved'] * 4, marks=MARKS(12, 13, 13, 15), names=CAND_ALL, focus=3,
       kicker='最後に登場した候補が、2点の差で1位', bg=BG_MAKI),

    # ───── まとめ・弱点・結論（s225–s254）
    BARS('最終的な採点', [{'label': '倭迹迹日百襲姫', 'value': 15, 'text': '15点', 'hi': True},
                          {'label': '神功皇后', 'value': 13, 'text': '13点', 'col': 'teal'},
                          {'label': '九州の女王', 'value': 13, 'text': '13点', 'col': 'teal'},
                          {'label': '天照大神', 'value': 12, 'text': '12点'}], max=20, gap=130, bg=BG_MAKI),
    BARS('最終的な採点', [{'label': '倭迹迹日百襲姫', 'value': 15, 'text': '15点', 'hi': True},
                          {'label': '神功皇后', 'value': 13, 'text': '13点', 'col': 'teal'},
                          {'label': '九州の女王', 'value': 13, 'text': '13点', 'col': 'teal'},
                          {'label': '天照大神', 'value': 12, 'text': '12点'}], max=20, gap=130,
         note='20点満点', bg=BG_MAKI),
    CARD('ただし、この結果には', 'はっきりした弱点があります', bg=BG_MAKI),
    CARD('3つ', '挙げておきます', center=True, bg=BG_MAKI),
    ROWS('この結論の弱いところ', [('弱点 1', '崇神天皇の時代そのものがはっきりしない', True)], bg=BG_MAKI),
    CARD('研究者によって', '数十年の幅で年代が違ってくる', bg=BG_MAKI),
    ROWS('この結論の弱いところ', [('弱点 1', '崇神天皇の時代がはっきりしない'),
                                 ('弱点 2', '纒向の年代は、纒向という場所の年代', True)], bg=BG_MAKI17),
    CARD('そこに卑弥呼が住んでいたという', '証拠では、まだありません', bg=BG_MAKI17),
    ROWS('纒向の大きな建物から', [('誰が住んだのかを示す文字', '1つも出ていない', True)], bg=BG_MAKI17),
    ROWS('この時代の列島', [('文字で記録を残す習慣', 'まだ広まっていなかった', True)], bg=BG_MAKI17),
    ROWS('この結論の弱いところ', [('弱点 1', '崇神天皇の時代がはっきりしない'),
                                 ('弱点 2', '纒向の年代は、纒向という場所の年代'),
                                 ('弱点 3', '九州の説が否定されたわけではない', True)], bg=BG_YOSHI),
    BARS('九州との差', [{'label': '倭迹迹日百襲姫', 'value': 15, 'text': '15点', 'hi': True},
                        {'label': '九州の女王', 'value': 13, 'text': '13点', 'col': 'teal'}], max=20,
         note='わずか2点の差', bg=BG_YOSHI),
    P('shikanoshima_z16', SHIKA, (1900, 1700),
      rings=[{'at': SHIKA, 'r': 28, 'label': '金の印', 'sub': '親魏倭王の印は、まだ土の中', 'side': 1}],
      text={'kicker': 'もし九州のどこかで見つかれば', 'caption': '順位は一夜で入れ替わる'}),
    CARD('卑弥呼の正体は', '今も開かれたままの問い', bg=BG_SHIKA),
    CARD('それでも', '今ある記録から考える限り', '答えは1つです', bg=BG_MIWA),
    CARD('卑弥呼に最も近いのは', '倭迹迹日百襲姫', gold=1, kicker='大和の三輪山のふもとで神の言葉を伝えた女性', bg=BG_MIWA),
    P('miwa_z15', MIWA, (4200, 3700),
      rings=[{'at': MIWA, 'r': 30, 'label': '三輪山', 'sub': '1800年ほど前の大和の春', 'side': -1}],
      text={'kicker': 'ふもとには桃の花の甘い香り'}),
    P('makimuku_z17', MAKI, (900, 820),
      rings=[{'at': MAKI, 'r': 26, 'label': '奥の建物', 'side': 1}],
      text={'kicker': '1人の女性が誰にも姿を見せずに', 'caption': '神の言葉を聞いていたのかもしれない'}),
    MAP(EA, routes=WEI, places=[{'at': LUOYANG, 'label': '魏', 'side': 1, 'col': 'teal', 'r': 12},
                                {'at': MAKI, 'label': '大和', 'side': -1, 'col': 'gold', 'r': 11}],
        text={'kicker': 'その言葉を受けた弟が、遠い海の向こうへ'}),
    THEO('ここで初めて', [{'k': '中国の記録', 'name': '倭の女王'},
                          {'k': '日本の記録', 'name': '倭迹迹日百襲姫'}], hi=[0, 1], bg=BG_MAKI),
    ROWS('720年', [('日本書紀をまとめた人々も', '卑弥呼が誰なのかを知りたがっていた', True)], bg=BG_MAKI),
    CARD('だからこそ', '中国の記録をわざわざ引き写した', bg=BG_MAKI),
    CARD('1300年前の人々が抱いた問いを', '私たちは今も同じように抱いている', bg=BG_MAKI),
    CARD('そして桃の種1つから', 'その答えに少しずつ近づいている', bg=BG_MAKI17),
    COMMENT('大和の姫だったのか', bg=BG_MAKI),
    COMMENT('それとも九州の女王か', bg=BG_YOSHI),
    COMMENT('ぜひコメント欄へ', bg=BG_MAKI),
    COMMENT('最初に書いた予想とも', '比べてみてください', bg=BG_MAKI),
    CARD('次回は', '奈良の都の大仏は', 'どうやって造られたのか', kicker='卑弥呼の時代から500年後', bg=BG_HASHI),
    CARD('最後までご覧いただき', 'ありがとうございました', center=True, bg=BG_MIWA),
]

# readings VOICEVOX would otherwise get wrong (the subtitle keeps the script's own wording)
SAY = {
    's06': lambda t: t.replace('1行ずつ', 'いちぎょうずつ'),
    's89': lambda t: t.replace('この孁という字', 'この、れい、という字'),
    's132': lambda t: t.replace('2回り分', 'ふたまわりぶん'),
    's146': lambda t: 'さんもんは、やまと、と読みます。',
    's149': lambda t: t.replace('46.5センチ', 'よんじゅうろくてんごセンチ'),
}
ASR = {}

lines = json.load(open('lines.json', encoding='utf-8')) if os.path.exists('lines.json') else []
if lines and len(lines) != len(S):
    sys.exit(f'✗ {len(S)} scenes for {len(lines)} sentences')

def credit(imgs):
    g = [i for i in imgs if i in LAYER]; ph = [PHOTO[i] for i in imgs if i in PHOTO]
    return '・'.join((['出典：国土地理院（空中写真）'] if g else []) + ph)
for s, l in zip(S, lines):
    for k in [k for k, v in s.items() if v is None]: s.pop(k)
    imgs = [i for i in [s.get('img')] + ([s['bg']['img']] if s.get('bg') else []) if i]
    if imgs:
        c = credit(imgs); keep = s.get('source', '')
        s['source'] = (keep + '・' + c) if keep and not keep.startswith('出典：国土地理院') else c
    if l['id'] in SAY: s['say'] = SAY[l['id']](l['text'])
    if l['id'] in ASR: s['asr'] = ASR[l['id']]
# Same picture, next sentence: continue the shot (cont) instead of cutting to an identical frame
ALWAYS = {'mysteries', 'timeline', 'bars', 'doc'}
def same_picture(a, b):
    if a['layout'] != b['layout']: return False
    if a['layout'] == 'photo': return a['img'] == b['img']
    if a['layout'] == 'map': return a['view'] == b['view']
    if a['layout'] in ALWAYS: return a.get('axis') == b.get('axis') and a.get('doc') == b.get('doc')
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
       'title': '卑弥呼の正体', 'title_en': "Who Was Himiko?", 'mysteries': CAND,
       'board': {'kicker': '4人の候補', 'solved': '採点ずみ'}, 'chapter_label': 'CANDIDATE',
       'credits': ['地図　Natural Earth（パブリックドメイン）をもとに作図　空中写真　出典：国土地理院（地理院タイル）',
                   '史料　『三国志』魏書 東夷伝 倭人条 ／『日本書紀』巻第九 神功皇后紀（原文・新字体）',
                   '年代　春成秀爾ほか（2011）国立歴史民俗博物館研究報告 163 ／ 中塚武ほか（2018）纒向遺跡出土桃核の年代測定',
                   *(['写真　' + '、'.join(sorted({n for n in WIKI_NAMES})) + '（Wikimedia Commons、パブリックドメイン・CC0）'] if WIKI_NAMES else []),
                   *(['画像　' + ' ／ '.join(JP_TITLE.get(k, k) for k in AIC_WORKS) + '（シカゴ美術館、パブリックドメイン・CC0）'] if AIC_WORKS else []),
                   '音声　VOICEVOX:青山龍星',
                   '地図上の経路・範囲は模式図、遺跡の位置の一部は概略です。'],
       'scenes': S}
json.dump(out, open('scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(S), 'scenes', dict(Counter(s['layout'] for s in S)), sum(1 for s in S if s.get('cont')), 'cont')
