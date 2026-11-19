#!/usr/bin/env python3
"""Patiently look for public-domain / CC0 pictures on Wikimedia Commons and download the best match.
Commons rate-limits this container's shared address hard (HTTP 429), so every call waits, and a 429
waits longer and tries again. Run it detached and read the log.

  python tools/commons_hunt.py            # works through WANTED below, writing raw/<key>.jpg + SOURCES.jsonl
"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = {'User-Agent': 'history-video-ai/0.1 (educational documentary; contact via repository)'}
GAP = 40          # seconds between calls when all is well
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# key → search terms, tried in order until a public-domain picture turns up
WANTED = [
    ('daibutsu_face',  ['東大寺 大仏 盧舎那仏', 'Todaiji Daibutsu Vairocana', 'Nara Daibutsu statue']),
    ('daibutsuden',    ['東大寺 大仏殿', 'Todaiji Daibutsuden hall', 'Todaiji Great Buddha Hall']),
    ('todaiji_old',    ['Todaiji old photograph Meiji', '東大寺 古写真', 'Nara Daibutsu 1870']),
    ('shosoin',        ['正倉院', 'Shosoin Todaiji', 'Shosoin treasure house']),
    ('nagonobori',     ['長登銅山', 'Naganobori copper mine', '長登銅山跡 美祢市']),
    ('koganeyama',     ['黄金山神社 涌谷', 'Koganeyama shrine Wakuya', '涌谷町 黄金山']),
    ('gyoki',          ['行基', 'Gyoki monk statue', '行基菩薩像']),
    ('shomu',          ['聖武天皇', 'Emperor Shomu', '聖武天皇 肖像']),
    ('longmen',        ['龍門石窟 奉先寺 盧舎那仏', 'Longmen Fengxian Vairocana', 'Longmen Grottoes Buddha']),
    ('renben',         ['東大寺 大仏 蓮弁', 'Todaiji lotus petal engraving', '蓮弁 線刻 東大寺']),
    ('daibutsu_print', ['奈良大仏 浮世絵', 'Nara Daibutsu woodblock print', '大仏殿 絵図']),
]

def call(url, raw=False):
    for k in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                b = r.read()
            time.sleep(GAP)
            return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                print('  ! http', e.code, flush=True); return None
            w = 90 * (k + 1); print(f'  … 429, waiting {w}s', flush=True); time.sleep(w)
        except Exception as e:
            print('  !', e, flush=True); time.sleep(30)
    return None

def api(**p):
    p.setdefault('format', 'json')
    return call('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p))

done = {json.loads(l)['name'].split('/')[-1].rsplit('.', 1)[0]
        for l in open(f'{HERE}/SOURCES.jsonl', encoding='utf-8')} if os.path.exists(f'{HERE}/SOURCES.jsonl') else set()

for key, queries in WANTED:
    if key in done:
        print('= have', key, flush=True); continue
    print('##', key, flush=True)
    picked = None
    for q in queries:
        r = api(action='query', list='search', srsearch=q, srnamespace=6, srlimit=14)
        if not r or not r.get('query', {}).get('search'):
            continue
        titles = [s['title'] for s in r['query']['search']]
        info = api(action='query', titles='|'.join(titles[:14]), prop='imageinfo',
                   iiprop='url|size|extmetadata', iiurlwidth=1920)
        if not info: continue
        pages = {p['title']: p for p in info.get('query', {}).get('pages', {}).values()}
        for t in titles:                      # keep the search engine's order
            p = pages.get(t)
            if not p or 'imageinfo' not in p: continue
            ii = p['imageinfo'][0]; m = ii.get('extmetadata', {})
            lic = m.get('LicenseShortName', {}).get('value', '')
            if not re.search(r'public domain|cc0|pd', lic, re.I): continue
            if (ii.get('width') or 0) < 1100: continue
            picked = (t, ii, m, lic); break
        if picked: break
    if not picked:
        print('  ✗ nothing public domain for', key, flush=True); continue
    t, ii, m, lic = picked
    data = call(ii.get('thumburl') or ii['url'], raw=True)
    if not data:
        print('  ✗ download failed', t, flush=True); continue
    open(f'{HERE}/raw/{key}.jpg', 'wb').write(data)
    art = re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', '')).strip() or '作者不明'
    rec = {'name': f'raw/{key}.jpg', 'source': 'Wikimedia Commons: ' + t, 'page': ii['descriptionurl'],
           'license': lic, 'author': art, 'credit': f'写真：{art}（{lic}／Wikimedia Commons）',
           'fetched': time.strftime('%Y-%m-%d')}
    open(f'{HERE}/SOURCES.jsonl', 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f'  ✓ {key} | {t} | {lic} | {art[:40]} | {ii.get("width")}x{ii.get("height")}', flush=True)
print('HUNT DONE', flush=True)
