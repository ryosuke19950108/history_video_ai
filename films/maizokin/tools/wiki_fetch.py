#!/usr/bin/env python3
"""Pictures for the film, taken from the lead image of a Japanese Wikipedia article.

  python tools/wiki_fetch.py            # works through WANTED below → raw/<key>.jpg + SOURCES.jsonl

commons.wikimedia.org's API rate-limits this container's shared address to a standstill (HTTP 429 on every
call, see tools/commons_hunt.py), but ja.wikipedia.org's API answers normally and resolves files held on
Commons, and the files themselves come from upload.wikimedia.org. Only public domain, CC0 and CC BY are
taken: share-alike would bind the whole film, so it is refused along with everything else.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = {'User-Agent': 'history-video-ai/0.1 (educational documentary; contact via repository)'}
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OK = re.compile(r'public domain|^cc0|^cc[ -]by[ -]\d|^cc[ -]by$|^pd', re.I)
NO = re.compile(r'share.?alike|cc[ -]by[ -]sa|gfdl|non.?commercial|fair use', re.I)

# key → the article whose lead picture is wanted
WANTED = [
    ('oguri',       '小栗忠順'),
    ('katsu',       '勝海舟'),
    ('saigo',       '西郷隆盛'),
    ('togo',        '東郷平八郎'),
    ('itagaki',     '板垣退助'),
    ('kanrinmaru',  '咸臨丸'),
    ('ieyasu',      '徳川家康'),
    ('shingen',     '武田信玄'),
    ('koban_kei',   '慶長小判'),
    ('koban',       '小判'),
    ('senryobako',  '千両箱'),
    ('oban',        '大判'),
    ('edojo',       '江戸城'),
    ('toshogu',     '日光東照宮'),
    ('akagi',       '赤城山'),
    ('yokosuka',    '横須賀造船所'),
    ('gokinzo',     '御金蔵'),
    ('manen',       '万延二分金'),
    ('tobafushimi', '鳥羽・伏見の戦い'),
    ('kaido',       '中山道'),
]


def api(host, **p):
    p.setdefault('format', 'json'); p.setdefault('formatversion', '2')
    u = f'https://{host}/w/api.php?' + urllib.parse.urlencode(p)
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(20 * (k + 1))
    raise SystemExit('rate limited: ' + u)


def grab(u):
    # upload.wikimedia.org serves cached thumbnails at a fixed set of widths and rate-limits any other size
    # hard (it says so in the 429 body), so only the widths it lists are ever asked for.
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            w = 25 * (k + 1); print(f'  … 429, waiting {w}s', flush=True); time.sleep(w)
    return None


done = {json.loads(l)['name'].split('/')[-1].rsplit('.', 1)[0]
        for l in open(f'{HERE}/SOURCES.jsonl', encoding='utf-8')} if os.path.exists(f'{HERE}/SOURCES.jsonl') else set()

for key, art in WANTED:
    if key in done:
        print('= have', key); continue
    pg = api('ja.wikipedia.org', action='query', titles=art, prop='pageimages', piprop='name', pilicense='any')['query']['pages'][0]
    fname = pg.get('pageimage')
    if not fname:
        print(f'  ✗ {key}: {art} に代表画像がありません'); continue
    q = api('ja.wikipedia.org', action='query', titles='File:' + fname, prop='imageinfo',
            iiprop='url|size|extmetadata|user', iiurlwidth=1024)['query']['pages'][0]
    ii = (q.get('imageinfo') or [None])[0]
    if not ii:
        print(f'  ✗ {key}: {fname} の情報が取れません'); continue
    m = ii.get('extmetadata', {})
    lic = m.get('LicenseShortName', {}).get('value', '')
    if NO.search(lic) or not OK.search(lic):
        print(f'  ✗ {key}: {fname} のライセンスは {lic!r} — 使いません'); continue
    if (ii.get('width') or 0) < 600:
        print(f'  ✗ {key}: {fname} は {ii.get("width")} px しかありません'); continue
    src = ii.get('thumburl') or ii['url']
    ext = 'png' if src.lower().endswith('.png') else 'jpg'
    data = grab(src)
    if not data:
        print(f'  ✗ {key}: {fname} を取得できませんでした（429）', flush=True); continue
    open(f'{HERE}/raw/{key}.{ext}', 'wb').write(data)
    art_name = re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', '')).strip() or '作者不明'
    art_name = re.sub(r'\s+', ' ', art_name)[:60]
    ja = 'パブリックドメイン' if re.search(r'public domain|^pd', lic, re.I) else lic
    rec = {'name': f'raw/{key}.{ext}', 'source': 'Wikimedia Commons: File:' + fname,
           'page': 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(fname.replace(' ', '_')),
           'license': lic, 'author': art_name, 'credit': f'画像：{art_name}（{ja}／Wikimedia Commons）',
           'via': 'ja.wikipedia.org API（' + art + ' の代表画像）', 'fetched': time.strftime('%Y-%m-%d')}
    open(f'{HERE}/SOURCES.jsonl', 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f'  ✓ {key} | {fname} | {lic} | {art_name[:34]} | {ii.get("width")}x{ii.get("height")}')
    time.sleep(1)
print('FETCH DONE')
