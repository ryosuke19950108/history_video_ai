#!/usr/bin/env python3
"""Download the three public-domain pictures chosen from the candidate list, one at a time and patiently:
Wikimedia's file server rate-limits this container, so a 429 waits longer and tries again."""
import json, os, re, sys, time, urllib.request
UA = {'User-Agent': 'history-video-ai/0.1 (educational documentary; contact via repository)'}
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WANT = {1: ('renben', '画像：小川晴暘「大仏蓮弁線刻図」（パブリックドメイン／Wikimedia Commons）'),
        11: ('kaigen', '画像：「大仏開眼供養」東大寺大仏縁起絵巻より（パブリックドメイン／Wikimedia Commons）'),
        12: ('beams', '画像：「大仏殿の虹梁を運ぶ」東大寺大仏縁起絵巻より（パブリックドメイン／Wikimedia Commons）')}
cand = json.load(open(f'{HERE}/raw/cand/candidates.json', encoding='utf-8'))
for i, (key, credit) in WANT.items():
    if os.path.exists(f'{HERE}/raw/{key}.jpg'):
        print('= have', key, flush=True); continue
    x = cand[i]
    url = re.sub(r'/\d+px-', '/1280px-', x['url'].replace('https://thumb.wikimedia.org/', 'https://upload.wikimedia.org/').split('?')[0])
    for k in range(10):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=150) as r:
                b = r.read()
            open(f'{HERE}/raw/{key}.jpg', 'wb').write(b)
            rec = {'name': f'raw/{key}.jpg', 'source': 'Wikimedia Commons: ' + x['title'], 'page': x['page'],
                   'license': x['lic'], 'author': x['artist'], 'credit': credit, 'fetched': time.strftime('%Y-%m-%d')}
            open(f'{HERE}/SOURCES.jsonl', 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n')
            print(f'✓ {key} {len(b)//1024} KB | {x["lic"]} | {x["title"][:50]}', flush=True)
            time.sleep(90); break
        except urllib.error.HTTPError as e:
            if e.code != 429: print('  !', key, e, flush=True); break
            w = 120 * (k + 1); print(f'  … {key} 429, waiting {w}s', flush=True); time.sleep(w)
        except Exception as e:
            print('  !', key, e, flush=True); time.sleep(60)
print('THREE DONE', flush=True)
