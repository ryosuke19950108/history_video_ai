#!/usr/bin/env python3
"""Download OFL Google Fonts subset to the characters a film uses (TECHNIQUE.md §11) → <film>/fonts/*.woff2.
  python tools/fonts_subset.py <film_dir>
Characters are collected from index.html, film.json and scenes.json, plus digits, Latin and common punctuation."""
import json, os, re, sys, urllib.parse, urllib.request
film = sys.argv[1]
text = ''.join(open(os.path.join(film, f), encoding='utf-8').read() for f in ('index.html', 'film.json', 'scenes.json') if os.path.exists(os.path.join(film, f)))
chars = set(text) | set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,:;·–—-()（）「」『』、。・〜≒≈？！%/ ')
chars = ''.join(sorted(c for c in chars if c.isprintable()))
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
want = [('Noto Serif JP', 700, 'serif700'), ('Noto Serif JP', 500, 'serif500'), ('Noto Sans JP', 700, 'sans700'), ('Noto Sans JP', 500, 'sans500'), ('IBM Plex Mono', 500, 'mono500')]
os.makedirs(os.path.join(film, 'fonts'), exist_ok=True)
for fam, wt, name in want:
    q = urllib.parse.urlencode({'family': f'{fam}:wght@{wt}', 'text': chars, 'display': 'block'})
    css = urllib.request.urlopen(urllib.request.Request('https://fonts.googleapis.com/css2?' + q, headers={'User-Agent': UA}), timeout=60).read().decode()
    urls = re.findall(r'url\((https://[^)]+)\)', css)
    if len(urls) != 1: sys.exit(f'✗ {fam} {wt}: expected one file, got {len(urls)}')
    data = urllib.request.urlopen(urllib.request.Request(urls[0], headers={'User-Agent': UA}), timeout=60).read()
    open(os.path.join(film, 'fonts', name + '.woff2'), 'wb').write(data)
    print(f'✓ {name}.woff2  {fam} {wt}  {len(data)//1024} KB')
open(os.path.join(film, 'fonts', 'OFL.txt'), 'w').write('Noto Serif JP, Noto Sans JP (Google, SIL Open Font License 1.1); IBM Plex Mono (IBM, SIL Open Font License 1.1).\nSubsets downloaded from Google Fonts for the characters this film uses.\n')
print(len(chars), 'characters')
