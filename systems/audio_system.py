"""
音效系統 — 使用 NumPy 程式合成所有音效與 BGM，無需外部音效檔案。

音效清單:
  attack      普通攻擊 (衝擊切割聲)
  crit        暴擊    (明亮金屬清鳴)
  skill       技能    (魔法揮灑上升音)
  hit         受傷    (悶重衝擊)
  item        撿物品  (歡快鈴聲)
  level_up    升級    (五音上升琶音 + 收尾和弦)
  boss        Boss出現 (戲劇性揭幕音)
  explosion   爆炸    (低頻噪音爆破)
  game_over   死亡    (下降哀鳴)

BGM 清單:
  bgm_menu    主選單  (輕快冒險風，C大調五聲音階，116 BPM)
  bgm_battle  戰鬥    (chiptune 英雄風 140 BPM，D大調)
  bgm_boss    Boss戰  (史詩英雄風 170 BPM，E大調，不陰森)
"""

import pygame
import numpy as np

SR = 44100


# ── 波形基元 ──────────────────────────────────────────────
def _sine(freq, t):
    return np.sin(2 * np.pi * freq * t)

def _square(freq, t, duty=0.5):
    phase = (t * freq) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)

def _sawtooth(freq, t):
    return (2 * ((t * freq) % 1.0) - 1.0).astype(np.float32)

def _triangle(freq, t):
    phase = (t * freq) % 1.0
    return (2 * np.abs(2 * phase - 1) - 1).astype(np.float32)

def _noise(n):
    return np.random.uniform(-1.0, 1.0, n).astype(np.float32)

def _adsr(n, a=0.01, d=0.1, s=0.7, r=0.15):
    env = np.zeros(n, dtype=np.float32)
    a_n = min(n,           max(1, int(a * SR)))
    d_n = min(n - a_n,     max(1, int(d * SR)))
    r_n = min(n - a_n - d_n, max(1, int(r * SR)))
    s_n = max(0, n - a_n - d_n - r_n)
    i0 = 0;            env[i0:i0+a_n]         = np.linspace(0, 1, a_n)
    i1 = a_n;          env[i1:i1+d_n]         = np.linspace(1, s, d_n)
    i2 = a_n + d_n;    env[i2:i2+s_n]         = s
    i3 = i2 + s_n;     env[i3:i3+r_n]         = np.linspace(s, 0, r_n)
    return env

def _to_sound(samples, volume=0.5):
    samples = np.clip(samples * volume, -1.0, 1.0)
    data = (samples * 32767).astype(np.int16)
    stereo = np.ascontiguousarray(np.column_stack([data, data]))
    return pygame.sndarray.make_sound(stereo)

def _t(sec):
    return np.linspace(0, sec, int(SR * sec), dtype=np.float32)


# ── 音效生成 ──────────────────────────────────────────────
def _sfx_attack():
    """衝擊切割聲：高頻掃降 + 輕噪音"""
    t = _t(0.22)
    freq = 500 * np.exp(-t * 12)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    wave += 0.35 * _noise(len(t)) * np.exp(-t * 18)
    return _to_sound(wave * np.exp(-t * 9), 0.42)

def _sfx_crit():
    """暴擊：明亮金屬清鳴 (改為開朗的高音)"""
    t = _t(0.35)
    wave = (_sine(1046, t) * 0.8 + _sine(1318, t) * 0.5 +
            _sine(1568, t) * 0.3)
    wave += 0.15 * _noise(len(t)) * np.exp(-t * 30)
    env = _adsr(len(t), 0.005, 0.05, 0.3, 0.4)
    return _to_sound(wave * env, 0.45)

def _sfx_skill():
    """魔法音：頻率掃升 + 泛音"""
    t = _t(0.55)
    freq_rise = 180 + 700 * (t / 0.55) ** 1.5
    wave = np.sin(2 * np.pi * np.cumsum(freq_rise) / SR)
    wave += 0.4 * _sine(freq_rise * 1.5, t)
    wave += 0.15 * _noise(len(t)) * np.exp(-t * 6)
    env = _adsr(len(t), 0.04, 0.12, 0.6, 0.25)
    return _to_sound(wave * env, 0.48)

