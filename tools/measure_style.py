#!/usr/bin/env python3
"""Measure the look of reference frames as numbers (handbook part 2, "お手本を数値にする").

Usage:
  python tools/measure_style.py <frames_dir> [--glob '*_maxres[123].jpg'] [--out config/style_measurements.json]

Only the numbers are kept in the repository; the reference frames themselves stay outside it.
Metrics (all frames resized to 320x180 first, so every frame weighs the same):
  luma            mean Rec.709 luma 0-255
  dark / mid / light / bright frame ratios  (frame mean luma <50 / 50-90 / >=90 / >=150)
  saturation      mean HSV saturation 0-1 (all pixels) and of "coloured" pixels (S >= 0.15, V >= 0.15)
  cool / warm     share of coloured pixels with hue in 150-270 deg (cool) or 0-60 / 330-360 deg (warm)
  vignette        mean luma of the centre third divided by the mean luma of the outer border (>1 = darker edges)
  accents         the most frequent coloured hues (30 deg bins) with an example RGB
"""
import argparse, colorsys, glob, json, os, sys
from statistics import mean, median

import numpy as np
from PIL import Image


def frame_stats(path):
    im = Image.open(path).convert('RGB').resize((320, 180), Image.BILINEAR)
    a = np.asarray(im).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    luma = (0.2126 * r + 0.7152 * g + 0.0722 * b) * 255
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # hue in degrees
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    coloured = (sat >= 0.15) & (mx >= 0.15)
    hc = h[coloured]
    cool = float(((hc >= 150) & (hc < 270)).mean()) if hc.size else 0.0
    warm = float(((hc < 60) | (hc >= 330)).mean()) if hc.size else 0.0
    H, W = luma.shape
    centre = luma[H // 3:2 * H // 3, W // 3:2 * W // 3].mean()
    bw = W // 10
    border = np.concatenate([luma[:, :bw].ravel(), luma[:, -bw:].ravel(), luma[:H // 10].ravel(), luma[-H // 10:].ravel()]).mean()
    bins = {}
    if hc.size:
        rgb = a[coloured]
        idx = (hc // 30).astype(int)
        for k in np.unique(idx):
            sel = idx == k
            bins[int(k)] = (int(sel.sum()), [int(x) for x in (np.median(rgb[sel], axis=0) * 255)])
    return {
        'file': os.path.basename(path), 'luma': float(luma.mean()), 'sat': float(sat.mean()),
        'sat_coloured': float(sat[coloured].mean()) if coloured.any() else 0.0,
        'coloured_share': float(coloured.mean()), 'cool': cool, 'warm': warm,
        'vignette': float(centre / max(border, 1e-3)), 'bins': bins,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('frames_dir')
    ap.add_argument('--glob', default='*_maxres[123].jpg')
    ap.add_argument('--out', default='config/style_measurements.json')
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.frames_dir, a.glob)))
    if not files:
        sys.exit(f'no frames match {a.glob} in {a.frames_dir}')
    st = [frame_stats(f) for f in files]
    n = len(st)
    L = [s['luma'] for s in st]
    hue_total = {}
    for s in st:
        for k, (cnt, rgb) in s['bins'].items():
            t = hue_total.setdefault(k, [0, []])
            t[0] += cnt; t[1].append(rgb)
    tot = sum(v[0] for v in hue_total.values()) or 1
    accents = sorted(({'hue_deg': f'{k*30}-{k*30+30}', 'share': round(v[0] / tot, 3),
                       'example_rgb': [int(median(c[i] for c in v[1])) for i in range(3)]}
                      for k, v in hue_total.items()), key=lambda x: -x['share'])[:5]
    res = {
        'source': 'reference channel frames (in-video auto frames at ~25/50/75 %; thumbnails excluded)',
        'frames': n, 'videos': len({s['file'].rsplit('_maxres', 1)[0] for s in st}),
        'luma_mean': round(mean(L), 1), 'luma_median': round(median(L), 1),
        'dark_ratio': round(sum(l < 50 for l in L) / n, 3),
        'mid_ratio': round(sum(50 <= l < 90 for l in L) / n, 3),
        'light_ratio': round(sum(l >= 90 for l in L) / n, 3),
        'bright_ratio': round(sum(l >= 150 for l in L) / n, 3),
        'saturation_mean': round(mean(s['sat'] for s in st), 3),
        'saturation_coloured_mean': round(mean(s['sat_coloured'] for s in st), 3),
        'coloured_pixel_share': round(mean(s['coloured_share'] for s in st), 3),
        'cool_share_of_coloured': round(mean(s['cool'] for s in st), 3),
        'warm_share_of_coloured': round(mean(s['warm'] for s in st), 3),
        'vignette_centre_over_edge': round(median(s['vignette'] for s in st), 2),
        'accent_hues': accents,
    }
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(res, open(a.out, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
