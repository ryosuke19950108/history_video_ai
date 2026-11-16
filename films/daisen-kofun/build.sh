#!/bin/sh
# One-command build: script.txt + tools/make_scenes.py → daisen-kofun.mp4 (+ .srt, poster.jpg).
# Needs: the Lemo-Opuscar library ($LIB, with `setup.sh deps voice`), ffmpeg 7+ on PATH (repo .tools/ffmpeg),
# and a running VOICEVOX engine (docker run -d --rm --name voicevox -p 127.0.0.1:50021:50021 voicevox/voicevox_engine:cpu-latest).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
LIB=${LIB:-$HOME/lemo-opuscar}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder"; exit 1; }
[ -x "$REPO/.tools/ffmpeg/ffmpeg" ] && export PATH="$REPO/.tools/ffmpeg:$PATH"
PY="$LIB/.venv/bin/python"
cd "$HERE"
# 1. script → one line per sentence (readings and expected transcriptions from scenes.json)
"$PY" tools/make_scenes.py >/dev/null 2>&1 || true
"$PY" "$REPO/tools/script_lines.py" script.txt lines.json --scenes scenes.json
"$PY" tools/make_scenes.py
# 2. VOICEVOX narration (+ reading dictionary), then the library's speech check
"$PY" "$REPO/tools/tts_voicevox.py" lines.json voice --dict "$REPO/config/voicevox_dict.json" --pre 0.15 --post 0.2
(cd "$LIB" && "$PY" core/tts/asr_check.py "$HERE/lines.json" "$HERE/voice" --lang ja --model medium)
# 3. timeline (scene length = voice length), fonts, mix
"$PY" "$REPO/tools/build_timeline.py" "$HERE"
"$PY" "$REPO/tools/fonts_subset.py" "$HERE"
"$PY" mix.py
# 4. checks before the long render: reading time, measured style conditions
cd "$LIB"
node core/render/readcheck.mjs "$HERE"
CHK="$HERE/out/check"; rm -rf "$CHK"; mkdir -p "$CHK"
DUR=$("$PY" -c "import json;print(json.load(open('$HERE/film.json'))['dur'])")
node core/render/still.mjs "$HERE" --range "0:$DUR:1" --out "$CHK" > /dev/null
"$PY" "$REPO/tools/check_style.py" "$CHK" --film "$HERE"
# 5. picture, master, subtitles, poster
node core/render/video.mjs "$HERE" --fps 30 --workers 4 --out "$HERE/out/video.mp4"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/daisen-kofun.mp4" 30 0
"$PY" core/render/srt.py "$HERE/cues.json" "$HERE/daisen-kofun.srt"
node core/render/still.mjs "$HERE" 4 --out "$HERE/out" > /dev/null && cp "$HERE/out/t_4.jpg" "$HERE/poster.jpg"
ffmpeg -hide_banner -nostats -i "$HERE/daisen-kofun.mp4" -vf "blackdetect=d=0.1:pix_th=0.02" -an -f null - 2>&1 | grep -q black_start && { echo "✗ black frames"; exit 1; } || true
echo "✓ $HERE/daisen-kofun.mp4"
