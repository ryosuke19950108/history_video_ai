#!/usr/bin/env python3
"""Scene assignment for 日本最大の古墳はどうやって築かれたのか (handbook 11-3 step 2), written by Claude Code in the session.
One entry per sentence of script.txt, in order → scenes.json. Layouts: index.html `L.*`."""
import json, sys

DS = [34.5642, 135.4875]; KD = [34.5617, 135.6097]; IN = [36.1278, 139.4778]; HS = [34.5392611, 135.8412278]
SK = [34.5733, 135.4831]; OSY = [34.52, 135.68]
GSI = {'seamlessphoto': '空中写真', 'hillshademap': '陰影起伏図', 'ort_USA10': '1945〜50年 米軍撮影の空中写真', 'ort_old10': '1961〜69年撮影の空中写真'}
LAYER = {'daisen_z17': 'seamlessphoto', 'mozu_z15': 'seamlessphoto', 'konda_z16': 'seamlessphoto', 'inariyama_z17': 'seamlessphoto', 'hajinosato_z17': 'seamlessphoto',
         'osaka_hill_z11': 'hillshademap', 'sakai_hill_z13': 'hillshademap', 'japan_hill_z8': 'hillshademap', 'daisen_1940s_z16': 'ort_USA10', 'daisen_1960s_z16': 'ort_old10'}
OB = '出典：大林組の試算（1985）'
BG = [{'img': 'daisen_z17', 'at': DS, 'span': 1900, 'a': .12}, {'img': 'daisen_1940s_z16', 'at': DS, 'span': 2400, 'a': .14}, {'img': 'osaka_hill_z11', 'at': [34.56, 135.6], 'span': 70000, 'a': .16}]
_bgi = [0]
def bg():
    _bgi[0] += 1; return BG[_bgi[0] % len(BG)]

def P(img, at=DS, span=(1500, 1350), **kw): return {'layout': 'photo', 'img': img, 'at': at, 'span': list(span), **kw}
def T(kicker=None, title=None, number=None, unit=None, caption=None, **kw): return {k: v for k, v in dict(kicker=kicker, title=title, number=number, unit=unit, caption=caption, **kw).items() if v is not None}
def CARD(*lines, **kw): return {'layout': 'card', 'lines': list(lines), 'bg': kw.pop('bg', None) or bg(), **kw}
def CH(num, title, sub=None): return {'layout': 'chapter', 'num': num, 'title': title, 'sub': sub, 'bg': {'img': 'daisen_1940s_z16', 'at': DS, 'span': 2000, 'a': .12}}
def MY(status=(), focus=None, reveal=None, kicker=None): return {'layout': 'mysteries', 'status': list(status), 'focus': focus, 'reveal': reveal, 'kicker': kicker}
def BARS(kicker, items, **kw): return {'layout': 'bars', 'kicker': kicker, 'items': items, 'bg': bg(), **kw}
def CALC(kicker, rows, **kw): return {'layout': 'calc', 'kicker': kicker, 'rows': rows, 'bg': bg(), **kw}
def ROWS(kicker, rows, **kw): return {'layout': 'rows', 'kicker': kicker, 'rows': [r if isinstance(r, dict) else {'k': r[0], 'v': r[1] if len(r) > 1 else '', 'hi': len(r) > 2} for r in rows], 'bg': bg(), **kw}
def DOTS(kicker, groups, per=50): return {'layout': 'dots', 'kicker': kicker, 'groups': groups, 'per': per}
def DOC(doc, lines, hl, fs=66): return {'layout': 'doc', 'doc': doc, 'lines': lines, 'hl': hl, 'fs': fs, 'source': '史料：『日本書紀』巻第五 崇神天皇十年条（書き下しによる翻刻）'}
def COMMENT(text, sub=None): return {'layout': 'comment', 'text': text, 'sub': sub, 'bg': {'img': 'daisen_z17', 'at': DS, 'span': 2600, 'a': .08}}
def SEC(mode, kicker, label=None): return {'layout': 'section', 'mode': mode, 'kicker': kicker, 'label': label}
TH = [{'k': '説 1', 'name': '無理やり\n働かせた', 'sub': '権力者が大勢の民を'}, {'k': '説 2', 'name': '農閑期に\n交代で加わる', 'sub': '近くの村の人々が'}, {'k': '説 3', 'name': '専門の人々が\n中心に', 'sub': '土師氏のような人々'}]
def THEO(**kw): return {'layout': 'theories', 'kicker': '働いた人々についての3つの説', 'items': TH, 'bg': {'img': 'daisen_1960s_z16', 'at': DS, 'span': 2400, 'a': .1}, **kw}
BUD = lambda step: {'layout': 'budget', 'step': step, 'source': OB}
TL1 = {'layout': 'timeline', 'kicker': '文字と記録の年表', 'axis': [400, 760], 'step': 40}
EV1 = [{'y': 450, 'label': '大仙古墳', 'sub': '5世紀中頃', 'side': 1}, {'y': 471, 'label': '稲荷山の鉄剣', 'sub': '471年', 'side': -1}]
EV2 = EV1 + [{'y': 712, 'label': '古事記', 'sub': '712年', 'side': 1}, {'y': 720, 'label': '日本書紀', 'sub': '720年', 'side': -1, 'hi': True}]
SQ = [{'label': '大仙古墳', 'm2': 121000, 'text': '約12万1000 m²', 'hi': True}, {'label': 'クフ王のピラミッド', 'm2': 53000, 'text': '約5万3000 m²'}]
SQ3 = SQ + [{'label': '秦の始皇帝陵', 'm2': 122000, 'text': '約12万2000 m²'}]
MYS = ['どれだけ大きいのか', '土はどこから来たのか', '何人で何年かかったのか', 'なぜ崩れないのか']
ALL = ['solved', 'solved', 'half', 'solved']
OLD = lambda span=(2400, 2000), **kw: P('daisen_1940s_z16', DS, span, stamp='1945〜50年 米軍撮影', **kw)
RW_WEAK = [('弱点 1', '数字の多くは建設会社の試算'), ('弱点 2', '日本書紀の話は纒向の古墳'), ('弱点 3', '内部は発掘できない')]
def weak(n, hi): return ROWS('この結果の弱いところ', [(k, v, True) if i == hi else (k, v) for i, (k, v) in enumerate(RW_WEAK[:n])])

