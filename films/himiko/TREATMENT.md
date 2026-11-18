# TREATMENT — 卑弥呼の正体（約21分）

Style: my-styles/lamplit-archive (same as nihonjin-roots, with the 2026-11-17 decisions: no transition swish, larger text).
Script: the channel owner's (SCRIPT_SOURCE.txt, from the Gist in SCRIPT_URL.txt), 254 sentences, read unchanged.
Voice: VOICEVOX 青山龍星.

## Structure (given by the script)
Hook（日本の歴史書に名前がない）→ the viewer's guess → 魏志倭人伝で確かに分かること（道のり・倭国の乱・金印・鏡・壹与）→
300年の論争史（白石・宣長・内藤・白鳥）→ 2つのルールと4つの物差し（各5点・20点満点）→
01 天照大神 12点 → 02 神功皇后 13点 → 03 九州の女王 13点 → channel → 04 倭迹迹日百襲姫 15点 →
最終採点 → 3つの弱点 → 結論と締め。

The spine is a scoreboard (`mysteries` layout, `board` in scenes.json): the four candidates with their running totals.
Because the script withholds the fourth name until s177 (「まだ1度も名前が出ていません」), the board shows 「？」 for
candidate 4 until then; `index.html` was given a per-scene `names` and `marks` override for exactly this.

## Visual plan (one sentence = one scene; tools/make_scenes.py)
| Kind | Use |
|---|---|
| bars | the scoring — four measures at 5 points each, revealed in the order the narration gives them, then the final ranking |
| mysteries | the spine: four candidates, 採点ずみ with the score in place of the mark |
| map | East Asia from Natural Earth: 帯方郡→対馬→壱岐→九州の道のり, the sea the literal distances run into, 239年の遣使, 遼東, 狗奴国, 纒向に集まる土器 |
| photo | GSI aerials of the places named (志賀島, 石上神宮, 山門, 平原, 吉野ヶ里, 三輪山, 大神神社, 纒向, 箸墓) |
| timeline | 倭国の乱（146–189）, 論争の300年, 纒向の桃の種（135–230）と箸墓（3世紀中ごろ） |
| rows / theories / calc / card / doc / comment | the measures, the competing readings, the 120年のずれ, the turns of the argument, 魏志倭人伝と日本書紀の原文 |
| chapter | one per candidate (label CANDIDATE) |

箸墓古墳 (daisen-kofun) and 吉野ヶ里 (nihonjin-roots) aerials are reused; the rest were fetched for this film.

## Sound
Same score as nihonjin-roots (warm drone, chord change at each chapter card, bells when a candidate is scored),
without the transition swish.
