#!/usr/bin/env python3
"""Scene assignment for 出雲大社 48メートルの神殿 (handbook 11-3 step 2), written by Claude Code in the session.
One entry per sentence of script.txt, in order → scenes.json. Layouts: index.html `L.*` (score / heights / plan / pillar are this film's additions)."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from say import say

# places (lat, lon): GSI place-name search (msearch.gsi.go.jp) and the aerials themselves
IZ = [35.4019, 132.6856]; HAS = [35.4012, 132.6856]; MUS = [35.39875, 132.68879]; INASA = [35.3964, 132.6745]; YAKUMO = [35.4060, 132.6880]
KOJIN = [35.37938, 132.85253]; NARA = [34.6890, 135.8398]; KYO = [35.0200, 135.7420]; SADO = [38.02, 138.37]; IZW = [35.40, 132.69]
GSI_KEYS = ('izumo_z18', 'izumo_z17', 'izumo_z15', 'kojin_z17', 'todaiji_z17', 'toji_z18')
PHOTO = {}   # filled from SOURCES.jsonl (Wikimedia Commons, public domain / CC0 only)
for l in open('SOURCES.jsonl', encoding='utf-8'):
    r = json.loads(l)
    if r['source'].startswith('Wikimedia'): PHOTO[r['name'].split('/')[-1].rsplit('.', 1)[0]] = r['credit'].replace('Public domain', 'パブリックドメイン')
A = json.load(open('assets.json', encoding='utf-8')) if os.path.exists('assets.json') else {}
NE = '出典：Natural Earth（地図データ、パブリックドメイン）'
JPW = {'c': [35.5, 135.0], 'w': 11}; JPS = {'c': [36.5, 135.4], 'w': 12.5}

def MAP(view, **kw): return {'layout': 'map', 'view': view, 'source': NE, **kw}
def P(img, at, span=(1500, 1350), **kw): return {'layout': 'photo', 'img': img, 'at': at, 'span': list(span), **kw}
def T(kicker=None, title=None, number=None, unit=None, caption=None, **kw): return {k: v for k, v in dict(kicker=kicker, title=title, number=number, unit=unit, caption=caption, **kw).items() if v is not None}
def CARD(*lines, bg=None, **kw): return {'layout': 'card', 'lines': list(lines), 'bg': bg, **kw}
def CH(num, title, sub, bg): return {'layout': 'chapter', 'num': num, 'title': title, 'sub': sub, 'bg': bg}
def BARS(kicker, items, bg=None, **kw): return {'layout': 'bars', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def CALC(kicker, rows, bg=None, **kw): return {'layout': 'calc', 'kicker': kicker, 'rows': rows, 'bg': bg, **kw}
def ROWS(kicker, rows, bg=None, **kw): return {'layout': 'rows', 'kicker': kicker, 'rows': [r if isinstance(r, dict) else {'k': r[0], 'v': r[1] if len(r) > 1 else '', 'hi': len(r) > 2} for r in rows], 'bg': bg, **kw}
def THEO(kicker, items, bg=None, **kw): return {'layout': 'theories', 'kicker': kicker, 'items': items, 'bg': bg, **kw}
def COMMENT(text, sub=None, bg=None): return {'layout': 'comment', 'text': text, 'sub': sub, 'bg': bg}
def DOC(doc, lines, hl, source, bg=None, fs=62): return {'layout': 'doc', 'doc': doc, 'lines': lines, 'hl': hl, 'fs': fs, 'source': source, 'bg': bg}
def B(img, at, span, a=.24): return {'img': img, 'at': at, 'span': span, 'a': a}
def HT(kicker, items, **kw): return {'layout': 'heights', 'kicker': kicker, 'items': items, 'bg': kw.pop('bg', None), **kw}
def PLAN(mode, **kw): return {'layout': 'plan', 'mode': mode, 'bg': kw.pop('bg', None), **kw}
def PIL(mode=None, **kw): return {'layout': 'pillar', 'mode': mode, 'bg': kw.pop('bg', None), **kw}
def AI(n, *lines, **kw): return CARD(*lines, kicker='AIの判定 · 検証' + str(n), **kw)
def ASK(n): return CARD('AIの判定は、', 'こうでした。', kicker='検証' + str(n), bg=None)

# backdrops by topic
def ctr(k): return [A[k]['w'] / 2, A[k]['h'] / 2, 0] if k in A else None
BG_HON = B('honden_cc0', ctr('honden_cc0'), 2200, .24); BG_HON2 = B('haiden', ctr('haiden'), 2200, .24); BG_AIR = B('izumo_z17', IZ, 1100, .24)
BG_AIR18 = B('izumo_z18', HAS, 420, .26); BG_HOTO = B('hotohoto', ctr('hotohoto'), 1500, .26); BG_OON = B('oonamuchi', ctr('oonamuchi'), 1000, .24)
BG_DOTAKU = B('dotaku_group', ctr('dotaku_group'), 2200, .24); BG_1922 = B('izumo1922', ctr('izumo1922'), 1500, .24)

# the spine: the score, 記録の側 vs 誇張の側, over five checks
TOPICS = ['言い伝えの数字', '平安の記録', '倒れた記録', '1枚の設計図', '地中の柱']
M = ['exa', 'rec', 'rec', 'exa', 'rec']
def SCORE(n, add=None, focus=None, **kw):   # n = checks decided so far
    mk = M[:n]; return {'layout': 'score', 'rec': mk.count('rec'), 'exa': mk.count('exa'), 'marks': mk, 'add': add, 'focus': focus, 'topics': TOPICS, 'bg': None, **kw}
H3 = [{'label': '大昔', 'sub': '32丈', 'm': 96, 'dashed': True}, {'label': 'その後', 'sub': '16丈', 'm': 48, 'dashed': True}, {'label': '今の本殿', 'sub': '8丈', 'm': 24, 'hi': True}]
def h3(show=None, keep=None, **kw): return HT('本殿の高さ · 出雲大社に伝わる3つの数字', H3, show=show, keep=keep, max=100, **kw)
TL = {'layout': 'timeline', 'kicker': '出雲大社の神殿が倒れた記録', 'axis': [1000, 1250], 'step': 50}
FALLS = [{'y': 1031, 'label': '1031', 'side': 1}, {'y': 1061, 'label': '1061', 'side': -1}, {'y': 1109, 'label': '1109', 'side': 1}, {'y': 1141, 'label': '1141', 'side': -1},
         {'y': 1172, 'label': '1172', 'side': 1}, {'y': 1235, 'label': '1235', 'sub': '鎌倉時代', 'side': -1}]
TL2 = {'layout': 'timeline', 'kicker': '鎌倉時代の建て直し', 'axis': [1230, 1255], 'step': 5}
T35 = {'y': 1235, 'label': '倒れる', 'sub': '1235年', 'side': 1}; T48 = {'y': 1248, 'label': '新しい本殿', 'sub': '1248年', 'side': -1, 'hi': True}
WEAK = [('弱点 1', '見つかった柱は鎌倉時代のもの'), ('弱点 2', '柱の太さから高さは決まらない'), ('弱点 3', '48メートルは言い伝えの数字')]
def weak(n, hi): return ROWS('この結論の弱いところ', [(k, v, True) if i == hi else (k, v) for i, (k, v) in enumerate(WEAK[:n])], bg=None)
KOJIKI = DOC('『古事記』上巻（書き下し）', ['底つ石根に', '宮柱ふとしり', '高天の原に', '氷木たかしりて'], [1, 3], '『古事記』上巻 国譲りの段（書き下し）', bg=BG_OON, fs=58)
KUCHI = lambda hl: DOC('『口遊』（970年）', ['雲太', '和二', '京三'], hl, '源為憲『口遊』（970年）', bg=BG_HON, fs=110)
PLACES3 = [{'at': IZW, 'label': '出雲', 'sub': '雲太 · 1番目', 'side': -1, 'col': 'gold', 'big': 1, 'ss': 34, 'sc': 'gold'},
           {'at': NARA, 'label': '大和', 'sub': '和二 · 2番目', 'side': 1, 'col': 'teal', 'big': 1, 'ss': 34}, {'at': KYO, 'label': '京', 'sub': '京三 · 3番目', 'side': -1, 'col': 'teal', 'big': 1, 'ss': 34, 'dy': -40}]

S = [
 # ── hook (1-14)
 P('honden_cc0', ctr('honden_cc0'), (2300, 1900), text=T('平安〜鎌倉時代 · およそ200年', '7度も倒れた神殿', ts=80)),
 CARD('風もない日に、', 'ひとりでに倒れた。', bg=BG_HON),
 CARD('ふつうの高さの建物なら、', 'そう何度も倒れない。', bg=BG_HON),
 P('honden2', ctr('honden2'), (2300, 1900), text=T('出雲大社の言い伝え', None, '48', 'm', 'かつての神殿の高さ')),
 HT('今の本殿と、言い伝えの高さ', [{'label': '今の本殿', 'm': 24, 'floors': 1}, {'label': '言い伝え', 'm': 48, 'hi': True, 'floors': 1, 'sub': '16階建てほど'}], floors=True, max=60, step=12, note='1階 ≈ 3 m で数えた目安'),
 CARD('長いあいだ、', '話を大きくした言い伝え。', bg=BG_HON),
 CARD('1000年も前に、', '建てられたはずがない。', bg=BG_HON),
 THEO('AIと一緒に確かめたもの', [{'k': '1', 'name': '平安時代の\n記録'}, {'k': '2', 'name': '出雲大社の\n古い設計図'}, {'k': '3', 'name': '地中の\n巨大な柱'}], show=[0, 1], hide=[2], bg=BG_HON),
 THEO('AIと一緒に確かめたもの', [{'k': '1', 'name': '平安時代の\n記録'}, {'k': '2', 'name': '出雲大社の\n古い設計図'}, {'k': '3', 'name': '地中の\n巨大な柱'}], show=[2], hi=[2], bg=BG_HON),
 CARD('48メートルの神殿をめぐる、', '思いもよらない証拠。', gold=1, bg=BG_HON),
 COMMENT('あなたの予想は？', '動画を見る前に、コメント欄へ一言', bg=BG_HON),
 THEO('48メートルの神殿は', [{'k': 'A', 'name': '本当に\n建っていた'}, {'k': 'B', 'name': '話を\n盛っただけ'}], bg=BG_HON),
 CARD('最後に、', 'AIの答えと答え合わせ。', bg=BG_HON),
 CARD('まずは、', '確かに分かっていること。', bg=BG_AIR),
 # ── what is known (15-28)
 MAP(JPW, places=[{'at': IZW, 'label': '出雲大社', 'sub': '島根県出雲市', 'side': 1, 'col': 'gold'}]),
 P('oonamuchi', ctr('oonamuchi'), (1000, 900), stamp='大己貴命（大国主大神）', text=T('まつられている神様', '大国主大神', ts=80)),
 P('haiden', ctr('haiden'), (2200, 1900), text=T('縁結びの神様', None, None, None, '毎年、全国から多くの人が参拝')),
 ROWS('旧暦の10月', [('全国では', '神無月'), ('出雲では', '神在月', True)], bg=BG_HOTO),
 P('izumo_z15', [35.400, 132.692], (7000, 6000), rings=[{'at': IZ, 'r': 34, 'label': '本殿', 'side': 1}, {'at': YAKUMO, 'r': 30, 'label': '八雲山', 'side': 1, 'col': 'gold'}, {'at': INASA, 'r': 34, 'label': '稲佐の浜', 'side': -1, 'col': 'teal'}]),
 P('izumo_z15', INASA, (3800, 3200), rings=[{'at': INASA, 'r': 44, 'label': '稲佐の浜', 'side': -1, 'col': 'teal'}], text=T('神在月', '神々が上陸する浜', ts=80)),
 P('honden_cc0', ctr('honden_cc0'), (2000, 1800), text=T('今の本殿（国宝）', '1744年に建立', ts=84)),
 P('honden2', ctr('honden2'), (2000, 1800), text=T('今の本殿の高さ', None, 'およそ24', 'm', '神社の本殿として日本一')),
 CARD('60年ほどごとに、', '大がかりな修理。', bg=BG_HON2),
 P('honden2', ctr('honden2'), (2200, 1900), text=T('2013年', '平成の大遷宮', ts=84)),
 ROWS('出雲大社の名前', [('明治の初めまで', '杵築大社', True), ('今', '出雲大社')], bg=BG_1922),
 DOC('『出雲国風土記』（733年）', ['諸の皇神等', '宮処に参集ひて', '杵築きたまひき'], [2], '『出雲国風土記』出雲郡 杵築郷（書き下し）', bg=BG_AIR),
 ROWS('今に伝わる風土記', [('出雲', 'ほぼ完全な形', True), ('常陸 · 播磨 · 豊後 · 肥前', '一部だけ')], bg=BG_AIR),
 CARD('1300年近く前の出雲を、', '今も細かく知ることができる。', fs=70, bg=BG_AIR),
 # ── the myth (29-37)
 CARD('出雲大社の始まりは、', '神話の中に。', bg=BG_HOTO),
 CARD('舞台は、', '国を譲る場面。', bg=BG_OON),
 CARD('天の神々に、', '国を譲る。', kicker='古事記', bg=BG_OON),
 CARD('その代わりに求めたのは、', '自分の住まいとなる立派な宮。', gold=1, fs=70, bg=BG_OON),
 KOJIKI,
 DOC('『日本書紀』神代下（書き下し）', ['柱は', '高く太く', '板は', '広く厚く'], [1, 3], '『日本書紀』神代下 第九段 一書第二（書き下し）', bg=BG_OON, fs=66),
 CARD('神話が約束したのは、', 'とてつもなく高く太い建物。', gold=1, fs=70, bg=BG_OON),
 CARD('高さそのものが、', '神様との約束。', bg=BG_HON),
 CARD('では、', 'どれほど高かったのか。', bg=BG_HON),
 # ── three numbers (38-48)
 THEO('本殿の高さ · 出雲大社に伝わる3つの数字', [{'k': '大昔', 'name': '32丈'}, {'k': 'その後', 'name': '16丈'}, {'k': '今', 'name': '8丈'}], bg=BG_HON),
 h3(show=[0]),
 CALC('丈をメートルに', [('1丈', 'およそ3 m'), ('32丈', 'およそ96 m')]),
 h3(show=[0, 1], keep=[0]),
 h3(show=[0, 1, 2], keep=[0, 1]),
 HT('96メートルは', [{'label': '大昔の言い伝え', 'm': 96, 'hi': True, 'floors': 1, 'sub': '30階建てに近い'}, {'label': '今の本殿', 'm': 24, 'floors': 1}], floors=True, max=100, note='1階 ≈ 3 m で数えた目安'),
 CARD('木の建物で、', 'そこまでの高さは信じがたい。', fs=70),
 CARD('48メートルの言い伝えも、', '大げさな話と見られてきた。', fs=70, bg=BG_HON),
 P('toji', [800, 1000, 0], (1500, 1300), stamp='東寺の五重塔（京都）', text=T('今ある木造の塔でいちばん高い', None, 'およそ55', 'm')),
 HT('江戸時代の五重塔と、平安時代の出雲', [{'label': '東寺の五重塔', 'm': 55, 'sub': '江戸時代の建て直し'}, {'label': '出雲大社？', 'm': 48, 'hi': True, 'dashed': True, 'sub': '平安時代の言い伝え'}], max=60, step=10),
 CARD('明治から100年以上、', '決着がつかない問い。', bg=BG_HON),
 P('kojin_z17', KOJIN, (1300, 1100), rings=[{'at': KOJIN, 'r': 40, 'label': '荒神谷遺跡', 'sub': '島根県出雲市', 'side': 1}], text=T('発掘から分かったこと', '古代出雲の力', ts=84)),
 P('kenpoko', ctr('kenpoko'), (2300, 2000), stamp='荒神谷遺跡の銅剣・銅矛', text=T('1984年 · 荒神谷遺跡', None, '358', '本', '銅の剣がまとめて')),
 BARS('銅の剣の数', [{'label': 'それまでの全国', 'value': 300, 'text': 'およそ300本', 'col': 'teal'}, {'label': '荒神谷 1か所', 'value': 358, 'text': '358本', 'hi': True}], max=400),
 BARS('銅の剣の数', [{'label': 'それまでの全国', 'value': 300, 'text': 'およそ300本', 'col': 'teal'}, {'label': '荒神谷 1か所', 'value': 358, 'text': '358本', 'hi': True}], max=400, note='たった1か所から、日本じゅうの数を上回る'),
 P('dotaku_group', ctr('dotaku_group'), (2300, 2000), stamp='加茂岩倉遺跡の銅鐸', text=T('1996年 · 加茂岩倉遺跡', None, '39', '個', '銅鐸')),
 P('dotaku8', ctr('dotaku8'), (1700, 1500), stamp='加茂岩倉遺跡の銅鐸', text=T('1か所から出た銅鐸の数', '日本で最多', ts=84)),
 CARD('巨大な神殿を建てる力が、', '出雲にあっても不思議ではない。', fs=66, bg=BG_DOTAKU),
 CARD('それでも、', '決着がつかない理由。', bg=BG_HON),
 ROWS('48メートルの神殿', [('姿を描いた絵', '見つかっていない'), ('実物の一部', '見つかっていない', True)], bg=None),
 CARD('AIに確かめてもらう、', '2つのルール。'),
 ROWS('AIの2つのルール', [('ルール 1', '同じ時代の記録ほど重く見る', True)]),
 ROWS('AIの2つのルール', [('ルール 1', '同じ時代の記録ほど重く見る'), ('ルール 2', '信じる側にも疑う側にも同じ物差し', True)]),
 SCORE(0),
 SCORE(0, kicker='記録の側　対　誇張の側'),
 SCORE(0, kicker='検証は全部で5つ'),
 CARD('最後に勝つのは、', 'どちらか。', bg=BG_HON),
 # ── check 1: the numbers (65-79)
 CH('01', '言い伝えの数字', '検証1', BG_HON),
 h3(keep=[0, 1, 2]),
 h3(keep=[0, 1, 2], note='3つの数字の関係は？'),
 CALC('3つの数字', [('96 ÷ 2', '48'), ('48 ÷ 2', '24')]),
 ASK(1),
 AI(1, '時代ごとにぴったり半分ずつ、', '変わるとは考えにくい。', fs=66),
 AI(1, '数字がきれいにそろうのは、', '後から整えた跡かもしれない。', fs=66, gold=1),
 ROWS('32丈と16丈', [('いつ書かれたか', 'はっきりしない'), ('誰が書いたか', 'はっきりしない')]),
 ROWS('32丈と16丈', [('いつ書かれたか', 'はっきりしない'), ('誰が書いたか', 'はっきりしない'), ('平安時代の記録に', '書かれていない', True)]),
 CARD('言い伝えの数字だけでは、', '48メートルの証拠にならない。', fs=66),
 CARD('それでも、', '高い神殿がなかったことにはならない。', fs=66),
 CARD('言い伝えの奥の出来事は、', '別の記録で確かめる。', fs=70, bg=BG_HON),
 SCORE(1, add='exa', focus=0),
 SCORE(1),
 CARD('平安時代の人々の目に、', '出雲大社はどう映ったのか。', fs=70, bg=BG_HOTO),
 # ── check 2: the Heian record (80-106)
 CH('02', '平安時代の記録', '検証2', BG_HOTO),
 ROWS('平安時代の教科書', [('書かれた年', '970年'), ('書いた人', '源為憲'), ('読む人', '貴族の子どもたち', True)]),
 CARD('口遊', 'くちずさみ', gold=0, center=1),
 CARD('覚えておくべき知識を、', '口ずさめる短い言葉に。'),
 KUCHI([]),
 KUCHI([0, 1]),
 KUCHI([0, 1, 2]),
 P('daigokuden', ctr('daigokuden'), (1500, 1300), stamp='大極殿（平城宮の模型）', text=T('大極殿', '都の宮殿の中心', ts=84)),
 CARD('当時の貴族なら、', '誰でも知っている常識。'),
 MAP(JPW, places=PLACES3, note='『口遊』（970年）の「雲太 和二 京三」'),
 P('daibutsuden', ctr('daibutsuden'), (2300, 2000), stamp='東大寺大仏殿（今の建物）', text=T('和二 · 2番目', '東大寺の大仏殿', ts=84)),
 CALC('奈良時代の大仏殿', [('高さ', '15丈')]),
 CALC('奈良時代の大仏殿', [('高さ', '15丈'), ('15丈 × 3 m', 'およそ45 m')]),
 HT('もし雲太が高さの順なら', [{'label': '大仏殿', 'm': 45, 'sub': '奈良時代 · 15丈'}, {'label': '出雲大社', 'm': 48, 'hi': True, 'dashed': True, 'text': '45 m より上', 'sub': '雲太 · 1番目'}], max=60, step=10),
 HT('もし雲太が高さの順なら', [{'label': '大仏殿', 'm': 45, 'sub': '奈良時代 · 15丈'}, {'label': '言い伝え', 'm': 48, 'hi': True, 'sub': '16丈'}], max=60, step=10),
 CARD('ここで、', 'AIが出した1つの疑問。'),
 CARD('雲太の「太」は、', '大きいという意味。'),
 THEO('「雲太」の順番は', [{'k': 'A', 'name': '高さの順'}, {'k': 'B', 'name': '建物全体の\n大きさの順'}]),
 ASK(2),
 AI(2, '970年の時点で、', '大仏殿をしのぐ大きな建物。', fs=70, gold=1),
 AI(2, '48メートルの言い伝えを支える、', '同時代の記録。', fs=70),
 P('daibutsuden', ctr('daibutsuden'), (2000, 1800), text=T('日本最大級の木造の建物', '奈良の大仏殿', ts=84)),
 MAP(JPW, places=[PLACES3[0], dict(PLACES3[1], col='dim', sc='dim')], regions=[{'at': IZW, 'rx': .9, 'ry': .6, 'col': 'gold'}], note='大仏殿より上とされた建物が、遠い出雲に'),
 SCORE(2, add='rec', focus=1),
 SCORE(2),
 SCORE(2, kicker='同点'),
 HT('なぜ半分の高さに？', [{'label': '言い伝え', 'm': 48, 'dashed': True}, {'label': '今の本殿', 'm': 24, 'hi': True}], max=60, step=12),
 # ── check 3: the collapses (107-145)
 CH('03', '倒れた記録', '検証3', BG_HON),
 dict(TL, events=[]),
 dict(TL, events=FALLS[:1]),
 CARD('風もないのに、', 'ひとりでに倒れた。', kicker='1031年 · 出雲から都への報告', bg=BG_HOTO),
 dict(TL, events=FALLS[:5]),
 dict(TL, events=FALLS, spans=[{'from': 1031, 'to': 1235, 'label': 'およそ200年で7度'}]),
 CALC('倒れた間隔', [('200年 ÷ 7度', 'およそ30年に1度')]),
 CARD('親から子へ代わるほどの間隔で、', '倒れては建て直す。', fs=66, bg=BG_HON),
 CARD('AIが目を向けたのは、', '倒れた建物の高さ。', bg=BG_HON),
 P('honden2', ctr('honden2'), (2000, 1800), text=T('今の本殿 · 1744年から', '280年近く倒れていない', ts=72)),
 ASK(3),
 AI(3, '30年に1度倒れる建物は、', '今の本殿とまったく違う形。', fs=66),
 AI(3, '何度も倒れたことが、', 'とびぬけて高い証拠。', gold=1),
 CARD('ところが、', '思わぬ記録。', bg=BG_HOTO),
 ROWS('1031年の報告', [('1031年', '神殿がひとりでに倒れた'), ('翌年', 'うその報告とされる', True)]),
 MAP(JPS, places=[{'at': IZW, 'label': '出雲', 'side': -1, 'col': 'gold'}, {'at': SADO, 'label': '佐渡', 'side': 1, 'col': 'teal'}], routes=[{'pts': [[35.6, 133.0], [36.9, 135.5], [37.9, 138.1]], 'col': 'teal', 'dashed': True, 't': .4, 'dur': 1.6}],
     text=T('お告げを偽ったとして', '佐渡へ流される', ts=80)),
 CARD('風もないのに倒れた話は、', '本当ではなかったかもしれない。', fs=66),
 ROWS('残る6度の記録', [('1', '都の貴族の日記'), ('2', '出雲大社の古い文書'), ('', '別々に残っている', True)]),
 CARD('1つがうそでも、', '倒れ続けた事実は揺らがない。', gold=1, fs=70),
 dict(TL2, events=[T35]),
 dict(TL2, events=[T35], spans=[{'from': 1235, 'to': 1248, 'label': '仮の神殿へ · 建て直し'}]),
 dict(TL2, events=[T35, T48], spans=[{'from': 1235, 'to': 1248, 'label': '仮の神殿へ · 建て直し'}]),
 CALC('建て直しにかかった年月', [('1248 − 1235', '13年')]),
 ROWS('出雲の人々の仕事', [('建て直し', '13年もかかる大工事'), ('倒れる間隔', '30年に1度', True)]),
 CARD('ほとんど休む間もなく、', '神殿を建て続けた。', bg=BG_HON),
 CARD('何度も倒れた記録は、', '並外れた高さを示している。', gold=1, fs=70),
 SCORE(3, add='rec', focus=2),
 SCORE(3),
 SCORE(3, kicker='記録の側が逆転'),
 CARD('では、', 'なぜそれほど倒れたのか。'),
 CARD('AIが注目したのは、', '柱の立て方。'),
 ROWS('平安 · 鎌倉時代の神殿の柱', [('立て方', '掘立柱', True), ('', '地面に深い穴を掘り、直接立てる')]),
 CARD('地中に埋まった部分は、', '少しずつ傷んでいく。'),
 ROWS('高い柱にかかる力', [('風', '高い建物ほど強く受ける'), ('屋根', '重みがかかる'), ('根元', '地中で傷んでいく', True)]),
 CARD('根元から傷んだ高い柱は、', 'いつか持ちこたえられなくなる。', fs=66),
 ASK(3),
 AI(3, '倒れ続けた理由は、', '高さと柱の立て方の両方。', fs=70, gold=1),
 AI(3, '低い建物なら、', '30年ごとに倒れることはまずない。', fs=66),
 CARD('倒れ続けた神殿は、', 'どんな形をしていたのか。', bg=BG_HON),
 # ── check 4: the plan (146-171)
 CH('04', '1枚の設計図', '検証4', BG_HON2),
 ROWS('金輪御造営差図', [('伝えてきた家', '千家家（神社に代々仕える）'), ('描かれたもの', '神殿の柱と階段', True)]),
 PLAN('grid', side=['柱は9本', '縦横に3本ずつ']),
 PLAN('bundle', side=['1本の柱が', '丸太3本を束ねた形']),
 PLAN('bundle', rings=1, side=['金輪', '3本を締めつける鉄の輪']),
 PLAN('bundle', rings=1, side=['金輪', '＝鉄の輪']),
 PLAN('grid', side=['この並び方は', '今の本殿と同じ']),
 P('honden_cc0', ctr('honden_cc0'), (2000, 1800), text=T('日本で最も古い神社の建て方の1つ', '大社造', ts=92)),
 CARD('変わったのは、', '柱の太さと高さ。'),
 THEO('柱1本の作り', [{'k': '今の本殿', 'name': '1本の木'}, {'k': '図面', 'name': '3本を束ねる'}], hi=[1]),
 PLAN('stair'),
 PLAN('stair'),
 PLAN('stair', run=1),
 CARD('長い階段が必要なのは、', '床がそれだけ高かったから。', fs=70),
 CARD('AIは、', 'この図面にも厳しい目。'),
 ROWS('図面の弱いところ', [('建物の高さ', '書かれていない', True)]),
 ROWS('図面の弱いところ', [('建物の高さ', '書かれていない'), ('描かれた時期', 'はっきりしない', True)]),
 ROWS('図面の弱いところ', [('建物の高さ', '書かれていない'), ('描かれた時期', 'はっきりしない'), ('今伝わる図面', '鎌倉〜室町時代ごろの写し', True)]),
 CARD('立派さを示すために、', '大きく描いた可能性も。', fs=70),
 CARD('そのまま建てるには大きすぎる。', '絵空事の図、という声も。', fs=66),
 ASK(4),
 AI(4, '出雲大社の側だけの資料で、', 'ほかに裏付けがない。', fs=70),
 AI(4, 'これだけでは、', '48メートルの証拠と言えない。', fs=70, gold=1),
 SCORE(4, add='exa', focus=3),
 SCORE(4),
 SCORE(4, kicker='再び同点'),
 # ── channel (172-177)
 COMMENT('AIで確かめてほしい謎は？', 'コメントを読んで、次のテーマを決めています', bg=BG_HON),
 COMMENT('出雲大社でも、ほかの謎でも', '日本史の謎なら何でも', bg=BG_HON),
 COMMENT('ぜひコメントで', '教えてください', bg=BG_HON),
 SCORE(4, focus=4, kicker='勝負は最後の検証に'),
 CARD('歴史の謎を、', 'AIと1つずつ確かめる。', bg=BG_HON),
 CARD('次の検証を見逃さないよう、', 'チャンネル登録を。', fs=70, bg=BG_HON),
 # ── check 5: the pillars (178-214)
 CH('05', '地面の下の柱', '検証5', BG_AIR),
 CARD('ここでAIは、', '視点を変えた。', bg=BG_AIR),
 CARD('言葉で書かれた記録ではなく、', '地面の下に残されたもの。', fs=66, bg=BG_AIR),
 P('izumo_z18', IZ, (700, 560), text=T('2000年の春', '出雲大社の境内で', ts=84)),
 P('izumo_z18', HAS, (520, 420), rings=[{'at': HAS, 'r': 46, 'label': '八足門の前', 'side': 1}, {'at': IZ, 'r': 30, 'label': '本殿', 'side': 1, 'col': 'gold'}]),
 CARD('発掘の目的は、', '昔の柱を探すことではなかった。', fs=66, bg=BG_AIR18),
 CARD('地下の施設を造る前の、', '決まった手順の調査。', fs=70, bg=BG_AIR18),
 CARD('地面の下から、', 'とてつもないもの。', gold=1, bg=BG_AIR18),
 PIL('bare', side=['杉の丸太が3本', '1本の直径 1 m 超']),
 PIL(),
 PIL('people'),
 CALC('柱の切り口の広さ', [('3本合わせて', 'およそ4 m²')]),
 PIL('tatami'),
 PIL('stones'),
 PIL('stones'),
 CARD('直径1メートルを超える杉は、', '何百年も育った大木。', fs=70),
 CALC('9本の柱に必要な杉', [('3本 × 9本', '27本')]),
 PLAN('bundle', found=['uzu'], side=['宇豆柱', '本殿の正面中央']),
 PLAN('bundle', found=['uzu', 'shin', 'side'], side=['心御柱と側柱も', 'その年のうちに']),
 CARD('全国で大きく報じられ、', '柱を一目見ようと人々が。', fs=70, bg=BG_HON),
 P('izumo_z17', MUS, (1100, 900), rings=[{'at': MUS, 'r': 44, 'label': '島根県立古代出雲歴史博物館', 'side': 1, 'ls': 30}, {'at': IZ, 'r': 30, 'label': '本殿', 'side': 1, 'col': 'gold'}], text=T('3本の柱を保存', None, None, None, '800年近く前の柱の姿')),
 PLAN('bundle', rings=1, found=['uzu', 'shin', 'side'], side=['図面と', 'ぴたりと一致']),
 CARD('絵空事と言われた図面が、', '地面の下の実物で確かめられた。', fs=64, gold=1),
 dict(TL2, kicker='柱の木の年代', events=[T35, dict(T48, label='柱が立てられた', sub='1248年の可能性が高い')]),
 dict(TL2, kicker='柱の木の年代', events=[T35, dict(T48, label='柱が立てられた', sub='1248年の可能性が高い')], spans=[{'from': 1235, 'to': 1250, 'label': '鎌倉時代の中ごろ'}]),
 ASK(5),
 AI(5, '出雲大社の側だけの図面を、', '地中の実物が裏付けた。', fs=70),
 AI(5, '直径3メートルの柱が9本。', '今の本殿とは比べものにならない規模。', fs=64, gold=1),
 CARD('柱をもとに、', '鎌倉時代の本殿を描き直す。', fs=70, bg=BG_AIR),
 P('izumo_z17', MUS, (900, 760), rings=[{'at': MUS, 'r': 40, 'side': 1}], text=T('古代出雲歴史博物館', '高さ48メートルの', None, None, '本殿の10ぶんの1の模型', ts=76)),
 CARD('柱が見つかる前にも、', '描き直そうとした人々。'),
 ROWS('48メートルの本殿の復元図', [('つくった人々', '大林組のプロジェクトチーム'), ('監修', '建築史家 福山敏男', True)]),
 ROWS('福山敏男', [('1955年', '古代の出雲大社の本殿についての本'), ('早くから', '高い本殿の姿を研究', True)]),
 CARD('地中の柱が、', '何十年も遅れて答えを出した。', fs=70),
 SCORE(5, add='rec', focus=4),
 SCORE(5, win='rec', kicker='最終結果'),
 SCORE(5, win='rec', kicker='記録の側の勝利'),
 # ── weaknesses (215-223)
 CARD('ただし、', 'この結果の弱点。'),
 weak(0, -1) | {'kicker': 'この結論の弱いところ · 3つ'},
 weak(1, 0),
 ROWS('弱点 1', [('970年', '雲太と呼ばれた神殿'), ('1248年', '見つかった柱'), ('同じ大きさか', '分からない', True)]),
 weak(2, 1),
 CARD('太い柱を使った、', 'それほど高くない建物の可能性も。', fs=66),
 CARD('48メートルという数字そのものは、', '地中の柱も証明していない。', fs=64),
 weak(3, 2),
 ROWS('平安 · 鎌倉時代の記録', [('「48メートル」と書いた文書', '見つかっていない', True)]),
 # ── the answer and closing (224-247)
 CARD('それでも、', '答えは1つ。', gold=1, bg=BG_HON),
 HT('鎌倉時代の出雲大社', [{'label': '鎌倉時代の神殿', 'm': 48, 'hi': True, 'text': '巨大な神殿', 'sub': '直径3 m の柱 9本'}, {'label': '今の本殿', 'm': 24}], max=60, step=12),
 CARD('48メートルの言い伝えは、', '絵空事ではなかった。', gold=1, bg=BG_HON),
 dict(TL, events=FALLS, spans=[{'from': 1031, 'to': 1235, 'label': '何度も倒れた記録が、高さを裏付ける'}]),
 CARD('30年に1度倒れるほど高い神殿を、', '建て直し続けた。', fs=66, bg=BG_HON),
 ROWS('倒れるたびに', [('杉の大木', '27本'), ('束ねる', '鉄の輪'), ('階段', 'およそ109 m', True)]),
 CARD('その作業を、', '倒れるたびにくり返した。', bg=BG_HON),
 CARD('大国主大神が求めた約束を、', '守り続けること。', fs=70, bg=BG_OON),
 KOJIKI,
 P('izumo_z15', INASA, (3000, 2600), text=T('鎌倉時代のある秋の夕暮れ', '出雲の浜から', ts=84)),
 P('hotohoto', ctr('hotohoto'), (1500, 1300)),
 PLAN('stair', bg=BG_HOTO),
 HT('やがて今の高さに', [{'label': '鎌倉時代の神殿', 'm': 48, 'dashed': True}, {'label': '今の本殿', 'm': 24, 'hi': True}], max=60, step=12),
 P('honden_cc0', ctr('honden_cc0'), (2000, 1800), text=T('今も', '神社の本殿で日本一の高さ', ts=64)),
 ROWS('今の本殿が倒れない理由', [('高さ', '半分に'), ('柱', '地面に埋めず、石の上に立てる', True)], bg=BG_HON),
 THEO('出雲の人々の選択', [{'k': 'A', 'name': '高さを\n守る'}, {'k': 'B', 'name': '倒れない\n建物'}], bg=BG_HON),
 THEO('出雲の人々の選択', [{'k': 'A', 'name': '高さを\n守る'}, {'k': 'B', 'name': '倒れない\n建物'}], hi=[1], bg=BG_HON),
 P('honden_cc0', ctr('honden_cc0'), (2000, 1800), text=T('1000年前の人々が見上げた', '高さの記憶', ts=84)),
 COMMENT('48メートルの神殿は本当に建っていた？', bg=BG_HON),
 COMMENT('それとも、記録が大げさだった？', bg=BG_HON),
 COMMENT('ぜひコメント欄へ', '動画の最初の予想とも比べてみてください', bg=BG_HON),
 CARD('最初の予想と、', '比べてみてください。', bg=BG_HON),
 CARD('次回も、日本の歴史の謎を、', '記録と数字で確かめる。', fs=70, bg=BG_HON),
 P('izumo_z17', IZ, (1500, 1300)),
]

lines = json.load(open('lines.json', encoding='utf-8'))
if len(S) != len(lines):
    [print(i+1, l["text"][:28], "|", json.dumps({k: v for k, v in s.items() if k in ("lines","kicker","text","layout")}, ensure_ascii=False)[:90]) for i, (s, l) in enumerate(zip(S, lines))]; sys.exit(f"✗ {len(S)} scenes for {len(lines)} sentences")
ASR = json.load(open('asr_overrides.json', encoding='utf-8')) if os.path.exists('asr_overrides.json') else {}
def credit(imgs):
    g = [i for i in imgs if i in GSI_KEYS]; ph = [PHOTO[i] for i in imgs if i in PHOTO]
    return '・'.join((['出典：国土地理院（空中写真）'] if g else []) + ph)
def fit(k, sp):   # a photograph's span (source px across) must not exceed what it has, or the frame shows black bars
    if k not in A or A[k]['z'] is not None: return sp
    return min(sp, int(A[k]['w'] * .98), int(A[k]['h'] * 16 / 9 * .98))
for s, l in zip(S, lines):
    for k in [k for k, v in s.items() if v is None]: s.pop(k)
    if s.get('layout') == 'photo' and s['img'] not in A:   # photo not downloaded: show its words on a card over the honden
        t = s.get('text', {}); first = t.get('title') or ((t.get('number', '') + t.get('unit', '')) or s.get('stamp'))
        s.clear(); s.update(CARD(*[x for x in [first, t.get('caption')] if x], kicker=t.get('kicker'), bg=BG_HON))
        if not s['kicker']: s.pop('kicker')
    if s.get('bg') and s['bg']['img'] not in A: s['bg'] = BG_HON
    if s.get('layout') == 'photo': s['span'] = [fit(s['img'], v) for v in s['span']]
    if s.get('bg'): s['bg'] = dict(s['bg'], span=fit(s['bg']['img'], s['bg']['span']))
    imgs = [i for i in [s.get('img')] + ([s['bg']['img']] if s.get('bg') else []) if i]
    if imgs:
        c = credit(imgs); keep = s.get('source', '')
        s['source'] = (keep + '・' + c) if keep and not keep.startswith('出典：国土地理院') else c
    t = say(l['id'], l['text'])
    if t != l['text']: s['say'] = t
    if l['id'] in ASR: s['asr'] = ASR[l['id']]
# Same picture, next sentence: continue the shot (cont) instead of cutting to an identical frame
ALWAYS = {'timeline', 'bars', 'doc', 'score', 'heights', 'plan', 'pillar'}
def same_picture(a, b):
    if a['layout'] != b['layout']: return False
    if a['layout'] == 'photo': return a['img'] == b['img']
    if a['layout'] == 'map': return a['view'] == b['view']
    if a['layout'] in ALWAYS: return a.get('axis') == b.get('axis') and a.get('doc') == b.get('doc') and (a.get('mode') == 'stair') == (b.get('mode') == 'stair')
    if a['layout'] in ('rows', 'calc', 'theories'): return a.get('kicker') == b.get('kicker')
    return False
for a, b in zip(S, S[1:]):
    if same_picture(a, b):
        b['cont'] = True
        if 'bg' in a: b['bg'] = a['bg']
        elif 'bg' in b: b.pop('bg')
        if a.get('source') and not b.get('source'): b['source'] = a['source']
names = sorted({n for v in PHOTO.values() for n in re.sub(r'（.*', '', v.replace('写真：', '')).split('、') if n})
out = {'_about': 'One entry per sentence (same order as script.txt); generated by tools/make_scenes.py (Claude Code). Layouts: index.html L.*.',
       'title': '出雲大社 48メートルの神殿', 'title_en': 'The 48-Metre Shrine of Izumo', 'mysteries': TOPICS, 'chapter_label': 'CHECK',
       'credits': ['空中写真　出典：国土地理院（地理院タイル）　地図　Natural Earth（パブリックドメイン）をもとに作図',
                   '史料　『口遊』（970年）／『古事記』上巻／『日本書紀』神代下／『出雲国風土記』（書き下し）',
                   *(['写真　' + '、'.join(names) + '（Wikimedia Commons、パブリックドメイン・CC0）'] if names else []),
                   '音声　VOICEVOX:青山龍星',
                   '高さの図・柱の図・図面の図は、台本の数字をもとにした模式図です。'],
       'scenes': S}
json.dump(out, open('scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(S), 'scenes', dict(Counter(s['layout'] for s in S)), sum(1 for s in S if s.get('cont')), 'cont')
