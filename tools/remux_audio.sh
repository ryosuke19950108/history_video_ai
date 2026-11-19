#!/bin/sh
# Replace a finished film's soundtrack without touching its picture:
#   sh tools/remux_audio.sh film.mp4 mix.wav out.mp4
# The picture is copied stream to stream, so it stays exactly the frames that were already checked,
# and only the audio is encoded again. The audio goes through the same chain as core/render/mux.sh:
# two-pass loudnorm to −14 LUFS / TP −1.2, then a 4× oversampled limiter whose look-ahead is taken
# back, then AAC 256k. Use it when the mix had to be rebuilt (a timeline change) but the picture did not.
set -e
LC_ALL=C; export LC_ALL
die() { echo "remux_audio.sh: $*" >&2; exit 1; }
V="$1"; A="$2"; O="$3"
[ -n "$V" ] && [ -n "$A" ] && [ -n "$O" ] || die "usage: sh tools/remux_audio.sh film.mp4 mix.wav out.mp4"
[ -f "$V" ] || die "film not found: $V"
[ -f "$A" ] || die "audio not found: $A"
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || die "ffmpeg 7+ is needed on PATH"

M=$(ffmpeg -hide_banner -nostats -i "$A" -af loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json -f null - 2>&1) \
  || die "ffmpeg cannot read the audio '$A'"
J=$(echo "$M" | sed -n '/{/,/}/p')
g() { echo "$J" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
for k in input_i input_tp input_lra input_thresh target_offset; do
  case "$(g $k)" in ''|*inf*|*nan*) die "could not measure the loudness of '$A'";; esac
done
LN="loudnorm=I=-14:TP=-1.2:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true"

dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" 2>/dev/null | head -1; }
VD=$(dur "$V"); AD=$(dur "$A"); PAD=""
if awk -v a="$AD" -v v="$VD" 'BEGIN { exit !(a + 0 > 0 && v + 0 > 0 && a + 0 < v - 0.02) }'; then
  PAD=",apad=whole_dur=$VD"
  echo "remux_audio.sh: note: the audio ($AD s) is shorter than the picture ($VD s); padding it with silence" >&2
fi
# a mix much longer than the picture means the two were built from different timelines: that is the
# very fault this script is usually called to repair, so say so rather than quietly cutting it short
if awk -v a="$AD" -v v="$VD" 'BEGIN { exit !(a + 0 > v + 1.0) }'; then
  echo "remux_audio.sh: warning: the audio ($AD s) is more than a second longer than the picture ($VD s);" >&2
  echo "  they look like different timelines. Rebuild the mix from the film.json the picture was drawn from." >&2
fi

CEIL=-1.6
lim() { echo ",aresample=192000,alimiter=limit=$(awk -v d="$1" 'BEGIN { printf "%.4f", 10 ^ (d / 20) }'):attack=10:release=200:level=disabled:latency=1"; }
TMP="$O.$$.part.mp4"
trap 'rm -f "$TMP"' EXIT
ffmpeg -y -loglevel error -i "$V" -i "$A" \
  -filter_complex "[1:a]$LN$(lim $CEIL),aresample=48000$PAD[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart -shortest "$TMP" \
  || die "ffmpeg failed while writing '$O'"
[ -s "$TMP" ] || die "nothing was written to '$O'"
mv -f "$TMP" "$O"

measure() { ffmpeg -hide_banner -nostats -i "$O" -vn -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|LRA|Peak):" | head -3; }
R=$(measure); N=0
while [ $N -lt 3 ]; do
  OP=$(echo "$R" | awk '$1 == "Peak:" { print $2 }')
  [ -n "$OP" ] || break
  awk -v p="$OP" 'BEGIN { exit !(p + 0 > -1) }' || break
  CEIL=$(awk -v c="$CEIL" -v p="$OP" 'BEGIN { printf "%.2f", c - (p + 1.3) }'); N=$((N + 1))
  echo "remux_audio.sh: note: true peak $OP dB; encoding the audio again with the limiter at $CEIL dBFS" >&2
  ffmpeg -y -loglevel error -i "$O" -i "$A" -filter_complex "[1:a]$LN$(lim $CEIL),aresample=48000$PAD[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart -shortest "$TMP" \
    || die "ffmpeg failed while encoding the audio of '$O' again"
  mv -f "$TMP" "$O"
  R=$(measure)
done
echo "$O"
echo "$R"
OI=$(echo "$R" | awk '$1 == "I:" { print $2 }'); OP=$(echo "$R" | awk '$1 == "Peak:" { print $2 }')
awk -v i="$OI" -v p="$OP" 'BEGIN { exit !(i + 0 < -15 || i + 0 > -13 || p + 0 > -1) }' \
  && echo "remux_audio.sh: warning: missed the target (-14 LUFS, true peak <= -1 dB): measured $OI LUFS, peak $OP dB" >&2
exit 0
