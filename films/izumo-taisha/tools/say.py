"""Readings fixed by hand after checking VOICEVOX's kana for all 247 lines (names and terms: config/voicevox_dict.json)."""
import re
def say(i, t):
    s = re.sub(r'(?<!京)都', 'みやこ', t)                  # 京の都・都の朝廷 … read と without this
    s = re.sub(r'(\d+)丈', r'\1ジョウ', s)                  # 1丈 / 32丈 read たけ in some lines
    s = s.replace('1町', 'いっちょう')
    s = s.replace('雲太の太は', 'うんたの、たは')
    s = re.sub(r'雲太(?!和)', 'うんた', s)
    s = s.replace('傾かない', 'かたむかない').replace('一目見よう', 'ひとめ見よう').replace('黒々とした', 'くろぐろとした')
    return s
