"""
音效系統 — 使用 NumPy 程式合成所有音效與 BGM，無需外部音效檔案。

音效清單:
  attack      普通攻擊 (衝擊切割聲)
  crit        暴擊    (金屬撞擊聲)
  skill       技能    (魔法揮灑上升音)
  hit         受傷    (悶重衝擊)
  item        撿物品  (輕巧鈴聲)
  level_up    升級    (五音上升琶音)
  boss        Boss出現 (低沉震撼音)
  explosion   爆炸    (低頻噪音爆破)
  game_over   死亡    (四音下降哀鳴)

BGM 清單:
  bgm_menu    主選單  (悠揚琶音 ambient pad)
  bgm_battle  戰鬥    (chiptune 鼓組 + 旋律 140 BPM)
  bgm_boss    Boss 戰 (緊張快節奏 170 BPM)
"""

import pygame
import numpy as np

SR = 44100  # sample rate


# ── 波形基元 ──────────────────────────────────────────────
def _sine(freq, t):
    return np.sin(2 * np.pi * freq * t)

def _square(freq, t, duty=0.5):
    phase = (t * freq) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)

def _sawtooth(freq, t):
    return (2 * ((t * freq) % 1.0) - 1.0).astype(np.float32)

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
    """暴擊金屬撞聲：三次諧波 + 衰減"""
    t = _t(0.38)
    wave = (_sine(880, t) + 0.55 * _sine(1760, t) +
            0.28 * _sine(2640, t) +
            0.35 * _noise(len(t)) * np.exp(-t * 22))
    return _to_sound(wave * np.exp(-t * 7), 0.52)

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
    """撿物品鈴聲：快速三音琶音"""
    notes = [1047, 1319, 1568]   # C6 E6 G6
    segs = []
    for freq in notes:
        t = _t(0.09)
        wave = (_sine(freq, t) + 0.25 * _sine(freq * 2, t)) * np.exp(-t * 22)
        segs.append(wave)
    return _to_sound(np.concatenate(segs), 0.32)

def _sfx_level_up():
    """升級琶音：五音上升 C-E-G-C-E + 和弦收尾"""
    notes = [523, 659, 784, 1047, 1319]
    segs = []
    for freq in notes:
        t = _t(0.13)
        wave = (_sine(freq, t) + 0.3 * _sine(freq * 2, t)) * np.exp(-t * 9)
        segs.append(wave)
    # 最終和弦
    t = _t(0.7)
    chord = (_sine(523, t) + _sine(659, t) + _sine(784, t)) / 3
    chord *= np.exp(-t * 2.5)
    segs.append(chord)
    return _to_sound(np.concatenate(segs), 0.55)

def _sfx_boss():
    """Boss 出現：低沉震撼音 + 噪音衝擊"""
    t = _t(1.3)
    wave = (_sine(55, t) + 0.55 * _sine(110, t) +
            0.28 * _sine(165, t) + 0.15 * _sawtooth(55, t))
    wave += 0.25 * _noise(len(t)) * np.exp(-t * 1.2)
    env = _adsr(len(t), 0.04, 0.25, 0.55, 0.45)
    return _to_sound(wave * env, 0.65)

def _sfx_explosion():
    """爆炸：低頻衝擊噪音"""
    t = _t(0.65)
    freq = 180 * np.exp(-t * 7)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SR) * 0.45
    wave += _noise(len(t)) * 0.55 * np.exp(-t * 5)
    return _to_sound(wave * np.exp(-t * 3.5), 0.55)

def _sfx_game_over():
    """死亡：四音下降哀鳴"""
    notes = [523, 440, 392, 330]   # C5 A4 G4 E4
    segs = []
    for freq in notes:
        t = _t(0.32)
        wave = _sine(freq, t) + 0.35 * _sine(freq * 0.5, t)
        wave *= _adsr(len(t), 0.02, 0.05, 0.8, 0.1)
        segs.append(wave)
    return _to_sound(np.concatenate(segs), 0.45)


def _mix(music, idx, seg):
    """安全混音：自動截斷超出邊界的 seg"""
    avail = len(music) - idx
    if avail <= 0:
        return
    n = min(len(seg), avail)
    music[idx:idx+n] += seg[:n]