S = [
 # 1 hook
 P('daisen_z17', DS, (1700, 1300), outline=True, text=T('大仙古墳 · 大阪府堺市', None, '約200万', 'm³', '運ばれた土の量（試算）')),
 BARS('土の量のたとえ', [{'label': '運ばれた土', 'value': 200, 'text': '約200万 m³', 'hi': True}, {'label': '東京ドーム', 'value': 124, 'text': '1杯分'}], max=220, note='東京ドームのおよそ1.6杯分'),
 OLD((2800, 2300)),
 CARD('何人で、何年かけて、', 'どうやって築いたのか。', fs=76),
 CARD('工事の記録は、', '残っていない。'),
 CARD('文字は、', 'あった。'),
 P('inariyama_z17', IN, (950, 800), rings=[{'at': IN, 'm': 130, 'label': '稲荷山古墳', 'sub': '埼玉県行田市（位置は概略）', 'side': -1}], text=T('鉄剣に刻まれた年', None, '471', '年', None, y=380)),
 dict(TL1, events=EV1),
 dict(TL1, events=EV2, spans=[{'from': 450, 'to': 720, 'label': '250年以上の空白'}]),
 {'layout': 'theories', 'kicker': '3つの手がかり', 'items': [{'k': '手がかり 1', 'name': '発掘の\n調査結果'}, {'k': '手がかり 2', 'name': '建設会社の\n試算'}, {'k': '手がかり 3', 'name': '日本書紀の\n記述'}], 'bg': bg()},
 CARD('記録と数字で、', '1つずつ確かめる。'),
 P('daisen_1960s_z16', DS, (2300, 1900), stamp='1961〜69年撮影'),
 ROWS('工事現場にいた人々', [('土を運ぶ人',), ('道具を作る人',), ('米を炊く人',), ('石を集める人', '', 1)], dt=.35),
 COMMENT('あなたの予想は？', '何年かかったと思うか、コメント欄へ'),
 CARD('日本最大の古墳。', '何年かかった？', center=True),
 # 2 the tomb
 P('japan_hill_z8', DS, (900000, 650000), rings=[{'at': DS, 'r': 22, 'label': '大仙古墳', 'sub': '大阪府堺市'}]),
 P('mozu_z15', DS, (6000, 4300), rings=[{'at': DS, 'm': 330, 'label': '大仙古墳', 'sub': '仁徳天皇陵 · 宮内庁が管理'}], scale=1000),
 P('daisen_z17', DS, (1700, 1500), outline=True, text=T('築造', None, '5世紀', None, '中頃と考えられる')),
 ROWS('呼び方', [('仁徳天皇陵', '宮内庁の呼び方'), ('大仙古墳・大山古墳', '教科書で増えた書き方', 1)]),
 CARD('誰の墓なのか。', '確かめる手立ては、ない。'),
 CARD('どうやって築いたのか。', kicker='今回確かめること'),
 P('daisen_z17', DS, (1500, 1350), outline=True, text=T('前方後円墳', '鍵穴の形')),
 OLD((1500, 1350), text=T('墳丘3段 · 堀3重', None, '3重', None, 'まわりを囲む堀')),
 P('mozu_z15', DS, (7500, 5800), text=T('世界遺産', None, '2019', '年7月', '百舌鳥・古市古墳群')),
 CARD('日本に、古墳は', 'いくつある？'),
 BARS('全国の古墳の数', [{'label': '古墳', 'value': 16, 'text': '約16万基', 'hi': True}], max=18),
 BARS('全国の古墳の数', [{'label': '古墳', 'value': 16, 'text': '約16万基', 'hi': True}, {'label': 'コンビニ', 'value': 5.33, 'text': '古墳の約3分の1'}], max=18),
 BARS('全国の古墳の数', [{'label': '古墳', 'value': 16, 'text': '約16万基'}, {'label': '前方後円墳', 'value': .47, 'text': '約4700基', 'hi': True}], max=18),
 P('daisen_z17', DS, (1300, 1150), outline=True, text=T('日本最大', '大仙古墳')),
 P('konda_z16', KD, (2600, 2200), rings=[{'at': KD, 'm': 280, 'label': '誉田御廟山古墳', 'sub': '大阪府羽曳野市 · 墳丘長425m'}]),
 P('osaka_hill_z11', [34.57, 135.55], (95000, 75000), rings=[{'at': DS, 'r': 20, 'label': '百舌鳥（大仙古墳）', 'side': -1}, {'at': KD, 'r': 20, 'label': '古市（誉田御廟山古墳）'}]),
 MY(),
 MY(focus=0), MY(focus=2), MY(kicker='最後に、いくつ解けたか'),
 # mystery 1
 CH('01', 'どれだけ大きいのか'),
 P('daisen_z17', DS, (1250, 1100), outline=True),
 P('daisen_z17', DS, (1450, 1400), outline=True, text=T('教科書・案内板', None, '486', 'm', '墳丘の長さ')),
 P('daisen_z17', DS, (1400, 1350), outline=True, text=T('堺市の博物館も', None, '486', 'm', '長いあいだ使われた数字')),
 CARD('2018年、', '数字が変わった。', gold=0),
 BARS('墳丘の長さ', [{'label': '従来', 'value': 486, 'text': '486 m'}, {'label': '2018年 3次元測量', 'value': 525.1, 'text': '525.1 m', 'hi': True}], max=560, source='出典：宮内庁による3次元測量（2018年、台本による）'),
 CALC('差', [['525.1 m − 486 m', '約40 m'], ['25 m プール', '1本半を超える', 1]]),
 CARD('なぜ、', '長さが変わったのか。'),
 P('daisen_z17', [1440, 1400, 'px'], (900, 800), rings=[{'at': [1440, 1475, 'px'], 'r': 60, 'label': '裾（すそ）', 'side': -1}]),
 SEC('terraces', '墳丘のいちばん下の部分', '削られ、埋もれていた裾'),
 SEC('terraces', '測り直すと', '本来の裾は、もっと外側'),
 BARS('墳丘の底の面積', [{'label': '従来', 'value': 10.3, 'text': '約10万3000 m²'}, {'label': '測り直し', 'value': 12.1, 'text': '約12万1000 m²', 'hi': True}], max=14, note='2割近く広がった'),
 CARD('世界の巨大建造物と', '比べてみる。'),
 {'layout': 'squares', 'kicker': '底の面積（同じ縮尺）', 'items': SQ, 'note': '数値は台本による'},
 {'layout': 'squares', 'kicker': '底の面積（同じ縮尺）', 'items': SQ3, 'note': '数値は台本による'},
 {'layout': 'squares', 'kicker': '底の面積（同じ縮尺）', 'items': SQ3, 'note': 'ほぼ同じ広さ'},
 CARD('高さでは、', 'ピラミッドにかなわない。'),
 BARS('積み上げた量', [{'label': 'クフ王のピラミッド', 'value': 260, 'text': '約260万 m³'}, {'label': '大仙古墳の墳丘', 'value': 140, 'text': '約140万 m³', 'hi': True}], max=290),
 P('daisen_z17', DS, (1150, 1000), outline=True, text=T('地面を覆う広さ', '世界最大級')),
 CARD('なぜ、', 'これほど大きく造ったのか。'),
 CARD('記録は、ない。', '有力な見方がある。'),
 P('sakai_hill_z13', [34.5642, 135.46], (22000, 18000), rings=[{'at': DS, 'r': 24, 'label': '大仙古墳', 'sub': '堺の台地'}], stamp='現在の地形（陰影起伏図）'),
 P('osaka_hill_z11', [34.55, 135.33], (70000, 34000), to=DS, rings=[{'at': DS, 'r': 18, 'label': '大仙古墳'}], stamp='大阪湾から'),
 P('mozu_z15', [34.565, 135.47], (6500, 5200), text=T('研究者の見方', '海から見える場所に', ts=72)),
 MY(['solved'], 0, 0), MY(['solved'], 0),
 # mystery 2
 CARD('これだけの土は、', 'どこから来たのか。'),
 CH('02', '土はどこから来たのか'),
 OLD((1500, 1400), text=T('よく言われる説', '堀の土を積んだ', ts=80)),
 OLD((1450, 1350), text=T('よく言われる説', '掘る場所と積む場所が隣', ts=64)),
 CARD('数字で', '確かめられる資料がある。', fs=76),
 CARD('大林組の試算', '古代の工法で築いたら', kicker='1985年', fs=76),
 BUD(1), BUD(2), BUD(2), BUD(2), BUD(3), BUD(4),
 P('mozu_z15', DS, (4500, 6500), rings=[{'at': DS, 'm': 420, 'dashed': True, 'col': 'teal'}], text=T('古墳の外から', '半分近くの土を', ts=72)),
 CARD('200万m³の土は、', 'どれほどの重さか。'),
 CARD('土の重さは、', '種類や湿り気で変わる。', fs=76),
 CALC('仮に 1 m³ = 1.6 t とすると', [['200万 m³ × 1.6 t', '約320万 t']]),
 CALC('10トンのダンプカーなら', [['200万 m³ × 1.6 t', '約320万 t'], ['320万 t ÷ 10 t', '32万台分']], dt=.3),
 CARD('もっこ', kicker='当時の道具', fs=120),
 ROWS('もっこ', [('網や籠', '土を入れる'), ('2人で', '棒を担いで運ぶ', 1)]),
 CALC('仮に1回30キロとすると', [['1 m³ ＝ 1.6 t', '1600 kg'], ['1600 kg ÷ 30 kg', '50回以上']], dt=.5),
 CARD('それを、', '200万m³ぶん。', gold=1),
 CARD('運び方の手がかりは、', '日本書紀に。'),
 P('osaka_hill_z11', [34.55, 135.66], (75000, 55000), rings=[{'at': HS, 'r': 20, 'label': '纒向', 'sub': '奈良県桜井市'}, {'at': DS, 'r': 20, 'label': '大仙古墳', 'side': -1}]),
 {'layout': 'timeline', 'kicker': '築かれた時期', 'axis': [200, 500], 'step': 50, 'events': [{'y': 250, 'label': '纒向の巨大古墳', 'sub': '3世紀ごろ', 'side': 1}, {'y': 450, 'label': '大仙古墳', 'sub': '5世紀中頃', 'side': 1, 'hi': True}], 'spans': [{'from': 250, 'to': 450, 'label': 'およそ200年'}], 'bg': bg()},
 DOC('『日本書紀』崇神天皇十年条（書き下し）', ['是の墓は、', '日は人作り、', '夜は神作る。'], [1, 2], 70),
 DOC('『日本書紀』崇神天皇十年条（書き下し）', ['故、大坂山の', '石を運びて造る。'], [1], 58),
 P('osaka_hill_z11', [34.53, 135.72], (62000, 50000), rings=[{'at': OSY, 'r': 36, 'label': '大坂山（推定）', 'sub': '奈良と大阪の境のあたり', 'dashed': True, 'side': -1}, {'at': HS, 'r': 20, 'label': '纒向'}]),
 DOC('『日本書紀』崇神天皇十年条（書き下し）', ['山より墓に至るまで', '人民相踵ぎて', '手逓伝にして運ぶ。'], [2], 48),
 CARD('手から手へ。', sub='火事のときのバケツリレーのように'),
 CARD('古い記録に残る、', '数少ない具体的な場面。', fs=76),
 CARD('手で渡せない', '大きな石は？'),
 P('hajinosato_z17', [34.566, 135.6127], (1700, 1400), stamp='古市古墳群のあたり'),
 P('hajinosato_z17', [34.566, 135.6127], (1400, 1250), text=T('1978年 · 大阪府藤井寺市', '木のそり', None, None, '古墳の堀の底から', ts=96), stamp='古市古墳群のあたり'),
 {'layout': 'shura'}, {'layout': 'shura'}, {'layout': 'shura', 'small': True},
 DOTS('現地説明会', [{'n': 12000, 'label': '詰めかけた人 約1万2000人'}], per=100),
 P('konda_z16', KD, (3600, 3000), rings=[{'at': KD, 'm': 280, 'label': '古市古墳群', 'sub': '大阪府藤井寺市・羽曳野市'}]),
 ROWS('運ぶものと道具', [('土', 'もっこ'), ('小さな石', '手渡し'), ('大きな石', '修羅', 1)]),
 ROWS('運ぶものと道具', [('土', 'もっこ'), ('小さな石', '手渡し'), ('大きな石', '修羅', 1)]),
 MY(['solved', 'solved'], 1, 1),
 ROWS('2つ目の答え', [('土の半分', '堀から'), ('残り', 'よそから運び込む'), ('日本書紀', '列を作って運ぶ姿', 1)]),
 MY(['solved', 'solved']),
 # mystery 3
 CH('03', '何人で何年かかったのか'),
 CARD('大勢の民が、', '無理やり働かされた？'),
 CARD('ピラミッドの', '奴隷のようなイメージ。', fs=76),
 CARD('その見方が、', '変わってきている。'),
 ROWS('ピラミッドの発掘', [('ピラミッドのそば', '働いた人々の町の跡', 1)]),
 ROWS('ピラミッドの発掘', [('ピラミッドのそば', '働いた人々の町の跡'), ('パンを焼いた跡',), ('肉を食べていた跡',)]),
 CARD('奴隷ではなく、', '食事を与えられて働く人々。', fs=72),
 P('daisen_1960s_z16', DS, (1900, 1650), text=T('大林組の試算', '工事の姿', ts=88), stamp='1961〜69年撮影'),
 DOTS('いちばん忙しい時期', [{'n': 2000, 'label': '現場で働く人 1日 約2000人'}], per=25),
 DOTS('近くに住み込む人', [{'n': 3000, 'label': '全部で 約3000人', 'col': 'teal'}], per=25),
 DOTS('工事に関わった人', [{'n': 6000, 'label': '食事の支度なども含め 約6000人'}], per=25),
 CARD('何十万人ではなく、', '1つの町ほどの人数。', fs=76),
 OLD((2100, 1750)),
 OLD((1750, 1500)),
 CARD('6000人が働くには、', '6000人分の食べ物。', fs=76),
 CARD('計算してみる。', center=True),
 CALC('仮に1人1日3合とすると', [['1合', '約150 g'], ['150 g × 3合', '450 g']], dt=.6),
 CALC('米', [['450 g × 6000人', '約2.7 t'], ['2.7 t × 1年', '約1000 t']], dt=.8),
 CARD('土を運ぶ人だけでは、', '足りなかった。'),
 ROWS('欠かせなかったもの', [('田んぼ', '働く人たちを食べさせる'), ('仕組み', '米を集めて配る', 1)]),
 CARD('古墳の大きさは、', '村々の豊かさの大きさ。', gold=1, fs=76),
 CARD('現場には、', '専門の人々もいた。'),
 CARD('土師氏', kicker='古墳づくり・埴輪づくり', sub='はじし', fs=120),
 P('hajinosato_z17', [34.5665, 135.6127], (1500, 1300), text=T('今も残る地名', '土師ノ里', ts=110), stamp='大阪府藤井寺市'),
 P('hajinosato_z17', [34.5665, 135.6127], (1300, 1200), text=T('地名として今に', '土師ノ里', ts=110), stamp='大阪府藤井寺市'),
 CARD('道具も、', '大きく進歩していた。'),
 ROWS('5世紀ごろ', [('鋤・鍬', 'U字形の鉄の刃をつける', 1), ('広まった時期', '5世紀ごろ')]),
 ROWS('道具の違い', [('木だけの道具', '固い土には弱い'), ('鉄の刃', '固い土にも深く食い込む', 1)]),
 CARD('同じ人数でも、', '掘れる土が増えた。'),
 CARD('新しい鉄の技術は、', '海の向こうから。'),
 CARD('工事には、', '何年かかったのか。'),
 CARD('もう一度、', '計算してみる。'),
 P('daisen_z17', DS, (1600, 1450), outline=True, text=T('運ぶ土', None, '約200万', 'm³')),
 CALC('仮に1人1日1 m³とすると', [['200万 m³ ÷ 1 m³', 'のべ200万人']]),
 CALC('毎日2000人なら', [['200万人 ÷ 2000人', '1000日'], ['1000日', '約2年9か月']], dt=.7),
 CARD('1年中、', '工事だけをしていたわけではない。', fs=68),
 CARD('田植えや稲刈りの時期は、', '田んぼの仕事。', fs=76),
 CALC('工事ができるのが1年の3分の1なら', [['2年9か月 × 3', '8年以上']]),
 CARD('1人1日に運べる土が、', '半分の0.5 m³なら？', fs=76),
 CALC('運べる量が半分なら', [['8年以上 × 2', '16年以上']]),
 CARD('どの数字も、', 'あくまで仮の計算。'),
 ROWS('記録がないこと', [('1人1日に運べた量', '記録なし'), ('1年に働けた日数', '記録なし', 1)]),
 CARD('それでも、', '見えてくることがある。'),
 {'layout': 'timeline', 'kicker': '工事の年数（仮の計算）', 'axis': [0, 20], 'step': 2, 'events': [{'y': 2.75, 'label': '2年9か月', 'sub': '休みなし', 'side': 1}, {'y': 8, 'label': '8年以上', 'side': -1}, {'y': 16, 'label': '16年以上', 'side': 1, 'hi': True}], 'spans': [{'from': 10, 'to': 20, 'label': '10年を超える可能性が高い', 'hi': True}], 'bg': bg()},
 MY(['solved', 'solved', 'half'], 2, 2), MY(['solved', 'solved', 'half'], 2), MY(['solved', 'solved', 'half'], kicker='ここまでで 2つ半'),
 CARD('働いた人々についての', '3つの説。'),
 THEO(show=[0], hide=[1, 2]), THEO(show=[1], hide=[2]), THEO(show=[2]), THEO(show=[]),
 ROWS('合わせたい数字', [('人数', '数千人規模'), ('年月', '10年を超えるかも'), ('田んぼ', '仕事との折り合い', 1)]),
 THEO(show=[], hi=[1, 2]), THEO(show=[], hi=[1, 2]),
 CARD('進んで加わったのか、', '命じられたのか。', sub='どの記録にも書かれていない', fs=76),
 COMMENT('少しだけ、お願いがあります'),
 COMMENT('コメントを読んで、', '次に確かめるテーマを決めています'),
 COMMENT('確かめてほしいこと', '古墳のことでも、ほかの歴史の謎でも'),
 COMMENT('確かめてほしいこと', 'ぜひコメント欄で教えてください'),
 CARD('日本史と古代の謎を、', '記録と数字で。'),
 COMMENT('チャンネル登録', '次の動画を見逃さないように'),
 # mystery 4
 CH('04', 'なぜ崩れないのか'),
 P('daisen_z17', DS, (1300, 1150), outline=True),
 CARD('土の山は、', '本来とても崩れやすい。'),
 ROWS('土の山の弱点', [('雨', '土が流れる'), ('自分の重さ', '少しずつ沈む', 1)]),
 OLD((1400, 1250)),
 CARD('設計どおりに', '形を描き出す技。', kicker='秘密 1'),
 P('daisen_z17', DS, (1250, 1100), outline=True, text=T('上から見ると', 'ほぼ左右対称', ts=84)),
 CARD('500mを超える形を、', '目分量では整えられない。', fs=72),
 ROWS('考えられている方法', [('縄', '張って長さを測る'), ('杭', '打ちながら輪郭を写し取る', 1)]),
 P('daisen_z17', DS, (1150, 1050), outline=True, text=T('記録はない', '形が語る測量の技', ts=72)),
 CARD('土の積み方。', kicker='秘密 2'),
 SEC('layers', '墳丘の断面'),
 SEC('layers', '敷く → たたく → 固める', '繰り返す'),
 CARD('この技は、', '土塀や城の土台へ。'),
 SEC('terraces', '墳丘は3段', '理由があった'),
 SEC('terraces', '段ごとの平らな面', '土を運ぶ人の足場'),
 SEC('terraces', '完成したあと', '平らな面に埴輪'),
 SEC('terraces', '一気に積むより', '崩れにくい'),
 CARD('今の堤防や道路の盛り土も、', '同じ考え方。', fs=72),
 ROWS('今の盛り土の工程', [('薄く敷く',), ('機械で締め固める',), ('また敷く', '繰り返し', 1)]),
 CARD('機械の代わりに、', '人の手で。'),
 CARD('表面を覆う石。', kicker='秘密 3'),
 SEC('fukiishi', '斜面には', 'こぶし大の石'),
 SEC('fukiishi', '葺石（ふきいし）', '土を雨から守る'),
 CALC('葺石（大林組の試算）', [['葺石の数', '約536万個'], ['重さ', '約1万4000 t']], dt=.6, source=OB),
 CALC('人手（大林組の試算）', [['石集め ＋ 水路掘り', 'のべ17万人']], source=OB),
 CARD('石を集めるために、', '水路まで掘った。'),
 ROWS('石の運び方', [('川原の石', '舟に積んで水の上を', 1), ('人が担ぐ', 'ずっと大変')]),
 ROWS('運び方の使い分け', [('土', '人の肩で'), ('石', '水の上で', 1)]),
 ROWS('運び方の使い分け', [('土', '人の肩で'), ('石', '水の上で', 1)]),
 OLD((1500, 1300), text=T('完成したばかりの古墳', '石に覆われた山', ts=84)),
 P('sakai_hill_z13', [34.5642, 135.47], (17000, 12000), rings=[{'at': DS, 'r': 22, 'label': '大仙古墳'}], stamp='現在の地形（陰影起伏図）'),
 CALC('埴輪（大林組の試算）', [['埴輪', '約1万5000個']], source=OB),
 CARD('宮内庁と堺市が、', '初めて共同で発掘。', kicker='2018年', fs=76),
 ROWS('2018年の共同発掘', [('堤の部分', '埴輪の列'), ('', '石を敷いた跡', 1)]),
 MY(ALL, 3, 3),
 ROWS('崩れない理由', [('正確な設計',), ('薄い層で突き固めた土',), ('536万個の石', '', 1)]),
 # summary
 MY(ALL, kicker='まとめ'), MY(ALL, 0, kicker='まとめ'), MY(ALL, 1, kicker='まとめ'), MY(ALL, 2, kicker='まとめ'), MY(ALL, 3, kicker='まとめ'), MY(ALL, kicker='解けたのは 3つ'),
 CARD('何年かかったのか。', 'それだけは、まだ分からない。', fs=76),
 CARD('この結果の、', '弱いところ。'),
 weak(1, 0), weak(1, 0), weak(2, 1), weak(2, 1), weak(3, 2), weak(3, 2),
 CARD('墳丘の中は、', 'ほかの古墳から推し量るしかない。', fs=64),
 P('daisen_z17', DS, (1000, 900)),
 CARD('今ある記録と数字から、', '見えてくる姿。'),
 CARD('何十万人を無理やり、', '短い期間で — ではなかった。', fs=72),
 ROWS('最も筋が通る姿', [('人数', '数千人'), ('年月', '10年を超える'), ('田んぼ', '折り合いをつけながら', 1)]),
 CARD('土を運んで固め、', '石で覆っていった。'),
 P('sakai_hill_z13', [34.5642, 135.47], (15000, 10000), rings=[{'at': DS, 'r': 22, 'label': '堺の台地'}]),
 OLD((1700, 1450)),
 P('daisen_z17', DS, (1400, 1750)),
 CARD('ただの土の山では、', 'ない。'),
 CARD('数えきれない人々の、', '毎日の働き。', gold=1),
 P('mozu_z15', [34.5690, 135.4855], (3600, 2900), rings=[{'at': SK, 'r': 26, 'label': '堺市役所', 'sub': '21階 展望ロビー（位置は概略）', 'side': -1}, {'at': DS, 'm': 300, 'label': '大仙古墳'}]),
 P('mozu_z15', [34.5690, 135.4855], (2900, 4600), rings=[{'at': SK, 'r': 26}, {'at': DS, 'm': 300}]),
 CARD('あなたは、', '何年かかったと思いますか。', fs=76),
 COMMENT('数年？ それとも10年以上？', 'ぜひコメント欄で教えてください'),
 OLD((2400, 2700)),
]