def _sfx_hit():
    """受傷悶擊：低頻掃降 + 噪音"""
    t = _t(0.20)
    freq = 280 * np.exp(-t * 18)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    wave += 0.45 * _noise(len(t)) * np.exp(-t * 28)
    return _to_sound(wave * np.exp(-t * 14), 0.38)

def _sfx_item():
    """撿物品：歡快三音上升琶音 (更明亮)"""
    notes = [1319, 1568, 2093]   # E6 G6 C7
    segs = []
    for freq in notes:
        t = _t(0.10)
        wave = (_sine(freq, t) * 0.7 + _sine(freq * 2, t) * 0.3) * np.exp(-t * 18)
        segs.append(wave)
    return _to_sound(np.concatenate(segs), 0.35)

def _sfx_level_up():
    """升級：明亮六音上升 C-E-G-B-D-G + 喜悅和弦"""
    notes = [523, 659, 784, 988, 1175, 1568]
    segs = []
    for freq in notes:
        t = _t(0.11)
        wave = (_triangle(freq, t) * 0.5 + _sine(freq, t) * 0.5) * np.exp(-t * 9)
        segs.append(wave)
    # 最終大七和弦
    t = _t(0.8)
    chord = (_sine(523, t) + _sine(659, t) + _sine(784, t) + _sine(988, t)) / 4
    chord *= np.exp(-t * 2.0)
    segs.append(chord)
    return _to_sound(np.concatenate(segs), 0.55)

def _sfx_boss():
    """Boss 出現：戲劇性號角揭幕音 (不陰森)"""
    t = _t(1.2)
    # 號角和弦 E G B (E大調)
    wave = (_sine(164.81, t) * 0.6 + _sine(196.00, t) * 0.5 +
            _sine(246.94, t) * 0.4 + _sine(329.63, t) * 0.3)
    wave += 0.15 * _noise(len(t)) * np.exp(-t * 2)
    env = _adsr(len(t), 0.06, 0.20, 0.65, 0.30)
    return _to_sound(wave * env, 0.60)

def _sfx_explosion():
    """爆炸：低頻衝擊噪音"""
    t = _t(0.65)
    freq = 180 * np.exp(-t * 7)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SR) * 0.45
    wave += _noise(len(t)) * 0.55 * np.exp(-t * 5)
    return _to_sound(wave * np.exp(-t * 3.5), 0.55)

def _sfx_game_over():
    """死亡：四音下降哀鳴"""
    notes = [523, 440, 392, 330]
    segs = []
    for freq in notes:
        t = _t(0.32)
        wave = _sine(freq, t) + 0.35 * _sine(freq * 0.5, t)
        wave *= _adsr(len(t), 0.02, 0.05, 0.8, 0.1)
        segs.append(wave)
    return _to_sound(np.concatenate(segs), 0.45)


def _mix(music, idx, seg):
    avail = len(music) - idx
    if avail <= 0:
        return
    n = min(len(seg), avail)
    music[idx:idx+n] += seg[:n]


# ── BGM 生成 ──────────────────────────────────────────────

