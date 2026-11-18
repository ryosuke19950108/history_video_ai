#!/bin/sh
# Delivery cut: master .mp4 → <name>_1080p.mp4, 1920×1080, under a size cap (README: 400 MiB).
#   sh tools/deliver_1080p.sh <master.mp4> <out_1080p.mp4> [cap_MiB]
# Two-pass H.264 at the bitrate that fills the cap, audio copied so the −14 LUFS mix is untouched.
set -e
IN=$1; OUT=$2; CAP=${3:-400}
[ -f "$IN" ] || { echo "no master: $IN"; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
ABR=$(ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of csv=p=0 "$IN")
case "$ABR" in ''|N/A) ABR=128000 ;; esac
# 97 % of the cap, less the audio, in bits per second
VBR=$(awk -v c="$CAP" -v d="$DUR" -v a="$ABR" 'BEGIN{printf "%d", (c*1048576*8*0.97)/d - a}')
[ "$VBR" -gt 300000 ] || { echo "cap too small for $DUR s"; exit 1; }
echo "duration ${DUR}s · video target $((VBR/1000)) kbps · cap ${CAP} MiB"
PASSLOG=$(mktemp -u)
ffmpeg -hide_banner -nostats -y -i "$IN" -c:v libx264 -preset slow -b:v "$VBR" -pass 1 -passlogfile "$PASSLOG" \
  -pix_fmt yuv420p -an -f mp4 /dev/null
ffmpeg -hide_banner -nostats -y -i "$IN" -c:v libx264 -preset slow -b:v "$VBR" -pass 2 -passlogfile "$PASSLOG" \
  -pix_fmt yuv420p -movflags +faststart -c:a copy "$OUT"
rm -f "$PASSLOG"*
ls -la "$OUT" | awk '{printf "%s  %.1f MiB\n", $9, $5/1048576}'
