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
    ('koban_keicho',  ['慶長小判', 'Keicho koban', 'Koban gold coin Japan']),
    ('koban_manen',   ['万延小判', "Man'en koban", '万延元年 小判']),
    ('koban_tempo',   ['天保小判', 'Tenpo koban', '天保一分金']),
    ('oguri',         ['小栗忠順', 'Oguri Tadamasa', '小栗上野介']),
    ('katsu',         ['勝海舟', 'Katsu Kaishu']),
    ('saigo',         ['西郷隆盛', 'Saigo Takamori']),
    ('kanrinmaru',    ['咸臨丸', 'Kanrin Maru', '万延元年遣米使節']),
    ('edojo_old',     ['江戸城 古写真', 'Edo castle photograph', '江戸城 西の丸']),
    ('toshogu',       ['日光東照宮 陽明門', 'Nikko Toshogu Yomeimon', '東照宮 古写真']),
    ('akagi_photo',   ['赤城山', 'Mount Akagi', '赤城山 大沼']),
    ('yokosuka_old',  ['横須賀製鉄所', 'Yokosuka Ironworks', '横須賀造船所 明治']),
    ('togo',          ['東郷平八郎', 'Togo Heihachiro']),
    ('itagaki',       ['板垣退助', 'Itagaki Taisuke']),
    ('kaido_uma',     ['東海道 馬 浮世絵', 'Japanese pack horse ukiyo-e', '中山道 街道 浮世絵']),
    ('senryobako',    ['千両箱', 'Senryobako', '小判 木箱']),
    ('ieyasu',        ['徳川家康', 'Tokugawa Ieyasu portrait']),
    ('ginka',         ['一分銀', 'Japanese silver coin Ansei', '天保一分銀']),
    ('edo_machi',     ['江戸 町 浮世絵', 'Edo city ukiyo-e', '江戸名所図会']),
    ('shingen',       ['武田信玄', 'Takeda Shingen portrait']),
    ('mint_phila',    ['Philadelphia Mint 1860', 'United States Mint Philadelphia 19th century']),
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
