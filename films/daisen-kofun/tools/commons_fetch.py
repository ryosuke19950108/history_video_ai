#!/usr/bin/env python3
"""Download Wikimedia Commons files (public domain / CC0 only) for backdrops, logging author, licence and page to SOURCES.jsonl.
  python tools/commons_fetch.py <key> "<File title>" [<key> "<File title>" ...]   → raw/<key>.jpg (longest side ≤ 2400 px)"""
import json, re, sys, time, urllib.parse, urllib.request
UA = {'User-Agent': 'history-video-ai/0.1 (educational documentary; contact via repository)'}
def get(u, raw=False):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r: b = r.read()
            return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(30 * (k + 1))
    raise SystemExit('rate limited: ' + u)
a = sys.argv[1:]
for key, title in zip(a[::2], a[1::2]):
    q = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'titles': 'File:' + title, 'prop': 'imageinfo',
            'iiprop': 'url|size|extmetadata', 'iiurlwidth': 2400, 'format': 'json'}))
    ii = next(iter(q['query']['pages'].values()))['imageinfo'][0]; m = ii['extmetadata']
    lic = m.get('LicenseShortName', {}).get('value', '')
    if not re.search(r'public domain|cc0|pd', lic, re.I): sys.exit(f'✗ {title}: licence {lic} (only public domain / CC0 are fetched)')
    url = ii.get('thumburl') if ii['width'] > 2400 else ii['url']
    open(f'raw/{key}.jpg', 'wb').write(get(url, raw=True))
    art = re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', '')).strip()
    rec = {'name': f'raw/{key}.jpg', 'source': 'Wikimedia Commons: ' + title, 'page': ii['descriptionurl'], 'license': lic, 'author': art,
           'credit': f'写真：{art}（{lic}／Wikimedia Commons）', 'fetched': time.strftime('%Y-%m-%d')}
    open('SOURCES.jsonl', 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n'); print('✓', key, lic, art[:40]); time.sleep(8)
