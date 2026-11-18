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
- 字幕（`.srt`）・サムネイル候補（`poster.jpg`）・チャプター（`CHAPTERS.txt`、1 行目は「◾️目次」）は Google ドライブのマイドライブ「history_video_ai」に置く。