lines = json.load(open('lines.json', encoding='utf-8'))
if len(S) != len(lines):
    sys.exit(f'✗ {len(S)} scenes for {len(lines)} sentences')
SAY = {'s122': lambda t: t.replace('米が必要', 'コメが必要')}
for s, l in zip(S, lines):
    for k in [k for k, v in s.items() if v is None]: s.pop(k)
    imgs = [s.get('img')] + ([s['bg']['img']] if s.get('bg') else [])
    imgs = [i for i in imgs if i]
    if 'source' not in s and imgs:
        s['source'] = '出典：国土地理院（' + '・'.join(dict.fromkeys(GSI[LAYER[i]] for i in imgs)) + '）'
    if l['id'] in SAY: s['say'] = SAY[l['id']](l['text'])
out = {'_about': 'One entry per sentence (same order as script.txt); generated by tools/make_scenes.py (Claude Code). Layouts: index.html L.*.',
       'title': '日本最大の古墳はどうやって築かれたのか', 'title_en': 'How Was Japan\'s Largest Tomb Built?', 'mysteries': MYS,
       'credits': ['地図・空中写真　出典：国土地理院（地理院タイル：シームレス空中写真・陰影起伏図・1945〜50年／1961〜69年の空中写真）',
                   '史料　『日本書紀』巻第五 崇神天皇十年条（書き下しによる翻刻）',
                   '数値　大林組の試算（1985）、宮内庁の3次元測量（2018）ほか（台本による）',
                   '音声　VOICEVOX:青山龍星',
                   '輪郭・断面・修羅の図は模式図、位置の一部は概略です。数値の一部は仮の計算です。'],
       'scenes': S}
json.dump(out, open('scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(S), 'scenes', dict(Counter(s['layout'] for s in S)))
