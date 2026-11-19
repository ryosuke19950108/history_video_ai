#!/usr/bin/env python3
"""Scene assignment for 奈良の大仏はどうやって造られたのか (handbook 11-3 step 2), written by Claude Code in the session.
One entry per sentence of script.txt, in order → scenes.json. Layouts: index.html `L.*`.
This film's board (mysteries) is the list of four questions; each is marked 解けた / 半分 as the script settles it.
The casting diagram (`cast`) is this film's own layout: the mould, and the earth mound that rose with every pour."""
import json, os, re, sys

# places (lat, lon); 概略 where the script itself says「あたり」
NARA = [34.68895, 135.83965]      # 東大寺 大仏殿
SHOSOIN = [34.69181, 135.83680]   # 正倉院
HEIJO = [34.69167, 135.79472]     # 平城宮跡 大極殿
KUNI = [34.74700, 135.84000]      # 恭仁京（京都府木津川市、概略）
NANIWA = [34.68300, 135.52000]    # 難波宮（大阪市中央区、概略）
SHIGARAKI = [34.92166, 136.08256] # 紫香楽宮跡
CHISHIKI = [34.58100, 135.63000]  # 知識寺跡（大阪府柏原市太平寺、概略）
NAGANOBORI = [34.24784, 131.33588]# 長登銅山跡（山口県美祢市）
NIU = [34.47350, 136.49629]       # 丹生（三重県多気町）
WAKUYA = [38.54765, 141.13954]    # 涌谷町（宮城県、概略）
KAMAKURA = [35.31698, 139.53638]  # 高徳院（鎌倉大仏）
LUOYANG = [34.62000, 112.45000]   # 唐の都 洛陽
LONGMEN = [34.55700, 112.47100]   # 龍門石窟

LAYER = {k: 'seamlessphoto' for k in ('todaiji_z17', 'todaiji_z15', 'heijo_z15', 'shigaraki_z16', 'naganobori_z16',
                                      'wakuya_z15', 'chishikiji_z16', 'niu_z15', 'kamakura_z17', 'shosoin_z18')}
PHOTO, WIKI_NAMES = {}, set()
for l in open('SOURCES.jsonl', encoding='utf-8'):
    r = json.loads(l)
    if r['source'].startswith('GSI tiles'): continue
    PHOTO[r['name'].split('/')[-1].rsplit('.', 1)[0]] = r['credit'].replace('Public domain', 'パブリックドメイン')
    if r['source'].startswith('Wikimedia'):
        WIKI_NAMES.add(re.sub(r'（.*', '', r['credit'].replace('写真：', '')).strip())
HAVE = set(PHOTO) | set(LAYER)
NE = '出典：Natural Earth（地図データ、パブリックドメイン）'

# views of the drawn map: centre (lat, lon) and degrees of longitude across the frame
EA = {'c': [34.5, 123.0], 'w': 44}; JP = {'c': [35.2, 136.0], 'w': 22}
JPW = {'c': [34.6, 133.6], 'w': 13}; JPNE = {'c': [36.6, 138.5], 'w': 15}
KINKI = {'c': [34.78, 135.80], 'w': 3.0}; KINKI2 = {'c': [34.70, 135.78], 'w': 2.0}

def MAP(view, **kw): return {'layout': 'map', 'view': view, 'source': NE, **kw}
def P(img, at, span=(1500, 1350), **kw): return {'layout': 'photo', 'img': img, 'at': at, 'span': list(span), **kw}
def CARD(*lines, bg=None, **kw): return {'layout': 'card', 'lines': list(lines), 'bg': bg, **kw}
def CH(num, title, sub, bg=None): return {'layout': 'chapter', 'num': num, 'title': title, 'sub': sub, 'bg': bg}
def MY(status=(), marks=None, focus=None, reveal=None, kicker=None, bg=None):
    return {'layout': 'mysteries', 'status': list(status), 'marks': marks, 'focus': focus,
            'reveal': reveal, 'kicker': kicker, 'bg': bg}
