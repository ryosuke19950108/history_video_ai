#!/usr/bin/env python3
"""Stitch GSI (国土地理院) map tiles around a point into one image (standard library + Pillow).
  python tools/gsi_tiles.py <layer> <zoom> <lat> <lon> <cols> <rows> <out.jpg>
Layers used here: seamlessphoto (空中写真), hillshademap (陰影起伏図), pale (淡色地図).
Terms: GSI tiles may be used with the credit 「出典：国土地理院」 (地理院タイル利用規約). Every fetch is logged to SOURCES.jsonl."""
import io, json, math, sys, time, urllib.request
from PIL import Image
layer, z, lat, lon, cols, rows, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
ext = 'jpg' if layer == 'seamlessphoto' else 'png'
n = 2 ** z
fx = (lon + 180) / 360 * n
fy = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
x0, y0 = int(fx) - cols // 2, int(fy) - rows // 2
img = Image.new('RGB', (cols * 256, rows * 256))
for j in range(rows):
    for i in range(cols):
        url = f'https://cyberjapandata.gsi.go.jp/xyz/{layer}/{z}/{x0+i}/{y0+j}.{ext}'
        req = urllib.request.Request(url, headers={'User-Agent': 'history-video-ai/0.1'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r: tile = Image.open(io.BytesIO(r.read())).convert('RGB')
        except Exception as e:
            print('missing', url, e); tile = Image.new('RGB', (256, 256))
        img.paste(tile, (i * 256, j * 256)); time.sleep(0.05)
img.save(out, quality=92)
# the point's pixel position inside the stitched image, for drawing on it
px, py = (fx - x0) * 256, (fy - y0) * 256
mpp = 156543.03392 * math.cos(math.radians(lat)) / n
rec = {'name': out, 'source': f'GSI tiles: {layer} z{z}', 'page': 'https://maps.gsi.go.jp/development/ichiran.html',
       'license': '国土地理院コンテンツ利用規約（出典明示で利用可・CC BY 4.0 互換）', 'credit': '出典：国土地理院（地理院タイル ' + layer + '）',
       'center': [lat, lon], 'point_px': [round(px, 1), round(py, 1)], 'm_per_px': round(mpp, 4), 'size': img.size,
       'fetched': time.strftime('%Y-%m-%d')}
open('SOURCES.jsonl', 'a').write(json.dumps(rec, ensure_ascii=False) + '\n')
print(json.dumps(rec, ensure_ascii=False))