def _bgm_menu():
    """
    主選單 BGM — 輕快冒險風 116 BPM，C大調五聲音階。
    像海賊出航前的期待感：明亮、輕鬆、有點搞笑。
    """
    bpm = 116
    beat = 60 / bpm
    bars = 16
    total = beat * 4 * bars
    t = _t(total)
    music = np.zeros(len(t), dtype=np.float32)

    # 暖和弦墊底 — C大調 (C E G C5)
    chord = [261.63, 329.63, 392.00, 523.25]
    for freq in chord:
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.0 * t)
        music += _sine(freq * vib, t) * 0.055

    # 輕快鋼琴/鐘琴主旋律 — C大調五聲音階
    # C D E G A C D E G (歡快跳躍)
    melody = [
        523.25, 587.33, 659.25, 783.99, 880.00,
        1046.5, 880.00, 783.99, 659.25, 587.33,
        523.25, 659.25, 783.99, 1046.5, 880.00, 659.25,
        523.25, 587.33, 659.25, 523.25, 659.25, 783.99,
        880.00, 659.25, 783.99, 1046.5, 880.00, 783.99,
        659.25, 523.25, 587.33, 523.25,
    ]
    rhythm = [
        0.5, 0.5, 0.5, 0.5, 1.0,
        0.5, 0.5, 0.5, 0.5, 1.0,
        0.5, 0.5, 1.0, 0.5, 0.5, 1.0,
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
        1.0, 0.5, 0.5, 0.5, 0.5, 0.5,
        1.0, 0.5, 0.5, 1.0,
    ]
    pos = beat * 4  # 第二小節才進入旋律
    for freq, dur_b in zip(melody, rhythm):
        d_sec = dur_b * beat * 0.82
        dur = int(d_sec * SR)
        if pos * SR + dur >= len(music):
            break
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_triangle(freq, ta) * 0.55 + _sine(freq * 2, ta) * 0.25)
        seg *= _adsr(dur, 0.005, 0.05, 0.55, 0.20) * 0.18
        _mix(music, int(pos * SR), seg)
        pos += dur_b * beat

    # 撥弦風低音 (C大調)
    bass_pat = [130.81, 130.81, 196.00, 164.81,
                174.61, 174.61, 130.81, 196.00]
    step = beat * 0.5
    for i in range(int(total / step)):
        freq = bass_pat[i % len(bass_pat)]
        dur = int(step * 0.70 * SR)
        ta = np.linspace(0, step * 0.70, dur, dtype=np.float32)
        seg = _triangle(freq, ta) * _adsr(dur, 0.005, 0.08, 0.5, 0.20) * 0.13
        _mix(music, int(i * step * SR), seg)

    # 輕鬆小鼓 (拍子 2 & 4)
    for b in range(int(total / beat)):
        if b % 4 in (1, 3):
            dur = int(0.09 * SR)
            ta = np.linspace(0, 0.09, dur, dtype=np.float32)
            seg = (_noise(dur) * 0.4 + _sine(220, ta) * 0.2) * np.exp(-ta * 40)
            _mix(music, int(b * beat * SR), seg * 0.28)
        # Hi-hat
        dur = int(0.04 * SR)
        ta = np.linspace(0, 0.04, dur, dtype=np.float32)
        _mix(music, int((b * beat + beat * 0.5) * SR),
             _noise(dur) * np.exp(-ta * 70) * 0.12)

    return _to_sound(np.clip(music, -1, 1), 0.72)


def _bgm_battle():
    """
    戰鬥 BGM — 英雄風 chiptune 140 BPM，D大調。
    活潑緊張但不沉重，像動作英雄追逐戰。
    """
    bpm = 140
    beat = 60 / bpm
    total = beat * 4 * 8
    music = np.zeros(int(SR * total), dtype=np.float32)

    def _kick(start):
        dur = int(0.14 * SR)
        ta = np.linspace(0, 0.14, dur, dtype=np.float32)
        freq = 100 * np.exp(-ta * 32)
        seg = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-ta * 20)
        _mix(music, int(start * SR), seg * 0.45)

    def _snare(start):
        dur = int(0.10 * SR)
        ta = np.linspace(0, 0.10, dur, dtype=np.float32)
        seg = (_noise(dur) * 0.5 + _sine(280, ta) * 0.5) * np.exp(-ta * 38)
        _mix(music, int(start * SR), seg * 0.32)

    def _hihat(start, open_=False):
        d = int((0.15 if open_ else 0.04) * SR)
        ta = np.linspace(0, d / SR, d, dtype=np.float32)
        seg = _noise(d) * np.exp(-ta * (10 if open_ else 70))
        _mix(music, int(start * SR), seg * 0.14)

    for b in range(int(total / beat)):
        _kick(b * beat)
        if b % 4 in (1, 3):
            _snare(b * beat)
        _hihat(b * beat + beat * 0.5)
        if b % 2 == 0:
            _hihat(b * beat + beat * 0.75, open_=True)

    # 低音線 — D大調五聲音階
    bass_pat = [146.83, 164.81, 185.00, 146.83,
                220.00, 196.00, 164.81, 146.83]
    n16 = beat * 0.5
    for i in range(int(total / n16)):
        freq = bass_pat[i % len(bass_pat)]
        dur = int(n16 * 0.80 * SR)
        ta = np.linspace(0, n16 * 0.80, dur, dtype=np.float32)
        seg = _square(freq, ta, duty=0.40) * _adsr(dur, 0.01, 0.06, 0.65, 0.18) * 0.20
        _mix(music, int(i * n16 * SR), seg)

    # 主旋律 — D大調，英雄風上揚感
    melody = [
        587.33, 659.25, 739.99, 783.99,  # D5 E5 F#5 G5
        880.00, 783.99, 659.25, 587.33,  # A5 G5 E5 D5
        659.25, 739.99, 880.00, 783.99,  # E5 F#5 A5 G5
        659.25, 587.33, 739.99, 587.33,  # E5 D5 F#5 D5
    ]
    rhythm = [0.5, 0.5, 0.5, 1.0,
              0.5, 0.5, 0.5, 1.0,
              0.5, 0.5, 1.0, 0.5,
              0.5, 1.0, 1.0, 2.0]
    pos = 0.0
    for freq, dur_b in zip(melody, rhythm):
        d_sec = dur_b * beat * 0.85
        dur = int(d_sec * SR)
        if pos * SR + dur >= len(music):
            break
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_triangle(freq, ta) * 0.6 + _sine(freq * 2, ta) * 0.3)
        seg *= _adsr(dur, 0.01, 0.07, 0.60, 0.20) * 0.22
        _mix(music, int(pos * SR), seg)
        pos += dur_b * beat

    # 和弦墊底 — D大調 (D F# A)
    chords_d = [[146.83, 185.00, 220.00], [196.00, 246.94, 293.66],
                [146.83, 185.00, 220.00], [164.81, 207.65, 246.94]]
    for bi, chord in enumerate(chords_d):
        t0 = bi * beat * 8
        if t0 >= total:
            break
        dur = int(beat * 8 * SR)
        for freq in chord:
            ta = np.linspace(0, dur / SR, dur, dtype=np.float32)
            seg = _sine(freq, ta) * _adsr(dur, 0.12, 0.20, 0.55, 0.35) * 0.06
            _mix(music, int(t0 * SR), seg)

    return _to_sound(np.clip(music, -1, 1), 0.75)


