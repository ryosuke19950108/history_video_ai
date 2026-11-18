#!/usr/bin/env python3
"""Scene assignment for 日本人はどこから来たのか (handbook 11-3 step 2), written by Claude Code in the session.
One entry per sentence of script.txt, in order → scenes.json. Layouts: index.html `L.*` (map / stack are this film's additions)."""
import json, os, re, sys

# places (lat, lon); sites from the GSI place-name search (msearch.gsi.go.jp), marked 位置は概略 on screen where approximate
NOJ = [36.8323, 138.2094]; YON = [24.4559, 122.9877]; TWS = [24.49, 121.86]   # 野尻湖 立が鼻, 与那国島, 台湾の東海岸（出発地、概略）
ODAI = [41.0657, 140.5480]; SAN = [40.8131, 140.6974]; KAKI = [41.9285, 140.9450]
ITA = [33.5654, 130.4528]; NABA = [33.4484, 129.9579]; YOSHI = [33.3250, 130.3818]; DS = [34.5642, 135.4875]
OKI = [26.33, 127.80]; KINKI = [34.7, 135.5]; HOK = [43.3, 142.6]
GSI = {'seamlessphoto': '空中写真'}
LAYER = {k: 'seamlessphoto' for k in ('nojiri_z14', 'odai_z16', 'sannai_z17', 'kakinoshima_z16', 'itazuke_z17', 'nabatake_z17', 'yoshinogari_z16', 'daisen_z17', 'mozu_z15')}
PHOTO = {}   # filled from SOURCES.jsonl (Wikimedia Commons, public domain / CC0 only)
for l in open('SOURCES.jsonl', encoding='utf-8'):
    r = json.loads(l)
    if r['source'].startswith('Wikimedia'): PHOTO[r['name'].split('/')[-1].rsplit('.', 1)[0]] = r['credit'].replace('Public domain', 'パブリックドメイン')
NE = '出典：Natural Earth（地図データ、パブリックドメイン）'

# views of the drawn map: centre (lat, lon) and degrees of longitude across the frame
EA = {'c': [38, 127], 'w': 62}; EA2 = {'c': [37, 128], 'w': 48}; JP = {'c': [35, 134], 'w': 36}; JPN = {'c': [37, 135], 'w': 30}
SW = {'c': [24.3, 122.5], 'w': 5.2}; KR = {'c': [36.5, 128.5], 'w': 16}; NOR = {'c': [47.5, 139], 'w': 40}
REGV = {'c': [34.6, 134], 'w': 58}; ICE = NOR; LANGV = {'c': [33.5, 130], 'w': 54}; ROUTEV = {'c': [40, 132], 'w': 92}; KR2 = {'c': [35.2, 128.8], 'w': 14}; KINGV = {'c': [37, 128.5], 'w': 20}