# ── BGM 生成 ──────────────────────────────────────────────
def _bgm_menu():
    """主選單 BGM — ambient pad + 慢速琶音 100 BPM，16 小節"""
    bpm = 100
    beat = 60 / bpm
    bars = 16
    total = beat * 4 * bars
    t = _t(total)
    music = np.zeros(len(t), dtype=np.float32)

    # Ambient pad — C大調和弦帶 vibrato
    chord = [261.63, 329.63, 392.00, 523.25]  # C4 E4 G4 C5
    for freq in chord:
        vib = 1 + 0.004 * np.sin(2 * np.pi * 4.5 * t)
        music += _sine(freq * vib, t) * 0.07

    # 慢速琶音
    arp = [261.63, 329.63, 392.00, 523.25, 659.25, 523.25, 392.00, 329.63]
    step = beat * 0.5
    n_steps = int(total / step)
    for i in range(n_steps):
        freq = arp[i % len(arp)]
        t0 = i * step
        idx = int(t0 * SR)
        dur = int(step * 0.78 * SR)
        if idx + dur >= len(music):
            break
        ta = np.linspace(0, step * 0.78, dur, dtype=np.float32)
        seg = _sine(freq, ta) * np.exp(-ta * 3.5)
        music[idx:idx+dur] += seg * 0.16

    # 高音鐘點綴 (每兩小節)
    bell_freqs = [1047, 1319, 1568, 2093]
    for bar in range(0, bars, 2):
        for bi, freq in enumerate(bell_freqs):
            t0 = (bar * 4 + bi * 0.75) * beat
            idx = int(t0 * SR)
            dur = int(0.6 * SR)
            if idx + dur >= len(music):
                break
            ta = np.linspace(0, 0.6, dur, dtype=np.float32)
            seg = _sine(freq, ta) * np.exp(-ta * 5)
            music[idx:idx+dur] += seg * 0.08

    return _to_sound(np.clip(music, -1, 1), 0.7)


def _bgm_battle():
    """戰鬥 BGM — chiptune 風格  140 BPM，8 小節"""
    bpm = 140
    beat = 60 / bpm
    total = beat * 4 * 8
    music = np.zeros(int(SR * total), dtype=np.float32)

    def _kick(start):
        dur = int(0.14 * SR)
        ta = np.linspace(0, 0.14, dur, dtype=np.float32)
        freq = 90 * np.exp(-ta * 35)
        seg = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-ta * 22)
        _mix(music, int(start * SR), seg * 0.50)

    def _snare(start):
        dur = int(0.12 * SR)
        ta = np.linspace(0, 0.12, dur, dtype=np.float32)
        seg = (_noise(dur) * 0.6 + _sine(220, ta) * 0.4) * np.exp(-ta * 32)
        _mix(music, int(start * SR), seg * 0.38)

    def _hihat(start, open_=False):
        d = int((0.18 if open_ else 0.05) * SR)
        ta = np.linspace(0, d / SR, d, dtype=np.float32)
        seg = _noise(d) * np.exp(-ta * (8 if open_ else 60))
        _mix(music, int(start * SR), seg * 0.18)

    for b in range(int(total / beat)):
        _kick(b * beat)
        if b % 4 in (1, 3): _snare(b * beat)
        _hihat(b * beat + beat * 0.5)
        if b % 2 == 0: _hihat(b * beat + beat * 0.75, open_=True)

    # 低音線 (方波)
    bass_pat = [130.81, 146.83, 164.81, 130.81,
                174.61, 164.81, 146.83, 130.81]
    n16 = beat * 0.5
    for i in range(int(total / n16)):
        freq = bass_pat[i % len(bass_pat)]
        dur = int(n16 * 0.82 * SR)
        ta = np.linspace(0, n16 * 0.82, dur, dtype=np.float32)
        seg = _square(freq, ta, duty=0.45) * _adsr(dur, 0.01, 0.06, 0.7, 0.15) * 0.22
        _mix(music, int(i * n16 * SR), seg)

    # 主旋律 (鋸齒波)
    melody = [523.25, 659.25, 783.99, 587.33, 523.25,
              659.25, 880.00, 783.99, 659.25, 587.33,
              523.25, 587.33, 659.25, 523.25, 659.25, 783.99]
    rhythm = [1, 0.5, 0.5, 1, 1, 0.5, 0.5, 1,
              0.5, 0.5, 1, 0.5, 0.5, 1, 1, 2]
    pos = 0.0
    for freq, dur_b in zip(melody, rhythm):
        d_sec = dur_b * beat * 0.88
        dur = int(d_sec * SR)
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_sawtooth(freq, ta) * 0.5 + _sine(freq * 2, ta) * 0.25)
        seg *= _adsr(dur, 0.01, 0.08, 0.65, 0.18) * 0.20
        _mix(music, int(pos * SR), seg)
        pos += dur_b * beat

    # 和弦墊底
    chords = [[261.63,329.63,392.00],[293.66,369.99,440.00],
              [261.63,329.63,392.00],[246.94,311.13,369.99]]
    for bi, chord in enumerate(chords):
        t0 = bi * beat * 8
        if t0 >= total: break
        dur = int(beat * 8 * SR)
        for freq in chord:
            ta = np.linspace(0, dur / SR, dur, dtype=np.float32)
            seg = _sine(freq, ta) * _adsr(dur, 0.1, 0.2, 0.6, 0.3) * 0.07
            _mix(music, int(t0 * SR), seg)

    return _to_sound(np.clip(music, -1, 1), 0.75)


