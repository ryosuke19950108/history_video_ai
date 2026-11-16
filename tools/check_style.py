#!/usr/bin/env python3
"""Check a film against the measured conditions in config/style.json (handbook 11-4: the ratios are guaranteed by a program,
not by the AI's good intentions).

  python tools/check_style.py <stills_dir> [--film <film_dir>]

<stills_dir> holds frames sampled across the film (e.g. `node core/render/still.mjs <film> --range 0:<dur>:1 --out <dir>`).
With --film, also checks every sentence length and that every scene has a subtitle. Exit 1 when a condition fails."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_style import frame_stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, 'config/style.json')))['conditions']
files = sorted(glob.glob(os.path.join(sys.argv[1], '*.jpg')))
if not files:
    sys.exit('no stills')
st = [frame_stats(f) for f in files]
n = len(st)
L = [s['luma'] for s in st]
cool = sum(s['cool'] for s in st) / n; warm = sum(s['warm'] for s in st) / n
res = {
    'frames': n,
    'luma_mean': round(sum(L) / n, 1),
    'light_ratio': round(sum(l >= 90 for l in L) / n, 3),
    'bright_ratio': round(sum(l >= 150 for l in L) / n, 3),
    'warm_over_cool': round(warm / max(cool, 1e-6), 2),
    'coloured_share': round(sum(s['coloured_share'] for s in st) / n, 3),
    'vignette': round(sorted(s['vignette'] for s in st)[n // 2], 2),
}
checks = [
    ('平均輝度', res['luma_mean'] <= C['frame_luma_mean_max'], f"{res['luma_mean']} ≤ {C['frame_luma_mean_max']}"),
    ('明るいコマ（輝度90以上）の割合', res['light_ratio'] <= C['light_frame_ratio_max'], f"{res['light_ratio']} ≤ {C['light_frame_ratio_max']}"),
    ('非常に明るいコマ（150以上）の割合', res['bright_ratio'] <= C['bright_frame_ratio_max'], f"{res['bright_ratio']} ≤ {C['bright_frame_ratio_max']}"),
    ('暖色/寒色', res['warm_over_cool'] >= C['warm_over_cool_min'], f"{res['warm_over_cool']} ≥ {C['warm_over_cool_min']}"),
    ('色の乗った画素の割合', C['coloured_share_range'][0] <= res['coloured_share'] <= C['coloured_share_range'][1], f"{res['coloured_share']} in {C['coloured_share_range']}"),
    ('周辺減光（中央/縁）', C['vignette_range'][0] <= res['vignette'] <= C['vignette_range'][1], f"{res['vignette']} in {C['vignette_range']}"),
]
if '--film' in sys.argv:
    film = json.load(open(os.path.join(sys.argv[sys.argv.index('--film') + 1], 'film.json'), encoding='utf-8'))
    lo, hi = C['scene_chars_range']
    bad = [s['id'] for s in film['scenes'] if not lo <= len(s['line']) <= hi]
    checks.append(('1文の文字数', not bad, f'{lo}-{hi} 字' + (f'（外れ: {bad}）' if bad else '')))
    nosub = [s['id'] for s in film['scenes'] if not any(a < s['t1'] and b > s['t0'] for a, b, _ in film['subs'])]
    checks.append(('字幕の常時表示', not nosub, 'every scene has a cue' + (f'（なし: {nosub}）' if nosub else '')))
light = [os.path.basename(f) for f, l in zip(files, L) if l >= 90]
ok = all(c[1] for c in checks)
for name, good, detail in checks:
    print(f"{'OK ' if good else 'NG '} {name}: {detail}")
if light:
    print('  明るいコマ:', ', '.join(light))
print(json.dumps(res, ensure_ascii=False))
sys.exit(0 if ok else 1)
