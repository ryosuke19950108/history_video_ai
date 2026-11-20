#!/usr/bin/env python3
"""Check that VOICEVOX actually read every name the way the film needs it read.

  python tools/check_readings.py films/<name>

VOICEVOX gets most Japanese right, but proper nouns it does not know are read whichever way its own
dictionary guesses, and the guess changes with the surrounding words: 小栗 came out ササグリ in one
sentence and 鳥羽 came out トリワ, while 勝海舟 was right in one sentence and カツミフネ in another.
Nothing in the build notices — the voice is fluent, the timeline is sound, and the film ships with a
wrong name in it. The speech check (core/tts/asr_check.py) does not catch these either: Whisper writes
小判 as 小板 and パーセント as %, so its mismatches are mostly spelling noise and a real misreading hides
in the list.

This compares what the engine actually said — the kana in voice/timing.json — against what the film
says it must say, for every sentence that contains the word. Put the expectations in the film's own
readings.json:

  {"小栗": ["オグリ"], "上野介": ["コオズケノスケ", "コウズケノスケ"], "鳥羽": ["トバ"]}

Each value is the list of kana spellings that count as correct (the engine writes long vowels as both
オオ and オウ depending on the word, so list both when unsure). A word is only checked in the sentences
that contain it. Exit 0 if every sentence is right, 1 if any is wrong, 2 if the check could not run.

A word that comes out wrong is fixed in config/voicevox_dict.json and the affected lines are read
again (tools/tts_voicevox.py ... --only s18,s32), not by editing the script. Beware short entries: a
two-character surname in the dictionary can swallow the start of a longer title — registering 小栗
made 小栗上野介 read オグリウエノカイ, which is why 上野介 is in the dictionary too.
"""
import argparse, json, os, sys


def strip(k):
    """the engine's kana with its accent and pause marks taken out"""
    for ch in ("'", '_', '、', '/', '…'):
        k = k.replace(ch, '')
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('film', help='the film folder (the one holding lines.json and voice/)')
    ap.add_argument('--readings', help='the expectations (default: <film>/readings.json)')
    a = ap.parse_args()

    d = os.path.abspath(a.film)
    rp = a.readings or os.path.join(d, 'readings.json')
    if not os.path.isfile(rp):
        print(f'✗ 読みの一覧がありません: {rp}', file=sys.stderr); return 2
    want = json.load(open(rp, encoding='utf-8'))
    lines = json.load(open(os.path.join(d, 'lines.json'), encoding='utf-8'))
    tp = os.path.join(d, 'voice', 'timing.json')
    if not os.path.isfile(tp):
        print(f'✗ 読み上げの記録がありません: {tp}（先に tts_voicevox.py を回してください）', file=sys.stderr); return 2
    T = json.load(open(tp, encoding='utf-8'))
    timing = T if isinstance(T, dict) else {t['id']: t for t in T}

    bad, checked = [], 0
    for ln in lines:
        said = ln.get('say') or ln['text']
        rec = timing.get(ln['id'])
        if not rec or not rec.get('kana'):
            continue
        kana = strip(rec['kana'])
        for surface, oks in want.items():
            if surface not in said:
                continue
            checked += 1
            if not any(strip(o) in kana for o in (oks if isinstance(oks, list) else [oks])):
                bad.append((ln['id'], surface, oks[0] if isinstance(oks, list) else oks, said, kana))

    for i, surface, exp, said, kana in bad:
        print(f'✗ {i}  「{surface}」が {exp} と読まれていません')
        print(f'    {said}')
        print(f'    {kana[:140]}')
    if bad:
        print(f'\n✗ {len(bad)} 文で読みが違います。config/voicevox_dict.json に足して、'
              f'tts_voicevox.py --only {",".join(sorted({b[0] for b in bad}))} で読み直してください',
              file=sys.stderr)
        return 1
    print(f'✓ 固有名詞 {len(want)}語・のべ {checked}箇所、すべて指定どおりに読まれています')
    return 0


if __name__ == '__main__':
    sys.exit(main())
