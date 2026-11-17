# Lamplit Archive — decisions (MY-STYLES, "start from a blank page")

Technique base: `visual-investigation`. Borrowed: `paper-lantern` (dissolve, light off/on), `map-explainer` (dissolve between map scales).
The user chose "decide with recommendations" (MY-STYLES §2: "you decide"); each row is a recommendation, shown to the user once with the test film.

| Section | Base (Visual Investigation) | Now | Why |
|---|---|---|---|
| §1 Essence | sources meet on one event clock | one finding per sentence; the dark is the medium | ancient-history topics have no shared clock; 20-min films are built sentence by sentence |
| §2 Materials | all sources greyscale | photos keep colour under a warm grade; maps inverted dark | measured reference: coloured pixels 15 %, warm 55 % |
| §3 Colour | one red accent | gold (numbers/names), red (markers), teal (measured drawing) | measured warm-dominant look; diagrams need a cool line |
| §4 Type | Noto Sans SC / Plex Mono / Source Serif | Noto Serif JP headings, Noto Sans JP subtitles, Plex Mono tags | Japanese channel; serif headings |
| §4 Subtitles | bilingual, two lines | one Japanese line, always on | channel language; always-on subtitles (measured reference) |
| §5 Motion | cut-ins with white flash | rise in opacity, drawn strokes | the dark look; white flashes break the light-frame condition |
| §6 Transitions | hard cuts on a 0.5 s grid, no dissolves | lamp-dim dissolve (0.7 s) | user decision: fades, confirmed in the reference channel |
| §7 Sound | pizzicato, clockwork tick | warm drone, bell per finding, paper | no clock; calm long-form listening |
| §8 Native moves | freeze/circle, sync grid, evidence map | locator ring, measured outline, highlighted source line, source meets measurement, year band | — (new) |
| §7 Sound (cuts) | — | no swish at scene changes (`sound.transition_sound: false`) | user decision 2026-11-17: 「画面切り替わる音は無くして」 |
| §4 Type (size) | — | on-screen text ×1.15, at least 26 px; subtitles 44 px (`type.text_scale`, `type.text_min_px`, `type.subtitle_px`) | user decision 2026-11-17: 「テキストがやや小さいので次回から大きく」 |
| Voice | Kokoro `am_michael` | VOICEVOX 青山龍星 (`config/style.json` sound.*) | user decision (the same voice as the reference channel; everything else about the channel is our own) |
| Length | 60 s | about 20 min (tests 30–60 s) | channel format |
