# FACTS — 出雲大社 48メートルの神殿

The script is the channel owner's (SCRIPT_SOURCE.txt, from the Gist in SCRIPT_URL.txt); the narration reads it unchanged.
This file records what was checked before numbers were put on screen, and what is drawn as a schematic.

## Numbers shown on screen
| Claim in the script | Note |
|---|---|
| 今の本殿 1744年（延享元年）, 国宝, 高さ約24 m（8丈） | standard description of the present honden |
| 平成の大遷宮 2013年 | 本殿遷座祭 2013-05 |
| 杵築大社 → 出雲大社（明治の初め）, 出雲国風土記 733年 | 風土記 出雲郡 杵築郷: 諸の皇神等が宮処に参集ひて杵築きたまひき（screen shows this 書き下し） |
| 32丈（約96 m）, 16丈（約48 m）, 8丈（約24 m） | the shrine's own tradition, as the script says (not a Heian record); 1丈 ≈ 3 m as the script computes |
| 東寺の五重塔 約55 m, 江戸時代の再建 | 54.8 m, rebuilt 1644 |
| 荒神谷遺跡 1984年 銅剣358本, それまで全国 約300本 | the usual description of the find |
| 加茂岩倉遺跡 1996年 銅鐸39個（1か所で最多） | matches |
| 『口遊』970年 源為憲,「雲太 和二 京三」 | 天禄元年 (970); 雲太 = 出雲の大社, 和二 = 大和の東大寺大仏殿, 京三 = 平安京の大極殿 |
| 奈良時代の大仏殿 15丈 ≈ 45 m | the script's figure (15丈 × 3 m) |
| 倒壊 1031, 1061, 1109, 1141, 1172, 鎌倉時代にも（1235）, 約200年で7度 | the script's list; the timeline shows the six years the script names and labels the span およそ200年で7度 |
| 1031年の報告は翌年うそとされ, 報告した役人は佐渡へ | 出雲守 橘俊孝, 1032年 佐渡へ配流 |
| 1235年倒壊, 1248年完成（13年） | 嘉禎元年 / 宝治二年 |
| 金輪御造営差図: 千家家に伝わる, 柱9本・各3本束ね, 金輪, 階段 1町（約109 m） | matches; 1町 ≈ 109 m |
| 2000年 八足門の前で宇豆柱, その年のうちに心御柱・側柱 | 2000-04 宇豆柱, 2000-09 心御柱 |
| 直径1 m超の杉3本 → 約3 m, 切り口 約4 m², 畳1枚 1.6 m² → 2枚半 | arithmetic as in the script; the pillar drawing uses these numbers |
| 柱は1248年の造営の可能性が高い | dating reported for the pillars (鎌倉時代中期) |
| 古代出雲歴史博物館, 10ぶんの1の模型 | matches |
| 大林組 + 福山敏男 監修の復元図, 福山敏男 1955年 | the script's statement |

## Drawn, not measured
- 高さの図 (heights): bars to one scale from the script's numbers; floor lines are 1階 ≈ 3 m, as the script counts (16階建て, 30階建て).
- 図面の図 (plan): a schematic of the 金輪御造営差図 (9 pillars, 3 logs each, iron rings), not a tracing; the stair drawing uses 13 m for the hall and 109 m for the stair.
- 柱の図 (pillar): three circles of 1.36 m in a 3 m bundle; people and tatami to the same scale; stones are a schematic.
- Maps are drawn from Natural Earth 1:50m land (public domain); the route to Sado is a schematic.
- Site positions from the GSI place-name search (荒神谷遺跡, 古代出雲歴史博物館) and from the aerials (本殿, 八足門, 稲佐の浜, 八雲山).

## Readings fixed for VOICEVOX (kana checked for all 247 lines)
The user's list (2026-11-20) is in config/voicevox_dict.json (出雲大社 → いずもたいしゃ, not おおやしろ). Also fixed in tools/say.py:
都 (と → みやこ), 1丈 / 32丈 (たけ → じょう), 1町 (いちまち → いっちょう), 雲太 (くもふと → うんた), 傾かない (かたぶ → かたむ), 一目 (いちもく → ひとめ), 黒々 (くろ → くろぐろ).
