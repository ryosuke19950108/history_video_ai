# Lamplit Archive（灯下の資料室） — Style Prompt (draft)

> History, ancient civilisations and archaeology told as a quiet investigation under one lamp. Real maps, aerial photographs, site plans and the words of the old sources rise out of a warm darkness, are checked against each other one finding at a time, and sink back into the dark. Serif headings, an always-on subtitle line, every source named on screen. Long-form (about 20 minutes) built from many short scenes: one sentence, one scene.
> References (grammar only): museum-gallery documentaries, archive-based history channels, forensic reconstructions. Never copy their names, logos, title cards, set phrases, thumbnails or voices.

Technique base: Visual Investigation (library `visual-investigation`). Borrowed moves: the dissolve timing and "light off / on" of Paper-cut Lightbox (`paper-lantern`), the dissolve between map scales of 3D Map Explainer (`map-explainer`). All measured values and conditions live in `config/style.json`; this file never repeats a number that file owns.

## 1. Essence, and what it is not

1. **One finding per scene, one sentence per scene.** Each narrated sentence is a scene; its picture shows exactly the evidence the sentence talks about.
2. **The dark is the medium.** The frame is mostly warm near-black; sources are lit like objects under a lamp (vignette, falloff). Transitions dim into that dark and the next layout rises out of it.
3. **Sources speak for themselves.** Maps, aerial photographs and scans are shown, not redrawn; text that we only have as a transcription is typeset and labelled as such (翻刻 / 書き下し).
4. **Uncertainty is drawn.** Competing theories sit side by side in dashed boxes; dates and sizes carry `約 / 〜 / 諸説あり`; inferences are marked.
5. **Calm.** One steady narrator, no stingers, no shouting captions.

Not Visual Investigation (no single event clock, no hard-cut grid, sources keep their colour). Not a slideshow (no centred bullet lists, no page turns). Not Flat Vector animation (nothing is illustrated as vector characters). Not an AI-image documentary (no generated picture stands in for a historical one).

## 2. Materials & rendering

- Kinds of source: maps and terrain (GSI tiles, historical maps), aerial and site photographs, document scans or typeset transcriptions, measured diagrams (outlines, scale bars, circles of a stated size), small data charts (year ranges).
- Photographs keep their colour under one warm grade (`grade.photo`); maps are inverted to dark line work (`grade.map`); paper cards are lit from the centre and fall off toward the edges.
- One grain on sources only, never on type or lines (`grade.grain_alpha`).
- Drawn evidence is thin line work: teal for measured outlines and diagrams, red for markers, gold for numbers.

## 3. Colour logic

Values: `palette` in `config/style.json`. Ground and panels are warm near-black; text is cream. Three accents, each with one job: **gold** = the number or name the sentence is about; **red** = a marker that points (ring, highlight, the rule under a heading); **teal** = measured drawing (outline, scale, circle of a stated size). Warm hues dominate coloured pixels; the frame stays dark (`conditions`).

## 4. Type & subtitles

- Headings, quotes and names: Noto Serif JP 700/500. Subtitles and labels: Noto Sans JP 700/500. Source tags, readouts, years: IBM Plex Mono 500. All OFL, subset to the characters used.
- **Subtitle**: one line, bottom centre (baseline `frame.subtitle_baseline`), cream with a soft black shadow, no band; never wider than `type.subtitle_safe_width`; a long sentence becomes two cues at a 、.
- **Source line**: bottom right, small mono `出典：…`, on every frame that shows a source.
- **Theory label**: a short serif name in a dashed box with a mono caption above it.
- Reading time: CJK ÷ 4.5 + 1.5 s for every key text (`readcheck.mjs`).

## 5. Motion quality

- 30 fps. The lamp-dim dissolve (`motion.transition_s`) is the only transition between scenes; inside a scene, things are drawn (rings clockwise, outlines stroke by stroke, highlights wiped) or rise in opacity with a small lift.
- Slow pushes only (`motion.photo_push_max`, `motion.map_push_max`); the camera never whips or shakes.

## 6. Shot & layout grammar

- 1920×1080, margins `frame.margin`; content above `frame.content_bottom`; subtitles below.
- Layouts: **map with locator ring** · **photo with drawn outline + number** · **document card with highlighted line** · **one-line question card** (the breath) · **two theories side by side** · **document + measured photo** (a source meets a measurement) · **year band** (ranges on a short axis, contested range dashed) · **pull-out ending** · **end card with sources**.
- One layout per sentence; text kept to what the sentence needs.

## 7. Sound palette

A low warm drone (fifths, filtered), a soft bell for each finding, paper rustle for document cards, a low thump after the question's silence; the narrator in front, music about `sound.music_below_voice_db` dB under the voice. At least one near-silence before the turn.

## 8. Native moves

- **Lamp-dim dissolve** — the outgoing layout dims toward the ground while the next rises out of it.
- **Locator ring** — a red ring drawn clockwise on the map at the site, a lower-third name and place.
- **Measured outline** — a teal outline traced over the aerial photograph, a scale bar and the number in gold.
- **Highlighted source line** — the decisive words wiped in red on a lit paper card.
- **Source meets measurement** — a quoted size beside a circle of that size drawn on the photograph.
- **Year band** — a short axis with the proposed ranges; the disputed ones dashed.

## 9. Pitfalls

- A light frame breaks the look: keep light frames under `conditions.light_frame_ratio_max`.
- Readings of historical names: give VOICEVOX a kana `say` and register frequent names in the user dictionary.
- A claim without a source in `FACTS.md` never reaches the voice or the screen; contested numbers always carry `諸説あり`.
- No generated image as a historical picture; no reference channel's names, phrases, logos or title-card wording.

## 10. Footage & sources

GSI tiles (credit 「出典：国土地理院」), public-domain scans (NDL, Wikimedia Commons PD/CC0), CC BY with full credit. Not allowed: CC BY-SA, unclear origin, "no known restrictions". Log every fetch in `SOURCES.jsonl`.

## 11. Engine

Lemo-Opuscar core render (Canvas 2D page, `render(t)`, `TEXTS(t)`), VOICEVOX via `tools/tts_voicevox.py` (same outputs as `core/tts/tts.py`), `core/tts/asr_check.py --lang ja`, `core/audio/sfx.py`, `core/render/mux.sh`; the measured-conditions check `tools/check_style.py`.
