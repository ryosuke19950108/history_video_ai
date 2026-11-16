# Lamplit Archive — our demo (test film)

One example among many. Don't reuse its story, arc, shots, props or timings.

Demo: *箸墓古墳は誰の墓か* (Whose Tomb Is Hashihaka?, 59.6 s) · source and build in `films/hashihaka-test/` (`sh build.sh`), film not committed (rebuild it). Style frame: `styleframe.jpg` (10.5 s), poster: `test.jpg`.

- **Story**: place → mound → legend → the question → two theories → source meets measurement → dates → still unknown.
- **Shots**: one layout per sentence (TREATMENT.md in the film folder); every native move of STYLE.md §8 appears once.
- **Palette & props**: exactly `config/style.json`; drawn props are the locator ring, the keyhole outline, the 100 m bar, the 150 m circle, the year axis.
- **Score**: synthesized drone in fifths, bells on findings, near-silence before the question (mix.py).
- **Build notes**: `script.txt` → `tools/script_lines.py` → `tools/tts_voicevox.py` (VOICEVOX 玄野武宏) → `core/tts/asr_check.py --lang ja --model medium` → `tools/build_timeline.py` → `index.html` (render(t)) → `tools/check_style.py` (measured conditions) → `core/render/video.mjs` → `core/render/mux.sh`.
- **Which file draws what**: `index.html` layouts `L.map_locator … L.pull_out`, `lamp()` (lamp + vignette), dissolve in `window.render`.