def BARS(kicker, items, bg=None, **kw): return {'layout': 'bars', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def CALC(kicker, rows, bg=None, **kw): return {'layout': 'calc', 'kicker': kicker, 'rows': rows, 'bg': bg, **kw}
def ROWS(kicker, rows, bg=None, **kw): return {'layout': 'rows', 'kicker': kicker,
    'rows': [r if isinstance(r, dict) else {'k': r[0], 'v': r[1] if len(r) > 1 else '', 'hi': len(r) > 2} for r in rows], 'bg': bg, **kw}
def THEO(kicker, items, bg=None, **kw): return {'layout': 'theories', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def COMMENT(text, sub=None, bg=None): return {'layout': 'comment', 'text': text, 'sub': sub, 'bg': bg}
def DOTS(kicker, groups, per=1, unit='人', bg=None, **kw):
    return {'layout': 'dots', 'kicker': kicker, 'per': per, 'unit': unit, 'cols': 30, 'gap': 46, 'r': 16,
            'y0': 360, 'ly': 800, 'lgap': 430, 'groups': groups, 'bg': bg, **kw}
def DOC(doc, lines, hl, source, bg=None, fs=58): return {'layout': 'doc', 'doc': doc, 'lines': lines, 'hl': hl, 'fs': fs, 'source': source, 'bg': bg}
def STACK(kicker, parts, bg=None, **kw): return {'layout': 'stack', 'kicker': kicker, 'parts': parts, 'bg': bg, **kw}
def TL(events, axis=(735, 760), step=5, bg=None, **kw):
    return {'layout': 'timeline', 'axis': list(axis), 'step': step, 'events': events, 'bg': bg, **kw}
def CAST(step=0, bg=None, **kw): return {'layout': 'cast', 'step': step, 'bg': bg, **kw}
def B(img, at, span, a=.22): return {'img': img, 'at': at, 'span': span, 'a': a} if img in HAVE else None

# backdrops: aerials of the places named, and pictures of the things talked about
BG_TODAI = B('todaiji_z17', NARA, 1100, 0.293); BG_TODAI15 = B('todaiji_z15', NARA, 3000, 0.268)
BG_HEIJO = B('heijo_z15', HEIJO, 3000, 0.268); BG_SHIGA = B('shigaraki_z16', SHIGARAKI, 1800, 0.268)
BG_NAGA = B('naganobori_z16', NAGANOBORI, 1800, 0.293); BG_WAKUYA = B('wakuya_z15', WAKUYA, 3000, 0.268)
BG_CHISHIKI = B('chishikiji_z16', CHISHIKI, 1800, 0.268); BG_NIU = B('niu_z15', NIU, 3000, 0.268)
BG_KAMA = B('kamakura_z17', KAMAKURA, 900, 0.293); BG_SHOSO = B('shosoin_z18', SHOSOIN, 500, 0.293)
# 大仏そのものの姿。同時代の像の写真も著作権の切れた絵も手に入らないので、本作のために描き起こした
# （坐像・施無畏印・螺髪・蓮の台座。顔立ちは今の大仏にならっている）
BG_ART = B('daibutsu_art', [1380, 690, 0], 1950, 0.244)
BG_ART_H = B('daibutsu_art', [1660, 430, 0], 1100, 0.268)     # 頭だけ
BG_VAIR = B('vairocana_stone', [960, 1500, 0], 2200, 0.244)   # 石の盧舎那仏（CC0）
def opt(*cands):
    """the first backdrop whose picture was actually found (the Commons hunt may come back empty-handed)"""
    for c in cands:
        if c: return c
    return None
BG_DEN = opt(B('daibutsuden', [800, 600, 0], 1500, 0.268), BG_TODAI)
BG_OLD = opt(B('todaiji_old', [800, 600, 0], 1500, 0.268), BG_TODAI15)
BG_GYOKI = opt(B('gyoki', [600, 600, 0], 1100, 0.268), BG_TODAI15)
BG_SHOMU = opt(B('shomu', [600, 600, 0], 1100, 0.268), BG_HEIJO)
BG_LONG = opt(B('longmen', [800, 600, 0], 1500, 0.268), BG_VAIR)
BG_REN = opt(B('renben', [800, 600, 0], 1500, 0.268), BG_ART)
BG_KOGANE = opt(B('koganeyama', [800, 600, 0], 1500, 0.268), BG_WAKUYA)

# the spine: four questions
MYST = ['何をどれだけ使ったか', '材料はどこから来たか', '15 mにどう流し込んだか', '何人が何年かけたか']
OPEN4 = ['open'] * 4
def MK(*v): return list(v)

# 大仏造立の詔（続日本紀 天平十五年十月辛巳条）
SHO = DOC('『続日本紀』天平十五年　大仏造立の詔',
          ['如更有人', '情願持一枝草', '一把土', '助造像者', '恣聴之'], hl=[1, 2],
          source='史料：『続日本紀』巻第十五 天平十五年十月辛巳条（原文・新字体）', fs=50)
def SHO2(**kw):
    d = dict(SHO); d.update(kw); return d

S = [
    # ───── つかみ（s01–s11）
    P('daibutsu_art', [1380, 690, 0], (1950, 1760),
      text={'kicker': '奈良の大仏はどうやって造られたのか', 'title': '大仏', 'ts': 150,
            'caption': '記録に残された銅は、およそ500トン'}),
    ROWS('数字が残っている', [('東大寺要録', '1300年近く前の記録から', True)], bg=BG_ART),
    CALC('同じ記録に', [['工事に関わった人（延べ）', '260万3638人', True]], bg=BG_ART),
    BARS('大仏の高さ', [{'label': '奈良の大仏', 'value': 14.98, 'text': '14.98 m', 'hi': True},
                        {'label': '5階建てのビル', 'value': 15, 'text': 'およそ15 m', 'col': 'teal'}], max=17, bg=BG_ART),
    CARD('重機も電気もない時代に', 'これをどうやって造ったのか', center=True, bg=BG_ART),
    ROWS('今回したこと', [('東大寺要録の数字', '1つずつ計算', True), ('発掘と研究の成果', '突き合わせ', True)], bg=BG_TODAI),
    CARD('見えてきたのは', '驚くほど理にかなった工事の姿', bg=BG_TODAI),
    COMMENT('予想を一言、コメント欄へ', bg=BG_TODAI),
    COMMENT('工事現場では毎日何人が働いていたと思いますか', bg=BG_TODAI),
    COMMENT('最後に答え合わせを', bg=BG_TODAI),
    CARD('まずは', 'なぜ造られたのかから', bg=BG_TODAI15),

    # ───── なぜ造られたのか（s12–s35）
    ROWS('正式な名前', [('盧舎那仏', 'るしゃなぶつ', True)], bg=BG_VAIR),
    CARD('宇宙のすみずみまで', '光で照らす仏', bg=BG_VAIR),
    ROWS('造ると決めた人', [('聖武天皇', '第45代', True)], bg=BG_SHOMU),
    TL([{'y': 743, 'label': '大仏を造る詔', 'sub': '紫香楽の宮', 'side': 1, 'hi': True}], axis=(735, 760), bg=BG_SHIGA),
    CARD('その少し前の日本は', '大変な苦しみの中にあった', bg=BG_HEIJO),
    ROWS('730年代', [('はやり病', '西日本から都まで広がる', True), ('政治の中心にいた人々', '次々と倒れた')], bg=BG_HEIJO),
    ROWS('続いた災い', [('日照りと飢え', ''), ('740年', '九州で大きな反乱', True)], bg=BG_HEIJO),
    MAP(KINKI, places=[{'at': HEIJO, 'label': '平城京', 'side': -1, 'col': 'gold', 'r': 10},
                       {'at': KUNI, 'label': '恭仁京', 'side': 1, 'col': 'teal', 'r': 9},
                       {'at': NANIWA, 'label': '難波宮', 'side': -1, 'col': 'teal', 'r': 9},
                       {'at': SHIGARAKI, 'label': '紫香楽の宮', 'side': 1, 'col': 'teal', 'r': 9}],
        text={'kicker': '都を何度も移しながら', 'caption': '国を立て直す道を探していた'}),
    CARD('天皇が頼ったのは', '仏の力', bg=BG_HEIJO),
    TL([{'y': 741, 'label': '国分寺・国分尼寺', 'sub': '国ごとに建てよ', 'side': 1, 'hi': True},
        {'y': 743, 'label': '大仏を造る詔', 'side': -1}], axis=(735, 760), bg=BG_HEIJO),
    ROWS('国分寺の頂点', [('奈良', '東大寺', True)], bg=BG_TODAI),
    CARD('その中心に', 'とてつもなく大きな仏を', bg=BG_TODAI),
    CARD('思い立ったきっかけが', 'ありました', bg=BG_CHISHIKI),
    MAP(KINKI, places=[{'at': CHISHIKI, 'label': '知識寺', 'sub': '今の大阪府柏原市（概略）', 'side': 1, 'col': 'gold', 'r': 11},
                       {'at': HEIJO, 'label': '平城京', 'side': -1, 'col': 'faint', 'r': 9}],
        text={'kicker': '740年', 'caption': '聖武天皇が盧舎那仏を拝んだ寺'}),
    ROWS('「知識」とは', [('自分の財や力を差し出して', '仏像や寺づくりに加わる人々', True)], bg=BG_CHISHIKI),
    CARD('知識寺の仏は', '土地の人々が力を合わせて造った', bg=BG_CHISHIKI),
    CARD('海の向こうの唐にも', '手本になる仏が', bg=BG_LONG),
    MAP(EA, places=[{'at': LONGMEN, 'label': '龍門', 'sub': '675年完成・高さ17 mほど', 'side': -1, 'col': 'gold', 'r': 11},
                    {'at': LUOYANG, 'label': '洛陽', 'side': 1, 'col': 'faint', 'r': 9},
                    {'at': NARA, 'label': '奈良', 'side': 1, 'col': 'teal', 'r': 10}],
        text={'kicker': '唐の都の郊外', 'caption': '岩山に彫られた盧舎那仏'}),
    THEO('2つの手本', [{'k': '唐　龍門', 'name': '国家の\n巨大な仏'}, {'k': '河内　知識寺', 'name': '人々が力を\n合わせた仏'}], bg=BG_LONG),
    CARD('その2つを合わせたものが', '聖武天皇の思い描いた大仏', gold=1, bg=BG_VAIR),
    SHO2(bg=BG_SHIGA),
    SHO2(hl=[1, 2, 4], bg=BG_SHIGA),
    CARD('命令で人を集めるのではなく', '国じゅうの心を集めて造る', bg=BG_SHIGA),
    COMMENT('この考え方が、後で効いてきます', bg=BG_SHIGA),

    # ───── 工事と開眼（s36–s56）
    MAP(KINKI, places=[{'at': SHIGARAKI, 'label': '紫香楽', 'sub': '工事はここで始まった', 'side': 1, 'col': 'gold', 'r': 11},
                       {'at': HEIJO, 'label': '平城京', 'side': -1, 'col': 'faint', 'r': 9}],
        text={'kicker': '744年', 'caption': '大仏の体の芯になる柱が立てられた'}),
    TL([{'y': 744, 'label': '体の芯の柱', 'sub': '紫香楽', 'side': 1, 'hi': True}], axis=(740, 756), step=4, bg=BG_SHIGA),
    TL([{'y': 744, 'label': '紫香楽で着工', 'side': 1},
        {'y': 745, 'label': '平城京へ戻る', 'sub': '東大寺の地で造り直し', 'side': -1, 'hi': True}], axis=(740, 756), step=4, bg=BG_TODAI),
    TL([{'y': 744, 'label': '着工', 'side': 1}, {'y': 745, 'label': '造り直し', 'side': -1},
        {'y': 752, 'label': '開眼供養', 'sub': '752年の春', 'side': 1, 'hi': True}], axis=(740, 756), step=4, bg=BG_TODAI),
    CALC('工事にかかった年月', [['745年 → 752年', 'およそ7年', True]], bg=BG_TODAI),
    DOTS('開眼の儀式に集まった僧', [{'n': 10000, 'label': '1万人を超える僧', 'col': 'gold'}], per=100, unit='人', bg=BG_DEN),
    ROWS('目を描き入れたのは', [('菩提僊那', '遠くインドから来た僧', True)], bg=BG_DEN),
    THEO('儀式で演じられた音楽', [{'k': '唐', 'name': '大陸の楽'}, {'k': '朝鮮半島', 'name': '三韓の楽'},
                                  {'k': '林邑', 'name': '今のベトナム'}], bg=BG_DEN),
    CARD('奈良の都に', 'アジアじゅうの文化が集まった1日', bg=BG_DEN),
    ROWS('ただし開眼の日', [('大仏の表面', 'まだ金色ではなかった', True)], bg=BG_TODAI),
    CARD('完成を待たずに行ったのには', '理由があったと考えられています', bg=BG_TODAI),
    TL([{'y': 552, 'label': '仏教が伝わる', 'sub': '日本書紀による', 'side': 1, 'hi': True}], axis=(540, 760), step=40, bg=BG_TODAI),
    CALC('752年とは', [['552年 ＋ 200年', '752年', True]], note='仏教が伝わって、ちょうど200年の年', bg=BG_TODAI),
    CARD('筆に結ばれた長いひもを', '参列した人々が握って縁を結んだ', bg=BG_SHOSO),
    P('shosoin_z18', SHOSOIN, (900, 820), rings=[{'at': SHOSOIN, 'm': 60, 'label': '正倉院', 'side': 1, 'col': 'gold'}],
      scale=50, text={'kicker': '開眼の筆とひも', 'caption': '今も正倉院に残されている'}),
    ROWS('今の大仏', [('高さ（台座を除く）', '14.98 m', True)], bg=BG_ART),
    ROWS('顔と目', [('顔の長さ', '5 mを超える', True), ('目の長さ', '1 mほど', True)], bg=BG_ART_H),
    ROWS('重さ', [('およそ250トン', '', True)], bg=BG_ART),
    BARS('2つの大仏', [{'label': '奈良の大仏', 'value': 14.98, 'text': '14.98 m', 'hi': True},
                       {'label': '鎌倉の大仏', 'value': 11.3, 'text': 'およそ11 m', 'col': 'teal'}], max=17, bg=BG_KAMA),
    ROWS('今の大仏殿', [('幅', 'およそ57 m', True), ('高さ', 'およそ49 m', True)], bg=BG_DEN),
    BARS('大仏殿の幅', [{'label': '今の大仏殿', 'value': 57, 'text': 'およそ57 m', 'col': 'teal'},
                        {'label': '奈良時代', 'value': 86, 'text': 'およそ86 m', 'hi': True}], max=95, bg=BG_DEN),

    # ───── 4つの謎（s57–s63）
    CARD('この巨大な銅の仏像を', 'どうやって造ったのか', center=True, bg=BG_ART),
    MY(OPEN4, kicker='今回の4つの謎', bg=BG_TODAI),
    MY(OPEN4, focus=0, bg=BG_TODAI),
    MY(OPEN4, focus=1, bg=BG_TODAI),
    MY(OPEN4, focus=2, bg=BG_TODAI),
    MY(OPEN4, focus=3, bg=BG_TODAI),
    MY(OPEN4, kicker='1つ解けるごとにお伝えします', bg=BG_TODAI),

    # ───── 謎1 材料（s64–s87）
    CH('01', '何をどれだけ使ったか', '1つ目の謎', bg=BG_ART),
    CARD('大仏には', '何がどれだけ使われたのか', center=True, bg=BG_ART),
    ROWS('手がかりになる記録', [('東大寺要録', '東大寺の歴史をまとめた書物', True)], bg=BG_TODAI),
    ROWS('東大寺要録', [('まとめられた時期', '平安時代の後半'), ('書かれていること', '材料の量が細かく', True)], bg=BG_TODAI),
    ROWS('まず見るのは', [('大仏の体そのもの', '銅', True)], bg=BG_ART),
    CALC('東大寺要録の記録', [['熟銅', '73万9560斤', True]], note='熟銅＝よく精錬された銅', bg=BG_ART),
    ROWS('斤という単位', [('昔の重さの単位', '時代によって重さが変わる', True)], bg=BG_ART),
    CALC('奈良時代の1斤で計算すると', [['73万9560斤 × 600 g', 'およそ440トン'],
                                       ['73万9560斤 × 670 g', 'およそ500トン', True]], bg=BG_ART),
    BARS('重さをくらべると', [{'label': '25 mプール1杯', 'value': 450, 'text': '400〜500トン', 'col': 'teal'},
                              {'label': '大仏の銅', 'value': 470, 'text': '440〜500トン', 'hi': True}], max=560, bg=BG_ART),
    CARD('プール1杯分の水と同じ重さの銅が', '大仏のために溶かされた', gold=1, bg=BG_ART),
    CALC('銅のほかに', [['白鑞（すずと鉛の合金）', '1万2000斤あまり', True]], bg=BG_ART),
    ROWS('白鑞を混ぜる理由', [('銅を', '溶けやすく、流れやすくするため', True)], bg=BG_ART),
    CALC('表面を金色にするための金', [['金', '1万436両', True]], bg=BG_ART),
    CALC('1両をおよそ42 gとして', [['1万436両 × 42 g', 'およそ440 kg', True]], bg=BG_ART),
    CALC('そして水銀', [['水銀', '5万8620両', True]], bg=BG_ART),
    CALC('同じように計算すると', [['5万8620両 × 42 g', 'およそ2.5トン', True]], bg=BG_ART),
    ROWS('金と水銀を混ぜると', [('金が水銀に溶けて', '銀色の柔らかい合金になる', True)], bg=BG_ART),
    ROWS('金めっきの手順', [('塗る', '大仏の表面に合金を'), ('あぶる', '炭火で水銀だけを飛ばす'),
                            ('残る', '金が表面に', True)], bg=BG_ART),
    CALC('金色にする作業だけで', [['表面を金色にする', 'およそ5年', True]], bg=BG_ART),
    CALC('銅を溶かすための炭', [['炭', '1万6656石', True]], bg=BG_NAGA),
    CARD('山ひとつ分の木が', '炭に変えられて炉へ運ばれた', bg=BG_NAGA),
    MY(['solved'] + ['open'] * 3, marks=MK('解けた', '？', '？', '？'), focus=0, reveal=0, bg=BG_ART),
    ROWS('大仏に使われたもの', [('銅', 'プール1杯分ほどの重さ', True), ('金', 'およそ440 kg', True),
                                ('水銀', 'およそ2.5トン', True)], bg=BG_ART),
    MY(['solved'] + ['open'] * 3, marks=MK('解けた', '？', '？', '？'), kicker='4つの謎のうち　1つ', bg=BG_ART),

    # ───── 謎2 材料の出どころ（s88–s105）
    CARD('これだけの材料を', 'どこから集めたのか', center=True, bg=BG_TODAI15),
    CH('02', '材料はどこから来たか', '2つ目の謎', bg=BG_NAGA),
    CARD('まずは', '銅から', bg=BG_NAGA),
    MAP(JPW, places=[{'at': NAGANOBORI, 'label': '長登銅山', 'sub': '山口県美祢市', 'side': 1, 'col': 'gold', 'r': 11},
                     {'at': NARA, 'label': '奈良', 'side': 1, 'col': 'teal', 'r': 10}],
        text={'kicker': '古い銅山の跡', 'caption': '本州の西の端にある'}),
    ROWS('長登という地名', [('奈良の都へ銅を送ったから', '「奈良登り」が始まりと伝わる', True)], bg=BG_NAGA),
    ROWS('1988年からの発掘', [('見つかったもの', '奈良時代の木の札がたくさん', True)], bg=BG_NAGA),
    ROWS('木の札には', [('銅を都へ送った記録', 'が書かれていた', True)], bg=BG_NAGA),
    ROWS('成分の研究から', [('長登の銅', '大仏に使われたと考えられている', True)], bg=BG_NAGA),
    MAP(JPW, routes=[{'pts': [NAGANOBORI, [34.0, 132.4], [34.3, 134.2], NARA], 'col': 'gold', 'wd': 5, 'dashed': True,
                      'label': '長登 → 奈良', 'lat': [33.6, 133.2]}],
        places=[{'at': NAGANOBORI, 'label': '長登', 'side': -1, 'col': 'gold', 'r': 10},
                {'at': NARA, 'label': '奈良', 'side': 1, 'col': 'teal', 'r': 10}]),
    MAP(JP, places=[{'at': NIU, 'label': '丹生', 'sub': '三重県の伊勢地方', 'side': 1, 'col': 'gold', 'r': 11},
                    {'at': NARA, 'label': '奈良', 'side': -1, 'col': 'teal', 'r': 10}],
        text={'kicker': '水銀の産地', 'caption': '大きな産地は伊勢にあった'}),
    ROWS('丹生という地名', [('残る土地では', '古くから水銀が採れた', True)], bg=BG_NIU),
    CARD('いちばん困ったのは', '金でした', bg=BG_TODAI),
    ROWS('当時の日本', [('金', 'まだ1度も採れていなかった', True)], bg=BG_TODAI),
    CARD('外国から手に入れるしかなく', '金色に包む量は集まりそうになかった', bg=BG_TODAI),
    CARD('聖武天皇は', '完成をあきらめかけていたとも伝わる', bg=BG_TODAI),
    COMMENT('金の話の続きは、後ほど', bg=BG_TODAI),
    MY(['solved', 'half', 'open', 'open'], marks=MK('解けた', '銅と水銀だけ', '？', '？'), focus=1, reveal=1, bg=BG_NAGA),
    MY(['solved', 'half', 'open', 'open'], marks=MK('解けた', '銅と水銀だけ', '？', '？'), kicker='4つの謎のうち　1つ半', bg=BG_NAGA),

    # ───── 謎3 どう流し込んだか（s106–s146）
    CH('03', '15 mにどう流し込んだか', '3つ目の謎', bg=BG_ART),
    CARD('高さ15メートルの仏像に', 'どうやって溶けた銅を流し込んだのか', center=True, bg=BG_ART),
    CARD('ここが', '大仏造りの最大の難所', bg=BG_ART),
    ROWS('銅を流し込む', [('銅が溶ける温度', 'およそ1085度'), ('それを15 mの高さへ', '今の技術でも簡単ではない', True)], bg=BG_ART),
    CARD('奈良時代の人々が選んだ方法は', '驚くほど理にかなっていた', bg=BG_ART),
    CAST(mode='core', kicker='① まず原型をつくる', label='土の大仏', note='土と木で、大仏と同じ大きさの像をつくる'),
    CAST(mode='core', kicker='① まず原型をつくる', label='土の大仏', note='太い木の柱を芯にし、わらを混ぜた土を何層にも塗り重ねる'),
    ROWS('わらを混ぜる理由', [('土が乾いても', 'ひび割れにくくするため', True)]),
    CAST(mode='core', kicker='① まず原型をつくる', label='土の大仏', note='最後は目の細かい土で表面を仕上げる'),
    CALC('原型と型づくり', [['745年の秋 → 747年の秋', 'およそ2年', True]]),
    CAST(mode='cover', kicker='② 外側を型で覆う', label='外型', note='原型の外側を、粘土の型ですっぽりと覆う'),
    CAST(mode='cover', kicker='② 外側を型で覆う', label='外型', note='そのあと原型の表面を、銅の厚さの分だけ薄く削り取る'),
    CAST(mode='gap', kicker='③ すきまができる', label='銅の厚さ', note='原型と外型のあいだに、薄いすきまができる'),
    CAST(mode='gap', kicker='③ すきまができる', label='銅の厚さ', note='そこへ溶けた銅を流し込めば、すきまの形どおりの仏像になる'),
    CARD('ところが', '15 mの型に1度で流し込むことはできない'),
    CALC('東大寺要録には', [['3年のあいだに', '8度に分けて鋳込んだ', True]]),
    CAST(step=1, from_=0, kicker='④ 下から8段に分けて', label='1回目', sub='下から順に'),
    CAST(step=1, kicker='④ 下から8段に分けて', label='1回目', sub='ここからが、いちばんの工夫'),
    CAST(step=2, from_=1, furnace=True, kicker='⑤ 土を盛って地面を高くする', label='2回目', sub='型の周りを土で埋める'),
    CAST(step=3, from_=2, furnace=True, kicker='⑤ 土を盛って地面を高くする', label='3回目', sub='山の上に炉を並べ、ふいごで火を強める'),
    CAST(step=4, from_=3, furnace=True, kicker='⑤ 土を盛って地面を高くする', label='4回目', sub='溶けた銅は、すぐ横の型へ'),
    CAST(step=6, from_=4, furnace=True, kicker='⑤ 土を盛って地面を高くする', label='6回目', sub='また土を盛り、また流し込む'),
    CAST(step=7, from_=6, furnace=True, kicker='⑥ 持ち上げる必要はなかった', label='7回目', sub='銅を15 mまで上げる必要はない'),
    CAST(step=8, from_=7, furnace=True, kicker='⑥ 持ち上げる必要はなかった', label='8回目', sub='いつも足元の高さで流し込む'),
    CAST(step=8.7, from_=8, kicker='⑦ 大仏は土の山の中', label='丸ごと埋まる', note='8回目が終わったとき、大仏は巨大な土の山の中にあった'),
    CAST(step=8, mound=False, kicker='⑧ 土を取り除く', label='姿を現す', note='土をすべて取り除いて、初めて大仏は姿を現した'),
    CALC('1回あたりの銅', [['500トン ÷ 8回', 'およそ60トン', True]]),
    TL([{'y': 747, 'label': '鋳込み始まる', 'side': 1, 'hi': True}, {'y': 749, 'label': '鋳込み終わる', 'side': -1, 'hi': True}],
       axis=(744, 754), step=2),
    ROWS('うまくいかなかった所', [('流し込んだ銅が回らず', 'すきまや穴ができた', True)]),
    ROWS('そうした所は', [('あとから銅を足して', '埋める作業がくり返された', True)]),
    ROWS('頭の巻き毛', [('体とは別に鋳造してから', '取り付けられた', True)], bg=BG_ART_H),
    P('daibutsu_art', [1660, 400, 0], (1150, 1050),
      text={'kicker': '頭の巻き毛', 'caption': '拳ほどの大きさの巻き毛がびっしりと並ぶ'}),
    CARD('この工事を率いた技術者の名前も', '記録に残っています', bg=BG_ART),
    ROWS('工事を率いた2人', [('大仏師', '国中連公麻呂', True), ('鋳物師の頭', '高市大国', True)], bg=BG_ART),
    ROWS('国中連公麻呂', [('朝鮮半島の百済から', '海を渡ってきた人の孫', True)], bg=BG_ART),
    CARD('海の向こうから伝わった技が', '大仏の形を決めていた', bg=BG_ART),
    CARD('大仏造りの工夫は', '1つの考え方にまとめられます'),
    CARD('難しいことを1度にやろうとせず', '小さな作業に分けて、くり返す', gold=1),
    MY(['solved', 'half', 'solved', 'open'], marks=MK('解けた', '銅と水銀だけ', '解けた', '？'), focus=2, reveal=2),
    CAST(step=5, from_=5, furnace=True, kicker='3つ目の謎の答え', label='足元で流し込む', note='大仏を土で埋めながら、いつも足元の高さで鋳込んでいた'),
    MY(['solved', 'half', 'solved', 'open'], marks=MK('解けた', '銅と水銀だけ', '解けた', '？'), kicker='4つの謎のうち　2つ半'),

    # ───── チャンネルのお願い（s147–s151）
    COMMENT('いただいたコメントで', '次に確かめるテーマを決めています', bg=BG_TODAI15),
    COMMENT('大仏のことでも', 'ほかの日本史の謎でも', bg=BG_TODAI15),
    COMMENT('確かめてほしい謎を、ぜひコメントで', bg=BG_TODAI15),
    CARD('日本の歴史の謎を', '記録と数字で1つずつ', bg=BG_TODAI15),
    COMMENT('チャンネル登録を', '次の検証を見逃さないように', bg=BG_TODAI15),

    # ───── 金はどこから来たか（s152–s170）
    CARD('後回しにしていた', '金の話に戻ります', bg=BG_WAKUYA),
    CARD('大仏を金色に包むための金は', 'どこから来たのか', center=True, bg=BG_WAKUYA),
    TL([{'y': 749, 'label': '陸奥から知らせ', 'sub': '749年の春', 'side': 1, 'hi': True}], axis=(744, 754), step=2, bg=BG_WAKUYA),
    CARD('陸奥の国で', '日本で初めて金が見つかった', gold=1, bg=BG_WAKUYA),
    MAP(JPNE, places=[{'at': WAKUYA, 'label': '涌谷', 'sub': '今の宮城県（概略）', 'side': 1, 'col': 'gold', 'r': 11},
                      {'at': NARA, 'label': '奈良', 'side': -1, 'col': 'teal', 'r': 10}],
        routes=[{'pts': [WAKUYA, [37.5, 139.8], [35.8, 137.4], NARA], 'col': 'gold', 'wd': 4, 'dashed': True}],
        text={'kicker': '金が見つかった場所', 'caption': '陸奥の国から都へ'}),
    CALC('都へ送られた金', [['陸奥の国の長官から', '金900両', True]], bg=BG_KOGANE),
    ROWS('その長官', [('百済王敬福', '百済の王族の流れをくむ人', True)], bg=BG_KOGANE),
    THEO('海を渡ってきた人々の力', [{'k': '大仏の形', 'name': '国中連公麻呂', 'sub': '百済から来た人の孫'},
                                    {'k': '大仏の金', 'name': '百済王敬福', 'sub': '陸奥の国の長官'}], bg=BG_KOGANE),
    CARD('聖武天皇は大変に喜び', '自ら大仏の前でその喜びを報告した', bg=BG_TODAI),
    ROWS('喜びのしるし', [('年号', '天平感宝と改められた', True)], bg=BG_TODAI),
    ROWS('万葉集に残る歌', [('詠んだのは', '大伴家持', True)], bg=BG_WAKUYA),
    DOC('『万葉集』巻十八　四〇九七', ['すめろきの', '御代栄えむと', '東なる', '陸奥山に', '金花咲く'], hl=[4],
        source='史料：『万葉集』巻第十八 四〇九七（大伴家持）', bg=BG_WAKUYA, fs=46),
    CARD('天皇の世が栄えるしるしとして', '東の陸奥の山に金の花が咲いた', bg=BG_WAKUYA),
    BARS('必要な金と、最初に届いた金', [{'label': '大仏に必要な金', 'value': 10436, 'text': '1万436両', 'hi': True},
                                        {'label': '最初に届いた金', 'value': 900, 'text': '900両', 'col': 'teal'}], max=11000, bg=BG_KOGANE),
    ROWS('その後も', [('陸奥の国から金が送られ', '大仏は少しずつ金色に包まれた', True)], bg=BG_KOGANE),
    P('wakuya_z15', WAKUYA, (2600, 2400), rings=[{'at': WAKUYA, 'm': 900, 'label': '涌谷町', 'side': 1, 'col': 'gold'}],
      scale=1000, text={'kicker': '金が採れた場所には', 'caption': '今も黄金山神社が建っている（位置は概略）'}),
    CARD('日本の金の歴史は', '大仏のためにここから始まった', bg=BG_KOGANE),
    MY(['solved', 'solved', 'solved', 'open'], marks=MK('解けた', '解けた', '解けた', '？'), focus=1, reveal=1, bg=BG_KOGANE),
    MY(['solved', 'solved', 'solved', 'open'], marks=MK('解けた', '解けた', '解けた', '？'), kicker='4つの謎のうち　3つ', bg=BG_KOGANE),

    # ───── 謎4 何人が何年か（s171–s208）
    CH('04', '何人が何年かけたか', '4つ目の謎', bg=BG_TODAI15),
    CARD('ここで', 'もう1度 東大寺要録の数字を', bg=BG_TODAI15),
    ROWS('記録は4つに分かれている', [('大仏と大仏殿に関わった人の数', '4つの内訳', True)], bg=BG_TODAI15),
    ROWS('材木の側', [('材木を寄進した人', '5万1590人', True), ('運搬などで働いた人', '166万5071人', True)], bg=BG_TODAI15),
    ROWS('金属の側', [('金属を寄進した人', '37万2075人', True), ('その工事で働いた人', '51万4902人', True)], bg=BG_TODAI15),
    CALC('4つを足すと', [['5万1590 ＋ 166万5071', ''], ['＋ 37万2075 ＋ 51万4902', '260万3638人', True]], bg=BG_TODAI15),
    STACK('260万3638人の内訳', [{'v': 2.0, 'c': 'teal', 'text': '5万', 'label': '材木を寄進', 'sub': '5万1590人'},
                                {'v': 64.0, 'c': 'gold', 'text': '166万', 'label': '材木を運ぶ', 'sub': '166万5071人'},
                                {'v': 14.3, 'c': 'cream', 'text': '37万', 'label': '金属を寄進', 'sub': '37万2075人'},
                                {'v': 19.7, 'c': 'dim', 'text': '51万', 'label': '金属の工事', 'sub': '51万4902人'}],
          src='東大寺要録の数字から'),
    BARS('材木の側と金属の側', [{'label': '材木の側', 'value': 171, 'text': '171万人あまり', 'hi': True},
                                {'label': '金属の側', 'value': 88, 'text': '88万人あまり', 'col': 'teal'}], max=190),
    CARD('巨大な銅の仏よりも', '大仏殿の木材を運ぶほうに人手がかかった'),
    BARS('奈良時代の日本', [{'label': '人口（推計）', 'value': 450, 'text': 'およそ450万人', 'col': 'teal'},
                            {'label': '延べ人数', 'value': 260, 'text': '260万3638人', 'hi': True}], max=500, bg=BG_HEIJO),
    CARD('260万人は', '人口の半分を大きく超えている', bg=BG_HEIJO),
    ROWS('ただし', [('これは', '延べ人数', True)], bg=BG_HEIJO),
    CALC('延べ人数とは', [['同じ人が10日働けば', '10人と数える', True]], bg=BG_HEIJO),
    CARD('国民の半分以上が', '工事に加わったわけではない', bg=BG_HEIJO),
    ROWS('平城京', [('暮らしていた人', 'およそ10万人', True)], bg=BG_HEIJO),
    CARD('都の人口の何割もが駆り出されていたら', '都の暮らしは成り立たなかったはず', bg=BG_HEIJO),
    CARD('では毎日の現場には', '何人くらいがいたのか', center=True, bg=BG_TODAI),
    CALC('工事の期間', [['745年 → 752年', 'およそ7年', True]], bg=BG_TODAI),
    CALC('日数に直すと', [['7年 × 365日', 'およそ2555日', True]], bg=BG_TODAI),
    CALC('1日あたりの人数', [['260万3638人 ÷ 2555日', 'およそ1000人', True]], bg=BG_TODAI),
    CALC('働いた人だけで計算すると', [['218万人 ÷ 2555日', 'およそ850人', True]], note='寄進した人を除いた数', bg=BG_TODAI),
    COMMENT('最初の予想は、いかがだったでしょうか', bg=BG_TODAI),
    BARS('前回の古墳とくらべると', [{'label': '日本最大の古墳', 'value': 2000, 'text': '多い日で2000人ほど', 'col': 'teal'},
                                    {'label': '大仏の現場', 'value': 1000, 'text': '1日およそ1000人', 'hi': True}], max=3000),
    CARD('260万人という数字に比べると', '毎日の現場は意外なほど少ない'),
    CARD('ここで見落とせないのが', '寄進した人の数'),
    DOTS('何らかの品を差し出した人', [{'n': 423665, 'label': '材木と金属を合わせて42万人あまり', 'col': 'gold'}],
         per=1000, unit='人'),
    SHO2(hl=[1, 2], bg=BG_SHIGA),
    CARD('その呼びかけに', '40万人以上が応えた', gold=1, bg=BG_SHIGA),
    CARD('寄進したのは', '名もない人々だけではありません'),
    ROWS('越中の国（今の富山県）', [('豪族が米3000石を寄進し', '位を授けられたと記録にある', True)]),
    ROWS('寄進を集めて回ったのは', [('行基', '僧', True)], bg=BG_GYOKI),
    ROWS('行基という僧', [('各地で橋や池を造り', '人々に深く慕われていた', True)], bg=BG_GYOKI),
    ROWS('朝廷との関係', [('かつては活動を禁じられ', '大仏造りでは力を借りられた', True)], bg=BG_GYOKI),
    TL([{'y': 745, 'label': '行基、大僧正に', 'sub': '日本で初めて', 'side': 1, 'hi': True}], axis=(740, 756), step=4, bg=BG_GYOKI),
    THEO('大仏を造ったもの', [{'k': '毎日の現場', 'name': '1日およそ1000人'},
                              {'k': '国じゅうから', 'name': '40万人を超える寄進'}], bg=BG_TODAI),
    CARD('大仏は、天皇の命令だけでなく', '国じゅうの人々の手で造られていた', gold=1, bg=BG_TODAI),
    MY(['solved'] * 4, marks=MK('解けた', '解けた', '解けた', '解けた'), focus=3, reveal=3, bg=BG_TODAI),
    MY(['solved'] * 4, marks=MK('解けた', '解けた', '解けた', '解けた'), kicker='4つの謎のうち　4つすべて', bg=BG_TODAI),

    # ───── 弱点（s209–s226）
    CARD('ただし', 'この答えには弱点があります'),
    ROWS('弱点は3つ', [('1', '記録の数字の確かさ', True), ('2', '重さの単位'), ('3', '今の大仏は奈良時代のものか')]),
    ROWS('弱点 1', [('記録の数字', 'そのものの確かさ', True)]),
    TL([{'y': 752, 'label': '大仏の開眼', 'side': 1, 'hi': True},
        {'y': 1106, 'label': '東大寺要録', 'sub': '350年以上あと', 'side': -1, 'hi': True}], axis=(700, 1750), step=200),
    ROWS('写すうちに', [('古い記録から写されたとされるが', '数字が変わった可能性もある', True)]),
    ROWS('実際に', [('資料によって', '白鑞や金の量に食い違いがある', True)]),
    ROWS('弱点 2', [('1斤や1両が何グラムか', '時代や物によって違う', True)]),
    BARS('銅の量', [{'label': '1斤600 gなら', 'value': 440, 'text': 'およそ440トン', 'col': 'teal'},
                    {'label': '1斤670 gなら', 'value': 500, 'text': 'およそ500トン', 'hi': True}], max=560),
    CARD('弱点 3', '大部分は奈良時代のものではない', bg=BG_ART),
    CARD('大仏はこれまでに', '何度も大きな被害を受けてきました', bg=BG_ART),
    TL([{'y': 855, 'label': '地震', 'sub': '頭が落ちる', 'side': 1, 'hi': True},
        {'y': 1180, 'label': '焼失', 'sub': '大仏殿ごと', 'side': -1, 'hi': True},
        {'y': 1567, 'label': '焼失', 'sub': '戦いの中で', 'side': 1, 'hi': True}], axis=(750, 1750), step=200),
    ROWS('1180年のあと', [('重源', '国じゅうを回って寄進を集めた', True), ('宋の技術者の力を借り', '5年で造り直した')]),
    CARD('1567年のあとは', '頭のない大仏が長いあいだ雨にさらされた'),
    ROWS('元の姿に戻したのは', [('公慶', '江戸時代の僧', True)]),
    TL([{'y': 1180, 'label': '焼失', 'side': 1}, {'y': 1185, 'label': '重源が再建', 'side': -1},
        {'y': 1567, 'label': '焼失', 'side': 1}, {'y': 1692, 'label': '今の頭', 'sub': '公慶が再建', 'side': -1, 'hi': True}],
       axis=(1150, 1750), step=100),
    ROWS('奈良時代のまま残るのは', [('台座の蓮の花びらなど', 'ごく一部だけ', True)], bg=BG_REN),
    CARD('その花びらには', '仏たちの住む世界が細い線で刻まれている', bg=BG_REN),
    CARD('工事の細かい手順の多くは', '記録と研究から組み立てた姿です'),

    # ───── 結論（s227–s246）
    CARD('それでも', '今ある記録から考える限り、答えは1つ', bg=BG_ART),
    CAST(step=8, from_=6, furnace=True, kicker='結論', label='8回に分けて', sub='土の山に埋めながら鋳込む'),
    ROWS('奈良の大仏', [('毎日の現場', 'およそ1000人', True), ('寄進した人', '40万人以上', True),
                        ('開眼まで', 'およそ7年', True)], bg=BG_ART),
    CAST(step=8.7, from_=8.7, kicker='749年の秋', label='巨大な土の山', note='平城京の東の山すそには、土の山がそびえていたはず'),
    CAST(step=8, mound=False, kicker='その山が取り除かれた日', label='15 mの仏', note='人々の前に、はじめてその姿を現した'),
    CARD('炉の火を守り続けた鋳物師も', '土を運び続けた働き手も、その日を待った', bg=BG_ART),
    CARD('遠い国から寄進をした人々も', '同じ思いだったことでしょう', bg=BG_ART),
    CARD('草1本や土ひとにぎりを持って集まった人々は', 'その姿をどんな思いで見上げたのか', center=True, fs=62, bg=BG_ART),
    P('todaiji_z17', NARA, (1200, 1100), rings=[{'at': NARA, 'm': 70, 'label': '東大寺 大仏殿', 'side': 1, 'col': 'gold'}],
      scale=100, text={'kicker': 'あれから1270年以上', 'caption': '大仏は同じ場所に座り続けている'}),
    CARD('何度炎に包まれても', 'そのたびに人々の手で造り直されてきた', bg=BG_TODAI),
    ROWS('国じゅうを歩いた僧', [('奈良時代', '行基', True), ('鎌倉時代', '重源', True)], bg=BG_GYOKI),
    ROWS('国じゅうを歩いた僧', [('奈良時代', '行基'), ('鎌倉時代', '重源'), ('江戸時代', '公慶', True)], bg=BG_GYOKI),
    CARD('大仏はいつの時代も', '1人の命令ではなく、大勢の人々の手で', gold=1, bg=BG_ART),
    CARD('修学旅行で見上げたあの大仏の中には', '500トンの銅と、数えきれない思いが', bg=BG_ART),
    COMMENT('大仏造りは国を1つにまとめたと思いますか', bg=BG_ART),
    COMMENT('それとも、人々を疲れさせたと思いますか', bg=BG_ART),
    COMMENT('ぜひコメント欄で教えてください', bg=BG_ART),
    COMMENT('最初に書いていただいた予想とも', '比べてみてください', bg=BG_ART),
    CARD('次回は', '徳川埋蔵金は本当にあるのか', bg=BG_TODAI15),
    CARD('最後までご覧いただき', 'ありがとうございました', center=True, bg=BG_ART),
]

# `from` is a Python keyword, so the scenes use from_ and it is renamed here
for s in S:
    if 'from_' in s: s['from'] = s.pop('from_')

# every shot keeps some texture behind the type: the casting diagram gets a faint one, the rest the
# aerial of the place that part of the film is about
BG_FAINT = B('todaiji_z17', NARA, 1700, 0.26)
FILL = [(range(106, 147), BG_ART), (range(147, 172), BG_TODAI15), (range(172, 209), BG_TODAI15),
        (range(209, 227), BG_ART), (range(227, 247), BG_ART)]
for i, s in enumerate(S, 1):
    if s.get('bg') or s['layout'] in ('map', 'photo'): continue
    s['bg'] = BG_FAINT if s['layout'] == 'cast' else next((b for r, b in FILL if i in r), BG_TODAI)

lines = json.load(open('lines.json', encoding='utf-8')) if os.path.exists('lines.json') else []
if lines and len(lines) != len(S):
    sys.exit(f'✗ {len(S)} scenes for {len(lines)} sentences')

# readings VOICEVOX cannot get from the written sentence
SAY = {'s83': lambda t: t.replace('1万6656石', '1万6656こく'),
       's163': lambda t: 'すめろきのみよ、さかえむと、あずまなるみちのくやまに、くがねはなさく。',
       's200': lambda t: t.replace('米3000石', 'こめ3000こく')}

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

# Same picture, next sentence: continue the shot (cont) instead of cutting to an identical frame
ALWAYS = {'mysteries', 'timeline', 'bars', 'doc', 'stack'}
def same_picture(a, b):
    if a['layout'] != b['layout']: return False
    if a['layout'] == 'photo': return a['img'] == b['img'] and a['at'] == b['at']
    if a['layout'] == 'map': return a['view'] == b['view']
    if a['layout'] == 'cast': return a.get('kicker') == b.get('kicker') and a.get('mode') == b.get('mode')
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

ART = 'イラスト　本作オリジナル（奈良の大仏の姿にならって描き起こし）'
out = {'_about': 'One entry per sentence (same order as script.txt); generated by tools/make_scenes.py (Claude Code). Layouts: index.html L.*.',
       'title': '大仏はどうやって造られたのか', 'title_en': 'How the Great Buddha Was Cast', 'mysteries': MYST,
       'board': {'kicker': '4つの謎', 'solved': '解けた'}, 'chapter_label': 'MYSTERY',
       'credits': ['地図　Natural Earth（パブリックドメイン）をもとに作図　空中写真　出典：国土地理院（地理院タイル）',
                   '史料　『続日本紀』巻第十五 天平十五年十月辛巳条 ／『万葉集』巻第十八 四〇九七（原文・新字体）',
                   '数字　『東大寺要録』の材料と人数の記載にもとづく',
                   *(['写真　' + '、'.join(sorted(WIKI_NAMES)) + '（Wikimedia Commons、パブリックドメイン・CC0）'] if WIKI_NAMES else []),
                   ART,
                   '音声　VOICEVOX:青山龍星',
                   '鋳込みの図・地図上の位置は模式図、遺跡の位置の一部は概略です。'],
       'scenes': S}
json.dump(out, open('scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(S), 'scenes', dict(Counter(s['layout'] for s in S)), sum(1 for s in S if s.get('cont')), 'cont')