def _bgm_boss():
    """
    Boss BGM — 史詩英雄風 170 BPM，E大調。
    緊張激烈但充滿鬥志，不陰森不壓抑，像主角與強敵的巔峰對決。
    """
    bpm = 170
    beat = 60 / bpm
    total = beat * 4 * 8
    music = np.zeros(int(SR * total), dtype=np.float32)

    # 鼓組 (和 bgm_battle 類似但更猛烈)
    for b in range(int(total / beat)):
        # 踢鼓
        dur = int(0.11 * SR)
        ta = np.linspace(0, 0.11, dur, dtype=np.float32)
        freq_k = 110 * np.exp(-ta * 38)
        _mix(music, int(b * beat * SR),
             np.sin(2 * np.pi * np.cumsum(freq_k) / SR) * np.exp(-ta * 22) * 0.50)
        # 小鼓 (拍 2 & 4)
        if b % 4 in (1, 3):
            dur2 = int(0.09 * SR)
            ta2 = np.linspace(0, 0.09, dur2, dtype=np.float32)
            _mix(music, int(b * beat * SR),
                 (_noise(dur2) * 0.6 + _sine(240, ta2) * 0.3) * np.exp(-ta2 * 40) * 0.38)
        # Hi-hat 16 分
        for sub in range(4):
            d = int(0.03 * SR)
            ta3 = np.linspace(0, 0.03, d, dtype=np.float32)
            _mix(music, int((b * beat + sub * beat / 4) * SR),
                 _noise(d) * np.exp(-ta3 * 90) * 0.10)

    # 低音 — E大調五聲 (E, F#, G#, B, C#)
    bass_e = [82.41, 92.50, 110.00, 82.41,
              123.47, 110.00, 92.50, 82.41]
    n8 = beat * 0.5
    for i in range(int(total / n8)):
        freq = bass_e[i % len(bass_e)]
        d_sec = n8 * 0.82
        dur = int(d_sec * SR)
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_square(freq, ta, duty=0.45) * 0.55 + _sine(freq * 2, ta) * 0.30)
        _mix(music, int(i * n8 * SR), seg * _adsr(dur, 0.01, 0.05, 0.72, 0.14) * 0.22)

    # 英雄旋律 — E大調，鬥志昂揚的線條
    mel_hero = [
        659.25, 739.99, 830.61, 880.00,   # E5 F#5 G#5 A5
        987.77, 880.00, 739.99, 659.25,   # B5 A5 F#5 E5
        739.99, 830.61, 987.77, 880.00,   # F#5 G#5 B5 A5
        830.61, 659.25, 739.99, 659.25,   # G#5 E5 F#5 E5
    ]
    pos = 0.0
    for freq in mel_hero:
        d_sec = 0.5 * beat * 0.86
        dur = int(d_sec * SR)
        if pos * SR + dur >= len(music):
            break
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_triangle(freq, ta) * 0.55 + _sawtooth(freq, ta) * 0.25 +
               _sine(freq * 2, ta) * 0.20)
        _mix(music, int(pos * SR), seg * _adsr(dur, 0.01, 0.06, 0.65, 0.18) * 0.20)
        pos += 0.5 * beat

    # 對位旋律 (五度上移 B大調)
    mel_counter = [
        987.77, 1108.73, 1244.51, 1318.51,
        987.77, 1108.73, 987.77, 880.00,
    ]
    pos2 = beat * 16  # 第三次出現才加入對位
    for freq in mel_counter:
        d_sec = beat * 0.86
        dur = int(d_sec * SR)
        if pos2 * SR + dur >= len(music):
            break
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = _triangle(freq, ta) * _adsr(dur, 0.01, 0.08, 0.50, 0.25) * 0.12
        _mix(music, int(pos2 * SR), seg)
        pos2 += beat

    # 電吉他風高亢單音 (偶數小節點綴)
    guitar_notes = [1318.51, 1567.98, 1318.51, 987.77,
                    1108.73, 1244.51, 1108.73, 987.77]
    for gi, freq in enumerate(guitar_notes):
        t0 = gi * beat * 4
        if t0 >= total:
            break
        dur = int(beat * 1.8 * SR)
        ta = np.linspace(0, beat * 1.8, dur, dtype=np.float32)
        vib = 1 + 0.008 * np.sin(2 * np.pi * 6 * ta)
        seg = _sawtooth(freq * vib, ta) * _adsr(dur, 0.005, 0.08, 0.65, 0.30) * 0.14
        _mix(music, int(t0 * SR), seg)

    return _to_sound(np.clip(music, -1, 1), 0.78)