def _bgm_boss():
    """Boss 戰 BGM — 緊張快節奏 170 BPM，8 小節"""
    bpm = 170
    beat = 60 / bpm
    total = beat * 4 * 8
    music = np.zeros(int(SR * total), dtype=np.float32)

    for b in range(int(total / beat)):
        dur = int(0.10 * SR)
        ta = np.linspace(0, 0.10, dur, dtype=np.float32)
        freq = 100 * np.exp(-ta * 40)
        _mix(music, int(b * beat * SR),
             np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-ta * 25) * 0.55)
        if b % 4 in (1, 3):
            ta2 = np.linspace(0, 0.10, dur, dtype=np.float32)
            _mix(music, int(b * beat * SR),
                 (_noise(dur) * 0.7) * np.exp(-ta2 * 35) * 0.42)
        for sub in range(4):
            d = int(0.04 * SR)
            ta3 = np.linspace(0, 0.04, d, dtype=np.float32)
            _mix(music, int((b * beat + sub * beat / 4) * SR),
                 _noise(d) * np.exp(-ta3 * 80) * 0.15)

    bass = [110, 116.54, 123.47, 110, 130.81, 110, 123.47, 116.54]
    n8 = beat * 0.5
    for i in range(int(total / n8)):
        freq = bass[i % len(bass)]
        d_sec = n8 * 0.85
        dur = int(d_sec * SR)
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_square(freq, ta) * 0.6 + _sawtooth(freq, ta) * 0.4)
        _mix(music, int(i * n8 * SR), seg * _adsr(dur, 0.01, 0.04, 0.75, 0.12) * 0.24)

    mel_boss = [220, 246.94, 261.63, 293.66, 329.63,
                261.63, 246.94, 220, 246.94, 293.66,
                329.63, 293.66, 261.63, 220, 246.94, 220]
    pos = 0.0
    for freq in mel_boss:
        d_sec = 0.5 * beat * 0.88
        dur = int(d_sec * SR)
        ta = np.linspace(0, d_sec, dur, dtype=np.float32)
        seg = (_sawtooth(freq * 2, ta) + 0.4 * _sine(freq * 2, ta))
        _mix(music, int(pos * SR), seg * _adsr(dur, 0.01, 0.05, 0.70, 0.15) * 0.18)
        pos += 0.5 * beat

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
            "attack":    _sfx_attack,
            "crit":      _sfx_crit,
            "skill":     _sfx_skill,
            "hit":       _sfx_hit,
            "item":      _sfx_item,
            "level_up":  _sfx_level_up,
            "boss":      _sfx_boss,
            "explosion": _sfx_explosion,
            "game_over": _sfx_game_over,
            "bgm_menu":  _bgm_menu,
            "bgm_battle":_bgm_battle,
            "bgm_boss":  _bgm_boss,
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
