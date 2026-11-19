#!/usr/bin/env python3
"""Look for a usable photograph of the Nara Great Buddha on Wikimedia Commons: public domain, CC0 or CC BY
(never share-alike, which would bind the whole film). Commons rate-limits this container hard, so every call
waits and a 429 waits longer. Candidates are downloaded to raw/cand/ to be looked at and chosen by hand.

  python tools/photo_hunt.py
"""
import json, os, re, time, urllib.parse, urllib.request

UA = {'User-Agent': 'history-video-ai/0.1 (educational documentary; contact via repository)'}
GAP = 35
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f'{HERE}/raw/cand'
os.makedirs(OUT, exist_ok=True)

QUERIES = [
    '東大寺 大仏 写真', 'Todaiji Daibutsu bronze statue photograph', 'Nara Daibutsu 19th century photograph',
    'Great Buddha Nara albumen photograph', 'Todaiji Vairocana bronze Nara', '東大寺 大仏殿 写真',
    'Daibutsuden Todaiji hall photograph', 'Nara Todaiji Meiji photograph',
]
OK_LIC = re.compile(r'public domain|cc0|^cc by [0-9.]+$|pd-', re.I)
BAD_LIC = re.compile(r'share.?alike|cc by-sa|gfdl', re.I)

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
            w = 75 * (k + 1); print(f'  … 429, waiting {w}s', flush=True); time.sleep(w)
        except Exception as e:
            print('  !', e, flush=True); time.sleep(25)
    return None

def api(**p):
    p.setdefault('format', 'json')
    return call('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(p))

seen, found = set(), []
for q in QUERIES:
    print('##', q, flush=True)
    r = api(action='query', list='search', srsearch=q, srnamespace=6, srlimit=16)
    if not r or not r.get('query', {}).get('search'): continue
    titles = [s['title'] for s in r['query']['search'] if s['title'] not in seen]
    seen.update(titles)
    titles = [t for t in titles if not t.lower().endswith(('.pdf', '.svg', '.tif', '.webm', '.ogv'))]
    if not titles: continue
    info = api(action='query', titles='|'.join(titles[:16]), prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=2000)
    if not info: continue
    for p in info.get('query', {}).get('pages', {}).values():
        ii = (p.get('imageinfo') or [{}])[0]; m = ii.get('extmetadata', {})
        lic = m.get('LicenseShortName', {}).get('value', '')
        if BAD_LIC.search(lic) or not OK_LIC.search(lic): continue
        if (ii.get('width') or 0) < 1200: continue
        art = re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', '')).strip() or '作者不明'
        found.append({'title': p['title'], 'lic': lic, 'artist': art[:60], 'w': ii['width'], 'h': ii['height'],
                      'url': ii.get('thumburl') or ii['url'], 'page': ii['descriptionurl'],
                      'date': re.sub('<[^>]+>', '', m.get('DateTimeOriginal', {}).get('value', ''))[:40]})
        print(f'  + {p["title"][:60]} | {lic} | {art[:30]} | {ii["width"]}x{ii["height"]}', flush=True)

json.dump(found, open(f'{OUT}/candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'--- {len(found)} candidates; downloading', flush=True)
for i, c in enumerate(found[:10]):
    data = call(c['url'], raw=True)
    if not data: continue
    open(f'{OUT}/c{i:02d}.jpg', 'wb').write(data)
    print(f'  ↓ c{i:02d}.jpg  {c["title"][:60]}', flush=True)
print('PHOTO HUNT DONE', flush=True)