# ── 主類別 ─────────────────────────────────────────────────
class AudioSystem:
    def __init__(self):
        self._enabled = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._music_ch: pygame.mixer.Channel | None = None
        self._current_music = ""
        self._music_volume = 0.5

        try:
            pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(16)
            self._enabled = True
            self._build_sounds()
        except Exception as e:
            print(f"[Audio] init failed: {e}")

    def _build_sounds(self):
        builders = {
            "attack":     _sfx_attack,
            "crit":       _sfx_crit,
            "skill":      _sfx_skill,
            "hit":        _sfx_hit,
            "item":       _sfx_item,
            "level_up":   _sfx_level_up,
            "boss":       _sfx_boss,
            "explosion":  _sfx_explosion,
            "game_over":  _sfx_game_over,
            "bgm_menu":   _bgm_menu,
            "bgm_battle": _bgm_battle,
            "bgm_boss":   _bgm_boss,
        }
        for name, fn in builders.items():
            try:
                self._sounds[name] = fn()
            except Exception as e:
                print(f"[Audio] failed to build '{name}': {e}")

    def play(self, name: str):
        if self._enabled and name in self._sounds:
            try:
                self._sounds[name].play()
            except Exception:
                pass

    def play_music(self, name: str, loops: int = -1):
        if not self._enabled or name not in self._sounds:
            return
        if self._current_music == name:
            return
        try:
            if not self._music_ch:
                self._music_ch = pygame.mixer.Channel(0)
            self._music_ch.set_volume(self._music_volume)
            self._music_ch.play(self._sounds[name], loops=loops)
            self._current_music = name
        except Exception:
            pass

    def stop_music(self):
        if self._music_ch:
            try:
                self._music_ch.stop()
                self._current_music = ""
            except Exception:
                pass

    def set_music_volume(self, vol: float):
        self._music_volume = max(0.0, min(1.0, vol))
        if self._music_ch:
            try:
                self._music_ch.set_volume(self._music_volume)
            except Exception:
                pass