def MAP(view, **kw): return {'layout': 'map', 'view': view, 'source': NE, **kw}
def P(img, at, span=(1500, 1350), **kw): return {'layout': 'photo', 'img': img, 'at': at, 'span': list(span), **kw}
def PH(img, at, span, **kw): return {'layout': 'photo', 'img': img, 'at': list(at) + [0], 'span': list(span), **kw}
def T(kicker=None, title=None, number=None, unit=None, caption=None, **kw): return {k: v for k, v in dict(kicker=kicker, title=title, number=number, unit=unit, caption=caption, **kw).items() if v is not None}
def CARD(*lines, bg=None, **kw): return {'layout': 'card', 'lines': list(lines), 'bg': bg, **kw}
def CH(num, title, sub, bg): return {'layout': 'chapter', 'num': num, 'title': title, 'sub': sub, 'bg': bg}
def MY(status=(), focus=None, reveal=None, kicker=None, bg=None): return {'layout': 'mysteries', 'status': list(status), 'focus': focus, 'reveal': reveal, 'kicker': kicker, 'bg': bg}
def BARS(kicker, items, bg=None, **kw): return {'layout': 'bars', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def CALC(kicker, rows, bg=None, **kw): return {'layout': 'calc', 'kicker': kicker, 'rows': rows, 'bg': bg, **kw}
def ROWS(kicker, rows, bg=None, **kw): return {'layout': 'rows', 'kicker': kicker, 'rows': [r if isinstance(r, dict) else {'k': r[0], 'v': r[1] if len(r) > 1 else '', 'hi': len(r) > 2} for r in rows], 'bg': bg, **kw}
def THEO(kicker, items, bg=None, **kw): return {'layout': 'theories', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def COMMENT(text, sub=None, bg=None): return {'layout': 'comment', 'text': text, 'sub': sub, 'bg': bg}
def DOC(doc, lines, hl, source, bg, fs=62): return {'layout': 'doc', 'doc': doc, 'lines': lines, 'hl': hl, 'fs': fs, 'source': source, 'bg': bg}
def B(img, at, span, a=.24): return {'img': img, 'at': at, 'span': span, 'a': a}

# backdrops by topic (aerials of the places named; the Kofun one is 大仙古墳 from the previous film)
BG_NOJ = B('nojiri_z14', NOJ, 6000, .24); BG_SAN = B('sannai_z17', SAN, 1600, .24); BG_ODAI = B('odai_z16', ODAI, 2800, .22)
BG_KAKI = B('kakinoshima_z16', KAKI, 2600, .22); BG_ITA = B('itazuke_z17', ITA, 1300, .22); BG_NABA = B('nabatake_z17', NABA, 1300, .22)
BG_YOSHI = B('yoshinogari_z16', YOSHI, 2600, .24); BG_PIT = B('sannai_pit', [960, 760, 0], 1900, .30); BG_TOWER = B('sannai_05', [900, 1250, 0], 2200, .28); BG_DOGU = B('sannai_dogu', [960, 720, 0], 1900, .26); BG_DS = B('daisen_z17', DS, 1900, .22); BG_MOZU = B('mozu_z15', DS, 5000, .22)
BG_THREE = B('three_peoples', [1200, 675, 0], 2400, .26); BG_TB = B('tb_syougaku', [960, 834, 0], 1920, .20); BG_GOG = B('dogu_goggle', [895, 840, 0], 1700, .26); BG_HEART = B('dogu_heart', [775, 700, 0], 1500, .26)
BG_SKULL = B('jomon_skull', [960, 1000, 0], 1920, .26); BG_ATT = B('yayoi_attire', [1250, 700, 0], 1300, .26); BG_YPIT = B('yoshi_pit', [960, 640, 0], 1920, .26)
BG_HANI = B('haniwa_warrior', [900, 700, 0], 1750, .22); BG_HANIW = B('haniwa_woman', [800, 640, 0], 1550, .24); BG_HANIF = B('haniwa_formal', [775, 640, 0], 1500, .24)

# the spine: three waves, each checked against DNA (mysteries layout, film-wide board below)
WAVES = ['縄文の人々', '弥生の人々', '古墳時代の人々']
OK1, OK2, OK3 = ['solved'], ['solved', 'solved'], ['solved', 'solved', 'solved']
# ancestry shares, Yamamoto et al. 2024 (Nature Communications 15: 9780), whole Biobank Japan
PARTS = [{'label': '縄文', 'sub': '狩りと採集', 'v': 12.4, 'text': '12.4%', 'c': 'gold'},
         {'label': '北東アジア系', 'sub': '弥生 · 米作り', 'v': 21.2, 'text': '21.2%', 'c': 'teal'},
         {'label': '東アジア系', 'sub': '古墳時代', 'v': 66.4, 'text': '66.4%', 'c': 'cream'}]
SRC24 = 'Yamamoto ほか（2024）Nature Communications'
def STACK(show=None, keep=None, **kw): return {'layout': 'stack', 'kicker': '今の日本人のDNA（17万1287人の平均）', 'parts': PARTS, 'show': show, 'keep': keep, 'src': SRC24, 'bg': None, **kw}
VILLAGE = {'layout': 'dots', 'kicker': '100人の村にたとえると', 'per': 1, 'cols': 25, 'gap': 54, 'r': 19, 'y0': 360, 'ly': 700, 'lgap': 430,
           'groups': [{'n': 12, 'label': '縄文 12人', 'col': 'gold'}, {'n': 21, 'label': '北東アジア 21人', 'col': 'teal'}, {'n': 66, 'label': '東アジア 66人', 'col': 'text'}]}
TL = {'layout': 'timeline', 'kicker': '列島の人々の年表', 'axis': [-40000, 0], 'step': 5000, 'fmt': 'ago'}
EVT = [{'y': -38000, 'label': '人が住み始める', 'sub': '約3万8000年前', 'side': 1}, {'y': -16000, 'label': '縄文時代', 'sub': '約1万6000年前〜', 'side': -1, 'hi': True},
       {'y': -3000, 'label': '弥生', 'sub': '約3000年前〜', 'side': 1}, {'y': -1700, 'label': '古墳', 'sub': '約1700年前〜', 'side': -1}]
TLB = {'layout': 'timeline', 'kicker': '弥生時代の始まり', 'axis': [-1200, 400], 'step': 200, 'fmt': 'bc'}
ROUTES3 = [{'pts': [[52.5, 141.5], [47.5, 142.6], [44.5, 142.2]], 'label': '北から', 'lat': [50.5, 143.5], 'col': 'cream', 'dashed': True},
           {'pts': [[37.0, 127.2], [35.3, 129.0], [34.2, 130.2]], 'label': '西から', 'lat': [37.6, 129.5], 'col': 'cream', 'dashed': True},
           {'pts': [[23.0, 121.1], [24.4, 122.9], [26.3, 127.7], [28.4, 129.5]], 'label': '南から', 'lat': [24.6, 126.0], 'col': 'cream', 'dashed': True}]
BRIDGE = [{'pts': [[44.0, 142.3], [45.6, 142.0], [47.5, 142.5], [51.5, 141.9], [52.3, 141.3], [53.0, 140.6]], 'col': 'gold', 'wd': 22, 'label': '陸続き（模式図）', 'lat': [48.5, 143.6]}]
KURO = [{'pts': [[20.5, 121.8], [22.5, 121.6], [24.0, 122.3], [25.2, 123.6], [26.5, 125.6]], 'col': 'teal', 'wd': 6, 'dashed': True, 'label': '黒潮', 'lat': [21.6, 122.2], 'noarrow': False, 't': .2, 'dur': 2.2}]
CANOE = {'pts': [TWS, [24.47, 122.4], YON], 'col': 'gold', 'wd': 5, 'label': '200 km超', 'lat': [24.62, 122.25], 'al': 'center', 't': .5, 'dur': 2.4}
NEA = {'at': [47, 128], 'rx': 10, 'ry': 6.5, 'col': 'teal', 'label': '北東アジア', 'ly': -20}
CEA = {'at': [32, 113], 'rx': 8, 'ry': 5.5, 'col': 'cream', 'label': '東アジア（中国の中心部）', 'ly': 0, 'ls': 30}
KINGS = [{'at': [40.3, 126.2], 'label': '高句麗', 'c': 'text', 'ls': 34}, {'at': [36.3, 126.9], 'label': '百済', 'c': 'text', 'ls': 34},
         {'at': [36.0, 129.1], 'label': '新羅', 'c': 'text', 'ls': 34}, {'at': [35.0, 128.0], 'label': '加耶', 'c': 'text', 'ls': 30}]
SITES_J = [{'at': ODAI, 'label': '大平山元遺跡', 'sub': '約1万6500年前の土器', 'side': -1, 'col': 'gold'}, {'at': SAN, 'label': '三内丸山遺跡', 'sub': '約5900年前〜', 'side': 1, 'col': 'gold'},
           {'at': KAKI, 'label': '垣ノ島遺跡', 'sub': '約9000年前の漆', 'side': 1, 'col': 'gold'}]
REG = lambda show: [p for i, p in enumerate([{'at': OKI, 'label': '沖縄', 'sub': '26.1%', 'big': 1, 'ss': 44, 'sc': 'gold', 'side': 1, 'col': 'gold', 'r': 12},
                                             {'at': KINKI, 'label': '近畿', 'sub': '9.8%', 'big': 1, 'ss': 44, 'sc': 'text', 'side': -1, 'col': 'teal', 'r': 12},
                                             {'at': HOK, 'label': '北海道のアイヌの人々', 'sub': '縄文の流れが特に濃い', 'side': -1, 'col': 'gold', 'r': 12}]) if i in show]
WEAK = [('弱点 1', '古い時代の人のゲノムが少ない'), ('弱点 2', '3つは大きな流れの整理'), ('弱点 3', '日本語の起源は分からない')]
def weak(n, hi): return ROWS('この結論の弱いところ', [(k, v, True) if i == hi else (k, v) for i, (k, v) in enumerate(WEAK[:n])], bg=[BG_SKULL, BG_THREE, None][hi])
SRC21 = 'Cooke ほか（2021）Science Advances'
DNAQ = 'DNAで確かめた2つの研究'
STUDIES = THEO(DNAQ, [{'k': '2021年9月', 'name': '古い時代の人\n12人のゲノム', 'sub': 'Science Advances'}, {'k': '2024年11月', 'name': '今の日本人\n17万1287人', 'sub': 'Nature Communications'}], bg=None)

S = [
 # ── hook (paragraphs 0-5)
 STACK(show=[0], kicker='あなたのDNAのうち'),
 STACK(show=[0], keep=[0], kicker='17万人を超える日本人のDNAから', note='住む地域によって、割合は2倍以上ちがう'),
 THEO('学校で習った日本人の成り立ち', [{'k': 'もとから列島に', 'name': '縄文人'}, {'k': '大陸から来た', 'name': '弥生人'}], bg=BG_TB),
 CARD('その答えが、', '書き換わろうとしている。', bg=BG_YOSHI),
 STUDIES,
 CARD('教科書にほとんどない、', '3つ目の流れ。', gold=1, bg=BG_TB),
 COMMENT('あなたの予想は？', '動画を見る前に、コメント欄へ一言', bg=BG_THREE),
 CARD('今の日本人のDNAで', 'いちばん多いのは？', bg=BG_THREE),
 THEO('どの時代に来た人々？', [{'k': 'A', 'name': '縄文時代'}, {'k': 'B', 'name': '弥生時代'}, {'k': 'C', 'name': 'もっと後の\n時代'}], bg=BG_THREE),
 CARD('最後に、', '答え合わせ。', bg=BG_THREE),
 # ── the first people (6-14)
 MAP(JPN, kicker=None, text=T('列島に人がやって来た', None, None, None, None)),
 dict(TL, events=EVT[:1]),
 MAP(ICE, bands=BRIDGE, note='氷河の時代 · 海面は今よりずっと低かった'),
 P('nojiri_z14', NOJ, (5200, 4400), rings=[{'at': NOJ, 'r': 30, 'label': '野尻湖', 'sub': '長野県信濃町（立が鼻遺跡）', 'side': 1}], text=T('湖の底から', None, None, None, 'ナウマンゾウの化石')),
 P('nojiri_z14', NOJ, (4200, 3500), rings=[{'at': NOJ, 'r': 30, 'label': '野尻湖', 'sub': '長野県信濃町（立が鼻遺跡）', 'side': 1}], text=T('その近くから', '石の道具', ts=84)),
 MAP(NOR, bands=BRIDGE, places=[{'at': HOK, 'label': '北海道', 'side': -1, 'col': 'gold'}, {'at': [50.5, 142.7], 'label': 'サハリン', 'side': 1, 'col': 'gold'}]),
 MAP(KR2, places=[{'at': [36.3, 127.8], 'label': '朝鮮半島', 'side': -1, 'col': 'dim', 'r': 1}, {'at': [34.3, 132.0], 'label': '本州', 'side': 1, 'col': 'dim', 'r': 1}],
     regions=[{'at': [34.4, 129.4], 'rx': 1.3, 'ry': .9, 'col': 'teal', 'label': '海が残った', 'ly': -70}]),
 CARD('3万年以上前の人々に、', '海を渡れたのか。', bg=BG_NOJ),
 CARD('実際に確かめた、', '大がかりな実験。', bg=BG_NOJ),
 MAP(SW, places=[{'at': TWS, 'label': '台湾', 'side': -1, 'col': 'gold'}], text=T('2019年7月 · 国立科学博物館など', '丸木舟で海へ', ts=80)),
 MAP(SW, places=[{'at': TWS, 'label': '台湾', 'side': -1, 'col': 'gold'}, {'at': YON, 'label': '与那国島', 'sub': '沖縄県', 'side': 1, 'col': 'gold'}], routes=[CANOE]),
 MAP(SW, places=[{'at': TWS, 'label': '台湾', 'side': -1, 'col': 'gold'}, {'at': YON, 'label': '与那国島', 'sub': '沖縄県', 'side': 1, 'col': 'gold'}], routes=[dict(CANOE, t=0, dur=.01)] + KURO),
 ROWS('頼りにしたもの', [('地図', 'なし'), ('コンパス', 'なし'), ('星と太陽', 'だけ', True)], bg=None),
 ROWS('試された舟', [('草を束ねた舟', '進めず'), ('竹のいかだ', '進めず')], bg=None),
 ROWS('試された舟', [('草を束ねた舟', '進めず'), ('竹のいかだ', '進めず'), ('丸木舟', '石の斧でくり抜く', True)], bg=None),
 MAP(SW, places=[{'at': TWS, 'label': '台湾', 'side': -1, 'col': 'gold'}, {'at': YON, 'label': '与那国島', 'sub': '約45時間で到着', 'side': 1, 'col': 'gold', 'sc': 'gold'}], routes=[dict(CANOE, t=0, dur=.01)]),
 CARD('3万年前の人々にも、', '南の海を越えられた。', gold=1, bg=BG_NOJ),
 MAP(ROUTEV, routes=ROUTES3),
 MY([], kicker='列島に流れ込んだ3つの波', bg=BG_THREE),
 MY([], kicker='日本人のルーツは、いくつの流れ？', bg=BG_THREE),
 CH('01', '縄文の人々', '1つ目の波', BG_GOG),
 # ── wave 1: Jomon (16-32)
 dict(TL, events=EVT[:2]),
 PH('sannai_pit', [960, 760], (1700, 1500), stamp='三内丸山遺跡（復元）', text=T('縄文の暮らし', '狩り・漁・木の実', ts=84)),
 P('odai_z16', ODAI, (2600, 2200), rings=[{'at': ODAI, 'r': 34, 'label': '大平山元遺跡', 'sub': '青森県外ヶ浜町（位置は概略）', 'side': 1}], text=T('土器のかけら', None, '約1万6500', '年前', None, ns=104)),
 P('odai_z16', ODAI, (2200, 1900), rings=[{'at': ODAI, 'r': 34, 'label': '大平山元遺跡', 'sub': '青森県外ヶ浜町（位置は概略）', 'side': 1}], text=T('世界でも', '最も古い時期の土器', ts=72)),
 P('sannai_z17', SAN, (1500, 1250), rings=[{'at': SAN, 'r': 60, 'label': '三内丸山遺跡', 'sub': '青森市', 'side': 1}], text=T('大きな集落', None, '約5900', '年前から', '1700年ほど続いた', ns=104)),
 THEO('巨大な建物の跡', [{'k': '柱', 'name': '栗の柱\n6本'}, {'k': '柱の太さ', 'name': '直径\n約1m'}, {'k': '伝えるもの', 'name': '暮らしの\n豊かさ'}], bg=BG_PIT),
 P('kakinoshima_z16', KAKI, (2400, 2000), rings=[{'at': KAKI, 'r': 40, 'label': '垣ノ島遺跡', 'sub': '北海道函館市（位置は概略）', 'side': 1}], text=T('漆を使った品', None, '約9000', '年前', None, ns=104)),
 CARD('木の樹液から、', '塗料を作る技。', bg=BG_KAKI),
 CARD('縄文人は、', 'どこから来たのか。', bg=BG_TOWER),
 THEO('骨や顔の形からの説', [{'k': '説 1', 'name': '南の人々に\n近い'}, {'k': '説 2', 'name': '北の人々に\n近い'}], bg=BG_TOWER),
 CARD('DNAで答えを出した、', '2021年9月の研究。', gold=1),
 ROWS('2021年の研究チーム', [('トリニティカレッジダブリン', 'アイルランド'), ('金沢大学', '日本'), ('ほか', '')]),
 ROWS('2021年の研究', [('発表', 'Science Advances（アメリカ）', True)]),
 ROWS('2021年の研究', [('発表', 'Science Advances（アメリカ）'), ('新たに読み解いた', '12人分のゲノム', True), ('時代', '縄文〜古墳時代')]),
 CARD('世界の人々のDNAと比べ、', 'どれだけ似ているか。'),
 CARD('似ている度合いから、', 'いつ分かれたかが見える。'),
 CARD('ゲノム ＝', '体の設計図の情報のすべて。', gold=0),
 PH('jomon_skull', [1000, 1000], (1700, 1500), stamp='縄文時代の人の頭骨（伊川津貝塚）', text=T('耳の奥の固い骨に、', 'DNAが残っていた', ts=72)),
 CARD('わずかなかけらを', '1つずつつなぎ合わせる。'),
 CARD('縄文人について、', '驚くような事実。', bg=BG_HEART),
 dict(TL, kicker='縄文人の祖先', events=[{'y': -20000, 'label': '大陸の人々と分かれる', 'sub': '約2万〜1万5000年前', 'side': 1, 'hi': True}], spans=[{'from': -20000, 'to': -15000, 'label': '', 'hi': True}], source='出典：' + SRC21),
 P('sannai_z17', SAN, (1800, 1500), text=T('何千年ものあいだ', None, '約1000', '人', '保たれた集団の規模（推定）', ns=120), source='出典：' + SRC21),
 CARD('子どもを残す世代の人数を、', '遺伝の計算から見積もった数。', fs=70),
 CALC('今の日本と比べると', [('1億2000万人 ÷ 1000人', '12万'), ('', '12万ぶんの1', True)], bg=BG_SAN),
 CARD('縄文時代の人口も、', '多くはなかった。', bg=BG_SAN),
 MAP(JPN, text=T('縄文時代の中ごろ · 小山修三さんの推定', None, '約26万', '人', '列島全体の人口', ns=120)),
 MAP(JPN, regions=[{'at': [37.5, 138.5], 'rx': 10, 'ry': 7, 'col': 'gold', 'label': '外とほとんど混ざらずに', 'ly': -230}]),
 CARD('世界のどの集団とも違う、', 'とても独特なDNA。', gold=1, bg=BG_GOG),
 MY([], focus=0, bg=BG_THREE),
 MAP(EA2, regions=[{'at': [38, 138], 'rx': 9, 'ry': 7, 'col': 'gold', 'label': '列島で独自の道', 'ly': -200}], note='約2万年前に大陸の人々と分かれた'),
 MY(OK1, focus=0, reveal=0, bg=BG_THREE),
 MAP(ROUTEV, routes=ROUTES3, text=T('縄文の祖先は', 'どの道から？', ts=80)),
 CARD('DNAも、', 'まだ答えを出していない。', bg=BG_HEART),
 CARD('今の大陸のどの集団にも、', 'きれいには結びつかない。', bg=BG_SKULL),
 MAP(ROUTEV, routes=ROUTES3, regions=[{'at': [38, 138], 'rx': 9, 'ry': 7, 'col': 'gold', 'label': '列島の中で混ざり合った？', 'ly': -200}]),
 CH('02', '弥生の人々', '2つ目の波', BG_ATT),
 # ── wave 2: Yayoi (33-46)
 MAP(KR2, places=[{'at': ITA, 'label': '九州の北部', 'side': 1, 'col': 'gold'}], text=T('約3000年前から', '田んぼで米作り', ts=80)),
 MAP(KR2, routes=[{'pts': [[36.6, 126.8], [35.2, 128.6], [33.9, 130.0]], 'col': 'teal', 'label': '海を渡って', 'lat': [34.6, 128.2], 'al': 'right', 'lx': -20}], places=[{'at': ITA, 'label': '九州の北部', 'side': 1, 'col': 'gold'}]),
 P('itazuke_z17', ITA, (1400, 1150), rings=[{'at': ITA, 'r': 60, 'label': '板付遺跡', 'sub': '福岡市', 'side': 1}], text=T('日本で最も古い時期の水田', None, None, None, None)),
 P('nabatake_z17', NABA, (1300, 1100), rings=[{'at': NABA, 'r': 50, 'label': '菜畑遺跡', 'sub': '佐賀県唐津市', 'side': 1}], text=T('水路やあぜ道まで', '本格的な田んぼ', ts=80)),
 P('yoshinogari_z16', YOSHI, (2600, 2200), text=T('深い堀で囲んだ', '大きな村', ts=84)),
 PH('yoshinogari_photo', [960, 560], (1500, 1300), stamp='吉野ヶ里遺跡（佐賀県・復元）'),
 CARD('弥生の始まりにも、', '大きな見直し。', bg=BG_YPIT),
 ROWS('2003年 · 国立歴史民俗博物館', [('調べたもの', '土器についた焦げなど'), ('方法', '最新の年代測定', True)], bg=BG_YOSHI),
 dict(TLB, events=[{'y': -1000, 'label': '紀元前10世紀ごろ', 'sub': '新しい研究', 'side': 1, 'hi': True}]),
 dict(TLB, events=[{'y': -1000, 'label': '紀元前10世紀ごろ', 'sub': '新しい研究', 'side': 1, 'hi': True}, {'y': -500, 'label': 'それまでの見方', 'sub': '約500年あと', 'side': -1}], spans=[{'from': -1000, 'to': -500, 'label': '500年ほど早まる', 'hi': True}]),
 CARD('米作りは、', 'ゆっくり広がっていった。', bg=BG_YPIT),
 THEO('日本人の成り立ち', [{'k': 'もとから列島に', 'name': '縄文人'}, {'k': '弥生時代に大陸から', 'name': '渡来した\n人々'}], bg=BG_ITA),
 CARD('二重構造モデル', '長く定説とされた考え方。', gold=0, bg=BG_ITA),
 ROWS('二重構造モデル', [('唱えた人', '人類学者 埴原和郎さん'), ('年', '1991年', True)], bg=BG_ITA),
 CARD('骨の形の違いを、', '数字にして比べた。', bg=BG_SKULL),
 P('itazuke_z17', ITA, (1700, 1450), text=T('弥生〜古墳時代の1000年ほどで', None, '100万', '人規模', '大陸から渡ってきた人々（埴原さんの見積もり）', ns=120)),
 CARD('当時としては、', '驚くほど大きな数字。', bg=BG_ITA),
 CARD('渡来した人々の流れが、', '日本人の大部分。', gold=1, bg=BG_ATT),
 CARD('大規模な渡来は、', '方向としては正しかった。', bg=BG_ATT),
 CARD('日ごろ感じてきたことと', '重なる考え方。', bg=BG_ATT),
 THEO('よく言われてきた顔立ちの2つの型', [{'k': '型 1', 'name': '目鼻立ちの\nはっきりした顔'}, {'k': '型 2', 'name': '平らで\nすっきりした顔'}], bg=BG_THREE),
 THEO('よく言われてきた顔立ちの2つの型', [{'k': '型 1', 'name': '目鼻立ちの\nはっきりした顔', 'sub': '縄文の流れ'}, {'k': '型 2', 'name': '平らで\nすっきりした顔', 'sub': '弥生の流れ'}], bg=BG_THREE),
 CARD('DNAは、二重構造モデルを', '裏づけたのか。', fs=70, bg=BG_ITA),
 ROWS('2021年の研究', [('調べた時代', '弥生時代の人々も', True)], bg=BG_ATT),
 MAP(EA, regions=[NEA], routes=[{'pts': [[44, 128], [39, 127], [35.3, 128.8], [33.9, 130.1]], 'col': 'teal', 'dashed': True, 'noarrow': False, 't': 1.0}], text=T('弥生の人々の祖先', '縄文 ＋ 北東アジア', ts=72)),
 MAP(EA, regions=[dict(NEA, label='中国の東北部 · ロシアの極東')], names=[{'at': [45.5, 127], 'label': '', 'c': 'dim'}]),
 MAP(EA, regions=[NEA], routes=[{'pts': [[44, 128], [39, 127], [35.3, 128.8], [33.9, 130.1]], 'col': 'teal', 'label': '米作りとともに', 'lat': [33.0, 127.6], 'al': 'right', 't': .3}]),
 THEO('二重構造モデルの2つの流れ', [{'k': '縄文', 'name': '縄文の\n人々'}, {'k': '弥生', 'name': '北東アジアの\n流れ'}], hi=[0, 1], bg=BG_ITA),
 MY(OK2, focus=1, reveal=1, bg=BG_THREE),
 CH('03', '古墳時代の人々', '3つ目の波', BG_HANI),
 # ── wave 3: Kofun (47-59)
 dict(TL, events=EVT),
 P('daisen_z17', DS, (1700, 1300), text=T('前回の動画', '大仙古墳', ts=84, caption=None)),
 MAP(JP, places=[{'at': [33.6, 130.6], 'label': '九州', 'side': -1, 'col': 'gold'}, {'at': DS, 'label': '前方後円墳', 'side': 1, 'col': 'gold'}, {'at': [38.3, 140.9], 'label': '東北', 'side': 1, 'col': 'gold'}]),
 PH('haniwa_woman', [760, 760], (1520, 1300), stamp='埴輪（古墳時代）', text=T('この時代の人々のDNAに、', '3つ目の祖先', ts=72)),
 MAP(EA, regions=[dict(NEA, label='北東アジア'), CEA], places=[{'at': [36.5, 137.5], 'label': '縄文', 'side': 1, 'col': 'gold', 'lc': 'gold', 'r': 1}]),
 MAP(EA, regions=[CEA], routes=[{'pts': [[33.5, 120.5], [35.3, 124.5], [35.8, 127.5], [34.6, 129.6], [34.3, 132.5]], 'col': 'cream', 'label': '東アジアの流れ', 'lat': [37.6, 123.0], 't': .3}]),
 THEO('研究チームの結論 · 3つの段階', [{'k': '1', 'name': '縄文'}, {'k': '2', 'name': '弥生'}, {'k': '3', 'name': '古墳時代'}], bg=BG_THREE),
 THEO('研究チームの結論 · 3つの段階', [{'k': '1', 'name': '縄文', 'sub': '狩りと採集'}, {'k': '2', 'name': '弥生', 'sub': '米作り'}, {'k': '3', 'name': '古墳時代', 'sub': '国のまとまり'}], bg=BG_THREE),
 CARD('三重構造モデル', '新しい考え方。', gold=0, bg=BG_THREE),
 CARD('「まったく新しい', '3つの層のモデル」', sub='研究チームの1人', bg=BG_THREE),
 CARD('人の流れは、', '日本書紀にも。', bg=BG_HANIF),
 DOC('『日本書紀』応神天皇十四年条', ['是歳、弓月君', '自百済来帰。', '臣領己国之人夫', '百廿県而帰化。'], [0, 3], '史料：『日本書紀』巻第十 応神天皇十四年条（原文・新字体）', BG_HANIF, fs=52),
 ROWS('弓月君', [('のちの子孫とされる', '秦氏', True), ('知られた技', '機織りなど')], bg=BG_HANIF),
 CARD('どこまで本当の出来事か、', '今となっては分からない。', bg=BG_HANIF),
 MAP(KINGV, names=KINGS, note='当時の朝鮮半島 · 国々が並び立ち、争う'),
 MAP(KINGV, names=KINGS, routes=[{'pts': [[35.4, 128.6], [34.8, 129.3], [34.4, 129.9]], 'col': 'cream', 'label': '海を渡った人々', 'lat': [35.3, 130.0], 'al': 'left', 't': .3}]),
 ROWS('新しく伝わったもの', [('鉄の刃をつけた道具', '前回の動画')], bg=BG_HANI),
 ROWS('新しく伝わったもの', [('鉄の刃をつけた道具', '前回の動画'), ('須恵器', '登り窯で高い温度で焼く灰色の器', True)], bg=BG_HANI),
 ROWS('新しく伝わったもの', [('鉄の刃をつけた道具', '前回の動画'), ('須恵器', '登り窯で高い温度で焼く灰色の器'), ('馬に乗る文化', '古墳時代', True)], bg=BG_HANI),
 ROWS('新しく伝わったもの', [('鉄の刃をつけた道具', '前回の動画'), ('須恵器', '登り窯で高い温度で焼く灰色の器'), ('馬に乗る文化', 'くつわ · あぶみなどの馬具', True)], bg=BG_HANI),
 ROWS('新しく伝わったもの', [('鉄の刃をつけた道具', '前回の動画'), ('須恵器', '登り窯で高い温度で焼く灰色の器'), ('馬に乗る文化', 'くつわ · あぶみなどの馬具'), ('文字の文化', 'この頃とされる', True)], bg=BG_HANI),
 DOC('『古事記』応神天皇の段', ['貢上人名', '和邇吉師、', '即論語十巻、', '千字文一巻、'], [1, 2, 3], '史料：『古事記』中巻 応神天皇の段（原文・新字体）', BG_HANIF, fs=56),
 CARD('新しい技術は、', '海を渡った人々とともに。', bg=BG_HANI),
 THEO('ぴたりと重なる', [{'k': '言い伝え', 'name': '日本書紀'}, {'k': 'ゲノム', 'name': 'DNAが示した\n3つ目の流れ'}], hi=[0, 1], bg=BG_THREE),
 MY(OK3, focus=2, reveal=2, bg=BG_THREE),
 MY(OK3, kicker='日本人のルーツは 3つの流れ', bg=BG_THREE),
 # ── channel (60-62)
 COMMENT('少しだけ、お願いがあります', bg=BG_SAN),
 CARD('コメントを読んで、', '次のテーマを決めています。', bg=BG_SAN),
 CARD('日本人のルーツでも、', 'ほかの歴史の謎でも。', bg=BG_SAN),
 COMMENT('確かめてほしいことは？', 'ぜひコメント欄で教えてください', bg=BG_SAN),
 CARD('日本史と古代の謎を、', '記録と数字で。', bg=BG_YOSHI),
 CARD('チャンネル登録を、', 'ぜひ。', bg=BG_YOSHI),
 # ── the answer (63-71)
 CARD('冒頭の予想の、', '答え合わせ。', gold=1, bg=BG_THREE),
 THEO('いちばん多いのは、どの波？', [{'k': '1', 'name': '縄文'}, {'k': '2', 'name': '弥生'}, {'k': '3', 'name': '古墳時代'}], bg=BG_THREE),
 STUDIES | {'hi': [1]},
 ROWS('2024年の研究', [('チーム', '大阪大学 · トリニティカレッジダブリンなど'), ('発表', 'Nature Communications（イギリス）', True)]),
 THEO('2つの研究のちがい', [{'k': '2021年', 'name': '遺跡の\n古い時代の人'}, {'k': '2024年', 'name': '今を生きる\n私たち'}], hi=[0]),
 THEO('2つの研究のちがい', [{'k': '2021年', 'name': '遺跡の\n古い時代の人'}, {'k': '2024年', 'name': '今を生きる\n私たち', 'sub': '桁違いの人数'}], hi=[1]),
 ROWS('バイオバンクジャパン', [('目的', '病気の研究'), ('集め始め', '2003年 · 全国の医療機関の協力')]),
 ROWS('バイオバンクジャパン', [('目的', '病気の研究'), ('集め始め', '2003年 · 全国の医療機関の協力'), ('調べた人数', '17万1287人', True)]),
 ROWS('比べたもの', [('今の日本人', '17万1287人'), ('古い時代の人のゲノム', '22人分', True)]),
 STACK(show=[0]),
 STACK(show=[0], keep=[0], note='＝ およそ8ぶんの1'),
 STACK(show=[0, 2], keep=[0]),
 STACK(show=[0, 2, 1], keep=[0, 2], note='3つを合わせて100%'),
 VILLAGE,
 CARD('多くの人にとって、', '意外な結果。', bg=BG_THREE),
 THEO('いちばん多かったのは', [{'k': '1', 'name': '縄文', 'sub': '12.4%', 'dashed': True}, {'k': '2', 'name': '弥生', 'sub': '21.2%', 'dashed': True}, {'k': '3', 'name': '古墳時代', 'sub': '66.4%'}], hi=[2], bg=BG_THREE),
 THEO('いちばん多かったのは', [{'k': '1', 'name': '縄文', 'sub': '12.4%', 'dashed': True}, {'k': '2', 'name': '弥生', 'sub': '21.2%', 'dashed': True}, {'k': '3', 'name': '古墳時代', 'sub': '正解'}], hi=[2], bg=BG_THREE),
 CARD('縄文は、', 'いちばん古い源流。', bg=BG_DOGU),
 CARD('いちばん多く受け継いだのは、', '海を渡ってきた人々。', fs=70, gold=1, bg=BG_HANIW),
 # ── reading the result (72-84)
 CARD('ここで1つ、', '誤解しやすい点。', bg=BG_THREE),
 CARD('東アジア系・北東アジア系は、', '今の国や民族の名前ではない。', fs=66),
 CARD('何千年も前の祖先の集団を、', 'DNAの特徴で分けた呼び名。', fs=66),
 CARD('今のどこかの国の人々が、', 'そのまま祖先ではない。', fs=70),
 MAP(REGV, kicker=None, text=T('地域による違い', None, None, None, None)),
 MAP(REGV, places=REG([0, 1]), note='縄文由来の割合（2024年の研究）'),
 BARS('縄文由来の割合', [{'label': '沖縄', 'value': 26.1, 'text': '26.1%', 'hi': True}, {'label': '近畿', 'value': 9.8, 'text': '9.8%', 'col': 'teal'}], max=30, note='その差 およそ2.6倍 · ' + SRC24),
 MAP(REGV, places=REG([0]), regions=[{'at': [26.4, 127.9], 'rx': 2.2, 'ry': 1.6, 'col': 'gold', 'label': '流れが届くのが遅かった', 'ly': -95}]),
 MAP(REGV, places=REG([1]), regions=[{'at': [34.8, 135.6], 'rx': 2.4, 'ry': 1.7, 'col': 'teal', 'label': '古墳時代の国の中心', 'ly': -110}]),
 CARD('割合の違いに、', '土地の歴史が映る。', bg=BG_YOSHI),
 MAP(REGV, places=REG([0, 1, 2]), note='縄文由来の割合（2024年の研究）'),
 MAP(REGV, places=REG([0, 2]), regions=[{'at': [43.3, 142.6], 'rx': 3.5, 'ry': 2.3, 'col': 'gold'}, {'at': [26.4, 127.9], 'rx': 2.2, 'ry': 1.6, 'col': 'gold'}], note='北と南の端に、縄文の流れが濃く'),
 MAP(REGV, regions=[{'at': [34.8, 135.0], 'rx': 3.5, 'ry': 2.5, 'col': 'cream', 'label': '真ん中から少しずつ', 'ly': -120}], routes=[{'pts': [[34.8, 136], [37.5, 139.5], [40.5, 141]], 'col': 'cream', 't': .5}, {'pts': [[34.2, 134], [32.5, 130.8], [30.5, 130.5]], 'col': 'cream', 't': .8}]),
 CARD('体質についても、', '1つの傾向。', bg=BG_SKULL),
 CARD('縄文由来の割合が高い人ほど、', '体格の数値がやや高い。', fs=70),
 CARD('なぜそうなるのかは、', 'まだ分かっていない。'),
 CARD('ここで、', '大切なこと。', bg=BG_THREE),
 CARD('優れている・劣っている、', 'はまったくない。', gold=1, bg=BG_THREE),
 THEO('3つの流れ', [{'k': '1', 'name': '縄文'}, {'k': '2', 'name': '弥生'}, {'k': '3', 'name': '古墳時代'}], hi=[0, 1, 2], bg=BG_THREE),
 CARD('どれか1つでも欠けたら、', '今の私たちはいない。', bg=BG_THREE),
 CARD('もう1つ、', '大切なこと。', bg=BG_SAN),
 CARD('追い出して', '入れ替わったのではない。', gold=1, bg=BG_SAN),
 STACK(show=[0], kicker='もし入れ替わっていたなら', note='縄文のDNAは、ほとんど残っていないはず'),
 STACK(show=[0], kicker='実際には', note='17万人のほぼ全員に、縄文の流れ'),
 CARD('隣り合って暮らし、', '家族になり、混ざり合った。', bg=BG_YOSHI),
 CARD('静かな歴史を、', '確かな数字として。', bg=BG_YOSHI),
 # ── summary (85-88)
 MY(OK3, kicker='ここまでの結果', bg=BG_THREE),
 MY(OK3, focus=0, kicker='1つ目の波 · 縄文', bg=BG_THREE),
 MY(OK3, focus=1, kicker='2つ目の波 · 弥生', bg=BG_THREE),
 STACK(show=[0, 1, 2], keep=[0, 1, 2], kicker='3つ目の波 · 古墳時代', note='今の日本人のDNAの、3ぶんの2近く'),
 CARD('2つではなく、', '3つの流れ。', gold=1, bg=BG_THREE),
 CARD('今ある研究から', '見えてくる答え。', bg=BG_THREE),
 THEO('教科書の日本人の成り立ち', [{'k': 'これまで', 'name': '2つの流れ'}, {'k': 'DNAの研究から', 'name': '3つの流れ'}], hi=[1], bg=BG_TB),
 CARD('物語に、', '新しい1章。', bg=BG_TB),
 weak(0, -1) | {'kicker': 'この結論の弱いところ'},
 # ── weaknesses (89-93)
 weak(1, 0),
 ROWS('調べられた古い時代の人のゲノム', [('2021年の研究', '12人分'), ('2024年の研究', '22人分', True)], bg=BG_SKULL),
 ROWS('2024年の研究のDNA', [('集めた場所', '病院に通う人々', True)], bg=None),
 ROWS('2024年の研究のDNA', [('集めた場所', '病院に通う人々'), ('日本人全体', 'そのまま映すとは限らない', True)], bg=None),
 CARD('調べが進めば、', '細かいところは変わるかも。', bg=BG_YPIT),
 CARD('研究は、', 'まだ始まったばかり。', bg=BG_YPIT),
 weak(2, 1),
 MAP(EA2, routes=[{'pts': [[37.0, 127.0], [35.3, 128.9], [33.9, 130.2]], 'col': 'cream', 't': .2, 'dur': .9}, {'pts': [[36.6, 126.4], [35.0, 128.2], [33.6, 130.0]], 'col': 'teal', 't': .7, 'dur': .9}, {'pts': [[35.8, 126.6], [34.6, 128.0], [33.4, 129.8]], 'col': 'cream', 't': 1.2, 'dur': .9}],
     text=T('1度にまとめてではなく', '何度も海を渡った', ts=72)),
 weak(3, 2),
 MAP(LANGV, places=[{'at': [26.3, 127.8], 'label': '琉球の言葉', 'side': 1, 'col': 'gold'}, {'at': [35.7, 139.7], 'label': '日本語', 'side': 1, 'col': 'gold'}], regions=[{'at': [40, 118], 'rx': 8, 'ry': 5.5, 'col': 'teal', 'label': '大陸に、はっきりした親類は見つからない', 'ly': 0, 'ls': 28}]),
 CARD('人の流れと言葉の流れ。', '今も大きな謎。', bg=None),
 CARD('それでも、', '答えは1つ。', gold=1, bg=BG_THREE),
 # ── closing (94-101)
 THEO('日本人の成り立ち', [{'k': '1', 'name': '縄文'}, {'k': '2', 'name': '弥生'}, {'k': '3', 'name': '古墳時代'}], hi=[0, 1, 2], bg=BG_THREE),
 CARD('奪い合ったのではなく、', '混ざり合った。', gold=1, bg=BG_THREE),
 P('nabatake_z17', NABA, (1700, 1400), text=T('約3000年前 · 九州の海辺', '米の種を抱えた舟', ts=76)),
 PH('sannai_pit', [960, 760], (1600, 1450), text=T('浜で迎えたのは', '縄文の人々', ts=84)),
 P('daisen_z17', DS, (2200, 1700), text=T('それから1000年ほど後', '鉄の道具と新しい技', ts=76)),
 CARD('鏡の前の顔は、', 'すべての出会いの続き。', gold=1, bg=BG_THREE),
 STACK(show=[0, 1, 2], keep=[0, 1, 2], kicker='17万人分のDNA', note='これまでにない規模の調べ'),
 CARD('3つの流れは今も、', 'あなたの中で1つに。', gold=1, bg=BG_THREE),
 THEO('あなたの中の3つの流れ', [{'k': '1', 'name': '列島で\n1万年以上'}, {'k': '2', 'name': '米の種を\n携えて'}, {'k': '3', 'name': '鉄と\n新しい技を携えて'}], hi=[0, 1, 2], bg=BG_THREE),
 CARD('どの流れも、', '今も生き続けている。', bg=BG_THREE),
 COMMENT('縄文の流れを感じますか？', bg=BG_SAN),
 COMMENT('海を渡った人々の流れを？', bg=BG_SAN),
 COMMENT('ぜひコメント欄へ', '動画の最初の予想とも比べてみてください', bg=BG_SAN),
 CARD('最初の予想と、', '比べてみてください。', bg=BG_SAN),
 CARD('次回　縄文の人々の顔を、', 'DNAから確かめる。', fs=70, bg=BG_SAN),
 P('sannai_z17', SAN, (1800, 1500)),
]

lines = json.load(open('lines.json', encoding='utf-8'))
if len(S) != len(lines):
    [print(i+1, l["text"][:28], "|", json.dumps({k: v for k, v in s.items() if k in ("lines","kicker","text","layout")}, ensure_ascii=False)[:90]) for i, (s, l) in enumerate(zip(S, lines))]; sys.exit(f"✗ {len(S)} scenes for {len(lines)} sentences")
# readings fixed by hand after checking VOICEVOX's kana for every line (names: config/voicevox_dict.json)
SAY = {'s01': lambda t: t.replace('8分の1', '8ぶんの1'),
       's88': lambda t: t.replace('平らですっきりした顔', '平らで、すっきりした顔'),
       's59': lambda t: t.replace('そのため縄文人', 'そのため、縄文人'),
       's106': lambda t: t.replace('三重構造モデル', 'さんじゅう構造モデル'),
       's109': lambda t: t.replace('120の県', 'ひゃくにじゅうのけん'),
       's115': lambda t: t.replace('登り窯', 'のぼりがま'),
       's178': lambda t: t.replace('3ぶんの2近く', '3ぶんの2ちかく')}
for i in ('s69', 's72', 's78', 's94', 's105', 's145', 's177', 's198', 's204'):   # 米作り / 米の種 read べい… without this
    SAY[i] = (lambda f: lambda t: f(t).replace('米作り', 'コメ作り').replace('米の種', 'コメの種'))(SAY.get(i, lambda t: t))
ASR = json.load(open('asr_overrides.json', encoding='utf-8')) if os.path.exists('asr_overrides.json') else {}
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
ALWAYS = {'mysteries', 'timeline', 'bars', 'stack', 'doc', 'dots'}
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
       'title': '日本人はどこから来たのか', 'title_en': 'Where Did the Japanese Come From?', 'mysteries': WAVES,
       'board': {'kicker': '3つの波', 'solved': '確かめた'}, 'chapter_label': 'WAVE',
       'credits': ['地図　Natural Earth（パブリックドメイン）をもとに作図　空中写真　出典：国土地理院（地理院タイル）',
                   '研究　Cooke ほか（2021）Science Advances 7: eabh2419 ／ Yamamoto ほか（2024）Nature Communications 15: 9780',
                   '史料　『日本書紀』巻第十 応神天皇十四年条 ／『古事記』中巻 応神天皇の段（原文・新字体）',
                   *(['写真　' + '、'.join(sorted({n for v in PHOTO.values() for n in re.sub(r'（.*', '', v.replace('写真：', '')).split('、')})) + '（Wikimedia Commons、パブリックドメイン・CC0）'] if PHOTO else []),
                   '音声　VOICEVOX:青山龍星',
                   '地図上の経路・範囲は模式図、遺跡の位置の一部は概略です。'],
       'scenes': S}
json.dump(out, open('scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(S), 'scenes', dict(Counter(s['layout'] for s in S)), sum(1 for s in S if s.get('cont')), 'cont')
