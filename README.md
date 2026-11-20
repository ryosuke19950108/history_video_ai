# history_video_ai

歴史・古代文明・考古学・歴史ミステリーの解説動画（約 20 分）を Claude Code 中心で自動制作する仕組み。
描画は [Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar) の公式レンダラー（MIT）、ナレーションは VOICEVOX。有料 API は使わない。

## 構成

| パス | 中身 |
|---|---|
| `config/style.json` | 作風の数値・条件の唯一の置き場所（パレット、グレード、動き、音量、条件） |
| `config/style_measurements.json` | お手本の実測値（`tools/measure_style.py`、`docs/style_measurements.md`） |
| `config/voicevox_dict.json` | 歴史用語の読み（VOICEVOX ユーザー辞書） |
| `my-styles/lamplit-archive/` | 自分のスタイル「灯下の資料室」（Lemo-Opuscar MY-STYLES、白紙から・技術の土台 Visual Investigation）の草案 |
| `tools/` | 台本分割、VOICEVOX、タイムライン、フォント、作風チェック |
| `films/<name>/` | 1 本ごとのプロジェクト（`script.txt` と `scenes.json` を書き、`sh build.sh`） |

## 1 本の作り方

1. `films/<name>/script.txt` に台本（1 行 1 文、30〜70 字）
2. `scenes.json` に各文の画面の型と素材（Claude Code が割り当てる）
3. `sh films/<name>/build.sh` — 読み上げ → 読み取りチェック → タイムライン → 作風チェック → 書き出し → −14 LUFS

前提：`~/lemo-opuscar`（`setup.sh deps voice`）、`.tools/ffmpeg`（ffmpeg 7 静的ビルド）、VOICEVOX Engine
（`docker run -d --rm --name voicevox -p 127.0.0.1:50021:50021 voicevox/voicevox_engine:cpu-latest`）。
動画ファイルと中間生成物は Git に入れない（`.gitignore`）。

## 納品

- 動画は 1080p 版（`<name>_1080p.mp4`、400 MiB 以下）だけをチャットで送る。720p の確認用は頼まれたときだけ作る。
  `sh tools/deliver_1080p.sh <master>.mp4 <name>_1080p.mp4 400` — 上限に収まるビットレートで2パス、音声はコピー（−14 LUFS のまま）。
- 字幕（`.srt`）・サムネイル候補（`poster.jpg`）・チャプター（`CHAPTERS.txt`、1 行目は「◼︎目次」）は Google ドライブのマイドライブ「history_video_ai」に置く。

## 作り直すときの注意（音ズレ）

`film.json` を作り直したら、**必ず `mix.py` も回す**。`mix.py` は各文の音声を `film.json` の時刻に置くので、
タイムラインだけ作り直して音を作り直さないと、映像と字幕は新しい時刻、音声は古い時刻のまま書き出され、
後半にいくほど音がずれる。`mux.sh` は長すぎる音を黙って切るだけなので、この取り違えに気づけない。

- `python tools/check_sync.py films/<name>` — 完成した動画の中の音声を、台本の時刻と突き合わせる。
  納品前に必ず通す（ずれていれば 0.25 秒以内に収まらず、どこで何秒ずれたかを出す）。
- `sh tools/remux_audio.sh <film>.mp4 out/mix.wav <out>.mp4` — 絵はそのままコピーして音だけ入れ替える。
  タイムラインが変わっていない（＝絵は正しい）のに音だけ作り直したときに使う。絵の再書き出しは要らない。

## 作り直すときの注意（固有名詞の読み）

VOICEVOX は知らない固有名詞を「それらしく」読む。しかもその読みは**前後の語で変わる**ので、
1文で正しく読めていても別の文では違う読みになる。徳川埋蔵金編では
小栗→ササグリ、鳥羽→トリワ、多田銀山→オオタギンザン、勝海舟→カツミフネ が出た。
声は流暢で、タイムラインも音量も正常なので、**何も気づかないまま納品されてしまう**。
`core/tts/asr_check.py`（Whisper）では見つからない。小判→小板、パーセント→% のような
表記違いが大量に出るため、本当の読み間違いがその中に埋もれる。

- `films/<name>/readings.json` に「この語はこう読まれていなければならない」を書く。
- `python tools/check_readings.py films/<name>` — `voice/timing.json` のカナと突き合わせる。
  読み上げのあと、書き出しの前に必ず通す。
- 直すときは台本をいじらず、`config/voicevox_dict.json` に足して
  `python tools/tts_voicevox.py lines.json voice --dict … --only s18,s32` で該当行だけ読み直す。
- **短い見出し語に注意**。2文字の姓を辞書に入れると長い呼び名の頭だけ食う。
  「小栗」を登録したら「小栗上野介」が オグリウエノカイ になったので、「上野介」も登録した。
  1文字の語（都・炎）は熟語まで壊すので辞書に入れず、文ごとの `say` で直す（大仏編）。
