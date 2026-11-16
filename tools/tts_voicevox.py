#!/usr/bin/env python3
"""VOICEVOX narration with the same inputs and outputs as Lemo-Opuscar's core/tts/tts.py (core/ is not modified).

  python tools/tts_voicevox.py lines.json out_dir [--speaker 玄野武宏] [--style ノーマル] [--host http://127.0.0.1:50021]
                               [--dict config/voicevox_dict.json] [--speed 1.0] [--pre 0.05] [--post 0.15]

lines.json = [{"id", "text", "say"?, "speed"?, "pitch"?, "intonation"?}]
  text  what the subtitles show (digits allowed)
  say   what is read, when it differs from text (kana for names VOICEVOX misreads)
Writes <id>.wav (24 kHz mono), dur.json ({id: seconds}) and timing.json ({id: {"kana", "moras": [[t0, t1, kana], ...]}}),
the mora timings coming from VOICEVOX's own audio_query, so subtitles can be split on them without speech-to-text.
--dict registers words (surface, pronunciation in katakana, accent_type) in the engine's user dictionary first; words already
present with the same surface are left alone. Standard library only. The engine must be running (docker image voicevox/voicevox_engine)."""
import argparse, json, os, sys, urllib.parse, urllib.request, wave


def call(host, method, path, params=None, body=None, raw=False):
    url = host + path + ('?' + urllib.parse.urlencode(params) if params else '')
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={'Content-Type': 'application/json'} if data else {})
    with urllib.request.urlopen(req, timeout=120) as r:
        b = r.read()
    return b if raw else (json.loads(b) if b else None)


def speaker_id(host, name, style):
    for s in call(host, 'GET', '/speakers'):
        if s['name'] == name:
            for st in s['styles']:
                if st['name'] == style:
                    return st['id']
            sys.exit(f'✗ {name} has no style {style}: ' + ', '.join(x["name"] for x in s['styles']))
    sys.exit(f'✗ unknown speaker {name}')


def register_dict(host, path):
    words = json.load(open(path, encoding='utf-8'))
    have = {v['surface'] for v in (call(host, 'GET', '/user_dict') or {}).values()}
    for w in words:
        # the engine stores surfaces in full-width form
        if w['surface'] in have:
            continue
        call(host, 'POST', '/user_dict_word', {'surface': w['surface'], 'pronunciation': w['pronunciation'],
                                               'accent_type': w.get('accent_type', 0), 'word_type': w.get('word_type', 'PROPER_NOUN')})
        print(f'+ dict {w["surface"]} → {w["pronunciation"]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lines'); ap.add_argument('out')
    ap.add_argument('--speaker', default='玄野武宏'); ap.add_argument('--style', default='ノーマル')
    ap.add_argument('--host', default=os.environ.get('VOICEVOX_HOST', 'http://127.0.0.1:50021'))
    ap.add_argument('--dict'); ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--pre', type=float, default=0.05); ap.add_argument('--post', type=float, default=0.15)
    a = ap.parse_args()
    try:
        ver = call(a.host, 'GET', '/version')
    except Exception as e:
        sys.exit(f'✗ VOICEVOX engine not reachable at {a.host}: {e}')
    if a.dict:
        register_dict(a.host, a.dict)
    sid = speaker_id(a.host, a.speaker, a.style)
    os.makedirs(a.out, exist_ok=True)
    lines = json.load(open(a.lines, encoding='utf-8'))
    durs, timing = {}, {}
    for ln in lines:
        q = call(a.host, 'POST', '/audio_query', {'text': ln.get('say') or ln['text'], 'speaker': sid})
        q['speedScale'] = ln.get('speed', a.speed)
        q['pitchScale'] = ln.get('pitch', q['pitchScale'])
        q['intonationScale'] = ln.get('intonation', q['intonationScale'])
        q['prePhonemeLength'], q['postPhonemeLength'] = a.pre, a.post
        q['outputSamplingRate'], q['outputStereo'] = 24000, False
        wav = call(a.host, 'POST', '/synthesis', {'speaker': sid}, body=q, raw=True)
        p = os.path.join(a.out, f'{ln["id"]}.wav')
        open(p, 'wb').write(wav)
        with wave.open(p) as w:
            durs[ln['id']] = round(w.getnframes() / w.getframerate(), 3)
        # mora timeline from the query itself (consonant + vowel lengths, pauses), scaled by speed
        t, moras, sp = a.pre / q['speedScale'], [], q['speedScale']
        for ph in q['accent_phrases']:
            for m in ph['moras'] + ([ph['pause_mora']] if ph.get('pause_mora') else []):
                d = ((m.get('consonant_length') or 0) + (m.get('vowel_length') or 0)) / sp
                moras.append([round(t, 3), round(t + d, 3), m['text']]); t += d
        timing[ln['id']] = {'kana': q.get('kana', ''), 'moras': moras}
        print(f'✓ {ln["id"]}  {durs[ln["id"]]:.2f} s  {ln["text"][:30]}')
    json.dump(durs, open(os.path.join(a.out, 'dur.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(timing, open(os.path.join(a.out, 'timing.json'), 'w'), ensure_ascii=False)
    print(f'VOICEVOX {ver} · {a.speaker}（{a.style}）· {len(lines)} lines · {sum(durs.values()):.1f} s')


if __name__ == '__main__':
    main()
