#!/usr/bin/env python3
"""raw/ GSI stitches → assets/*.jpg + assets.json (zoom and global pixel origin, so the page can place any lat/lon).
Origins are recovered from SOURCES.jsonl (centre lat/lon and its pixel position in the stitch)."""
import json, math
from PIL import Image
recs = {json.loads(l)['name']: json.loads(l) for l in open('SOURCES.jsonl', encoding='utf-8')}
meta = {}
for name, r in recs.items():
    key = name.split('/')[-1].rsplit('.', 1)[0]
    z = int(r['source'].split(' z')[-1]); lat, lon = r['center']; n = 2 ** z
    fx = (lon + 180) / 360 * n * 256
    fy = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n * 256
    im = Image.open(name).convert('RGB')
    if 'USA10' in r['source'] or 'old10' in r['source']: im = im.convert('L').convert('RGB')
    im.save(f'assets/{key}.jpg', quality=88)
    meta[key] = {'f': f'assets/{key}.jpg', 'z': z, 'gx0': round(fx - r['point_px'][0], 2), 'gy0': round(fy - r['point_px'][1], 2),
                 'mpp': r['m_per_px'], 'w': im.width, 'h': im.height, 'layer': r['source'].split(': ')[1].split(' ')[0], 'credit': r['credit']}
json.dump(meta, open('assets.json', 'w'), ensure_ascii=False, indent=1)
print('\n'.join(f'{k}: z{v["z"]} {v["w"]}x{v["h"]} {v["layer"]}' for k, v in meta.items()))
