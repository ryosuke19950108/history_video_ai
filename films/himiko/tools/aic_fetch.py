#!/usr/bin/env python3
"""Download Art Institute of Chicago images (public-domain works only, CC0) for backdrops,
logging artist, title, date and licence to SOURCES.jsonl.
  python tools/aic_fetch.py <key> <artwork_id> [<key> <artwork_id> ...]   → raw/<key>.jpg (width ≤ 1686 px, IIIF)
Wikimedia Commons is rate-limited from this container, so this is the public-domain source used instead."""
import json, sys, time, urllib.request
UA = {'User-Agent': 'history-video-ai/0.1 (educational documentary; contact via repository)'}

def get(u, raw=False):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r:
        b = r.read()
    return b if raw else json.loads(b)

a = sys.argv[1:]
for key, aid in zip(a[::2], a[1::2]):
    d = get(f'https://api.artic.edu/api/v1/artworks/{aid}?fields=id,title,artist_title,date_display,'
            'is_public_domain,image_id,credit_line,medium_display')['data']
    if not d['is_public_domain']:
        sys.exit(f'✗ {aid} {d["title"]}: not public domain')
    if not d.get('image_id'):
        sys.exit(f'✗ {aid} {d["title"]}: no image')
    url = f'https://www.artic.edu/iiif/2/{d["image_id"]}/full/1686,/0/default.jpg'
    open(f'raw/{key}.jpg', 'wb').write(get(url, raw=True))
    artist = d.get('artist_title') or '作者不詳'
    rec = {'name': f'raw/{key}.jpg', 'source': 'Art Institute of Chicago: ' + str(d['title']),
           'page': f'https://www.artic.edu/artworks/{aid}', 'license': 'Public domain (CC0)',
           'author': artist, 'date': d.get('date_display'),
           'credit': f'画像：{artist}「{d["title"]}」（シカゴ美術館、パブリックドメイン・CC0）',
           'fetched': time.strftime('%Y-%m-%d')}
    open('SOURCES.jsonl', 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('✓', key, '|', d['title'], '|', artist, '|', d.get('date_display'))
    time.sleep(2)
