"""
Q版（Chibi）角色精靈繪製模組。
大頭小身、圓潤可愛，符合 2D 遊戲風格。

draw_character(screen, cx, cy, char_data, r=28, t=0.0, hurt=False, blink=False, current_fruit=None)
  cx, cy  — 精靈中心（腰部）
  r       — 比例基準（角色選擇 ~32，遊戲內 ~22）
"""

import pygame
import math


def draw_character(screen, cx, cy, char_data, r=28, t=0.0,
                   hurt=False, blink=False, current_fruit=None):
    if blink:
        return

    cid    = char_data["id"]
    body_c = tuple(char_data["body_color"])
    skin_c = tuple(char_data["skin_color"])
    hair_c = tuple(char_data["hair_color"])
    hat_c  = tuple(char_data["hat_color"])
    det_c  = tuple(char_data["detail_color"])

    def S(n): return max(1, int(n * r / 28))

    if hurt:
        body_c = (255, 170, 170)
        skin_c = (255, 200, 200)
        hair_c = (255, 160, 160)

    walk = math.sin(t * 6)

    # chibi 比例常數
    hy   = cy - S(9)   # 頭部中心 Y（偏上）
    hr   = S(14)       # 頭部半徑（大頭）
    bw   = S(22)       # 身體寬度
    bh   = S(18)       # 身體高度
    bt_y = cy - S(3)   # 身體頂端 Y
    leg_w = S(7)
    leg_h = S(16)
    lt_y  = bt_y + bh  # 腿部頂端 Y

    # ── 鞋子 ─────────────────────────────────────────────────────────────────
    shoe_c = (28, 22, 18)
    wy = lt_y + leg_h
    pygame.draw.ellipse(screen, shoe_c,
                        (cx - S(13), wy + int(walk * S(2)), S(13), S(6)))
    pygame.draw.ellipse(screen, shoe_c,
                        (cx + S(1), wy - int(walk * S(2)), S(13), S(6)))

    # ── 腿部 ─────────────────────────────────────────────────────────────────
    leg_c = _leg_color(cid)
    pygame.draw.rect(screen, leg_c,
                     (cx - S(12), lt_y + int(walk * S(2)), leg_w, leg_h),
                     border_radius=S(3))
    pygame.draw.rect(screen, leg_c,
                     (cx + S(5), lt_y - int(walk * S(2)), leg_w, leg_h),
                     border_radius=S(3))

    # ── 身體 ─────────────────────────────────────────────────────────────────
    tx = cx - bw // 2
    pygame.draw.rect(screen, body_c, (tx, bt_y, bw, bh), border_radius=S(6))
    _chibi_torso_detail(screen, cid, cx, bt_y, bw, bh, body_c, det_c, skin_c, S)

    # ── 手臂 ─────────────────────────────────────────────────────────────────
    aw, ah = S(6), S(13)
    ay = bt_y + S(2)
    al = int(math.sin(t * 6 + math.pi) * S(2))
    ar = int(math.sin(t * 6) * S(2))
    pygame.draw.rect(screen, skin_c, (cx - bw // 2 - aw, ay + al, aw, ah), border_radius=S(3))
    pygame.draw.circle(screen, skin_c, (cx - bw // 2 - aw // 2, ay + al + ah), S(4))
    pygame.draw.rect(screen, skin_c, (cx + bw // 2, ay + ar, aw, ah), border_radius=S(3))
    pygame.draw.circle(screen, skin_c, (cx + bw // 2 + aw // 2, ay + ar + ah), S(4))

    # ── 頭部（大圓）──────────────────────────────────────────────────────────
    pygame.draw.circle(screen, skin_c, (cx, hy), hr)

    # ── 頭髮 ─────────────────────────────────────────────────────────────────
    _chibi_hair(screen, cid, cx, hy, hr, hair_c, S)

    # ── 五官 ─────────────────────────────────────────────────────────────────
    _chibi_face(screen, cid, cx, hy, hr, S, t)

    # ── 帽子 / 頭部配件 ──────────────────────────────────────────────────────
    _chibi_accessory(screen, cid, cx, hy, hr, hat_c, det_c, S, t)

    # ── 武器 ─────────────────────────────────────────────────────────────────
    _chibi_weapon(screen, cid, cx, cy, bt_y, bw, hy, hr, det_c, S)

    # ── 果實光環 ──────────────────────────────────────────────────────────────
    if current_fruit:
        fc = tuple(current_fruit["color"])
        gr = S(5) + int(abs(math.sin(t * 3)) * S(2))
        glow_y = lt_y + leg_h + S(3)
        pygame.draw.circle(screen, fc, (cx, glow_y), gr)
        pygame.draw.circle(screen, (255, 255, 255), (cx, glow_y), gr, 1)


# ── 身體顏色 helper ────────────────────────────────────────────────────────────

def _leg_color(cid):
    return {
        "luffy": (28, 28, 55),     # 深藍短褲
        "zoro":  (30, 55, 30),     # 深綠褲
        "nami":  (235, 220, 210),  # 膚色短裙下
        "sanji": (22, 22, 30),     # 黑褲
        "law":   (22, 18, 28),     # 深黑褲
    }.get(cid, (35, 30, 25))


# ── 身體細節 ──────────────────────────────────────────────────────────────────

def _chibi_torso_detail(screen, cid, cx, bt_y, bw, bh, body_c, det_c, skin_c, S):
    if cid == "luffy":
        # 紅背心 V領開口
        pygame.draw.polygon(screen, skin_c, [
            (cx, bt_y + S(2)),
            (cx - S(4), bt_y + S(9)),
            (cx + S(4), bt_y + S(9)),
        ])
        # 短褲上緣
        pygame.draw.rect(screen, (28, 28, 55),
                         (cx - bw // 2, bt_y + bh - S(5), bw, S(5)), border_radius=S(2))

    elif cid == "zoro":
        # 白色道服，綠色腰帶
        pygame.draw.rect(screen, det_c,
                         (cx - bw // 2 - S(1), bt_y + S(7), bw + S(2), S(6)), border_radius=S(2))

    elif cid == "nami":
        # 橘色上衣 + 白色迷你裙
        pygame.draw.polygon(screen, (245, 245, 248), [
            (cx - S(9), bt_y + S(10)),
            (cx + S(9), bt_y + S(10)),
            (cx + S(12), bt_y + bh),
            (cx - S(12), bt_y + bh),
        ])

    elif cid == "sanji":
        # 白色領帶 + 西裝翻領
        pygame.draw.polygon(screen, (220, 215, 210), [
            (cx - S(2), bt_y + S(2)),
            (cx + S(2), bt_y + S(2)),
            (cx + S(2), bt_y + S(11)),
            (cx, bt_y + S(14)),
            (cx - S(2), bt_y + S(11)),
        ])
        # 翻領
        pygame.draw.polygon(screen, body_c,
                            [(cx - bw // 2, bt_y), (cx - S(2), bt_y + S(8)), (cx - bw // 2, bt_y + S(9))])
        pygame.draw.polygon(screen, body_c,
                            [(cx + bw // 2, bt_y), (cx + S(2), bt_y + S(8)), (cx + bw // 2, bt_y + S(9))])

    elif cid == "law":
        # 黑色外套白色毛領
        fur_c = (235, 230, 222)
        pygame.draw.rect(screen, fur_c,
                         (cx - bw // 2 - S(1), bt_y, bw + S(2), S(7)), border_radius=S(4))
        pygame.draw.polygon(screen, (22, 18, 28), [
            (cx, bt_y + S(3)),
            (cx - S(3), bt_y + S(14)),
            (cx + S(3), bt_y + S(14)),
        ])


# ── 頭髮 ──────────────────────────────────────────────────────────────────────

def _chibi_hair(screen, cid, cx, hy, hr, hair_c, S):
    if cid == "luffy":
        # 黑色散亂瀏海（草帽下露出）
        for dx in range(-S(8), S(9), S(5)):
            pygame.draw.circle(screen, hair_c, (cx + dx, hy - hr + S(3)), S(5))
        pygame.draw.circle(screen, hair_c, (cx - hr + S(3), hy + S(2)), S(5))
        pygame.draw.circle(screen, hair_c, (cx + hr - S(3), hy + S(2)), S(5))

    elif cid == "zoro":
        # 短刺狀綠色頭髮
        pygame.draw.ellipse(screen, hair_c, (cx - hr + S(2), hy - hr, hr * 2 - S(4), hr + S(2)))
        for dx, dy in [(-S(8), -S(5)), (-S(3), -S(8)), (S(3), -S(8)), (S(8), -S(5))]:
            pygame.draw.circle(screen, hair_c, (cx + dx, hy - hr + dy), S(5))

    elif cid == "nami":
        # 長橘色頭髮
        pygame.draw.ellipse(screen, hair_c,
                            (cx - hr - S(3), hy - hr - S(1), hr * 2 + S(6), hr + S(3)))
        pygame.draw.ellipse(screen, hair_c, (cx - hr - S(5), hy, S(10), hr + S(10)))
        pygame.draw.ellipse(screen, hair_c, (cx + hr - S(5), hy, S(10), hr + S(10)))

    elif cid == "sanji":
        # 金色瀏海蓋住左眼
        pygame.draw.ellipse(screen, hair_c, (cx - hr, hy - hr, hr * 2, hr + S(2)))
        pygame.draw.ellipse(screen, hair_c, (cx - hr, hy - S(5), hr + S(5), hr + S(2)))

    elif cid == "law":
        # 黑色頭髮（帽子下露出少許）
        pygame.draw.ellipse(screen, hair_c, (cx - hr + S(3), hy - hr, hr * 2 - S(6), hr // 2 + S(3)))


# ── 五官 ──────────────────────────────────────────────────────────────────────

def _chibi_face(screen, cid, cx, hy, hr, S, t):
    ey  = hy + S(3)
    eox = S(5)
    er  = S(5)

    if cid == "sanji":
        # 只有右眼（左眼被頭髮遮住）
        _draw_eye(screen, cx + eox, ey, er, (38, 32, 22), S)
        # 左眼位置被頭髮遮，畫睫毛線
        pygame.draw.arc(screen, (20, 16, 10),
                        (cx - eox - er, ey - er, er * 2, er * 2), 0, math.pi, max(1, S(1)))
    elif cid == "zoro":
        # 索隆眼神較冷峻，眼睛小一點
        _draw_eye(screen, cx - eox, ey, er - S(1), (28, 55, 28), S)
        _draw_eye(screen, cx + eox, ey, er - S(1), (28, 55, 28), S)
    else:
        iris_c = {
            "luffy": (35, 28, 20),
            "nami":  (115, 58, 22),
            "law":   (85, 22, 115),
        }.get(cid, (32, 26, 18))
        _draw_eye(screen, cx - eox, ey, er, iris_c, S)
        _draw_eye(screen, cx + eox, ey, er, iris_c, S)

    # 鼻子（小點）
    pygame.draw.circle(screen, (190, 155, 120), (cx, hy + S(8)), S(1))

    # 嘴型
    if cid == "luffy":
        # 大笑
        pygame.draw.arc(screen, (22, 14, 10),
                        (cx - S(7), hy + S(8), S(14), S(8)), math.pi * 1.12, math.pi * 1.88, S(2))
        # 牙齒
        pygame.draw.rect(screen, (255, 252, 248),
                         (cx - S(4), hy + S(9), S(8), S(3)), border_radius=S(1))
    else:
        pygame.draw.arc(screen, (22, 14, 10),
                        (cx - S(4), hy + S(9), S(8), S(5)), math.pi * 1.2, math.pi * 1.8, max(1, S(1)))

    # 路飛左眼下方刀疤
    if cid == "luffy":
        pygame.draw.line(screen, (170, 55, 55),
                         (cx - eox + S(2), ey + er),
                         (cx - eox + S(4), ey + er + S(4)), max(1, S(1)))

    # 法律（羅）臉上的刺青標記（Ope Ope）
    if cid == "law":
        pygame.draw.circle(screen, (80, 22, 115), (cx + hr - S(3), hy + S(5)), S(2))


def _draw_eye(screen, ex, ey, er, iris_c, S):
    """Q版大眼睛：白色鞏膜 + 彩色虹膜 + 高光點"""
    pygame.draw.circle(screen, (252, 250, 246), (ex, ey), er)
    pygame.draw.circle(screen, iris_c, (ex, ey + S(1)), max(1, er - S(1)))
    # 睫毛（上弧）
    pygame.draw.arc(screen, (18, 13, 10),
                    (ex - er, ey - er, er * 2, er * 2),
                    math.pi * 0.12, math.pi * 0.88, max(1, S(1)))
    # 高光
    pygame.draw.circle(screen, (255, 255, 255),
                       (ex - max(1, er // 3), ey - max(1, er // 3)), max(1, er // 3))


# ── 帽子 / 配件 ───────────────────────────────────────────────────────────────

def _chibi_accessory(screen, cid, cx, hy, hr, hat_c, det_c, S, t):
    if cid == "luffy":
        # 超大草帽（比頭還寬！）
        brim_y = hy - hr + S(6)
        dome_w = hr * 2 + S(4)
        dome_h = S(11)
        brim_w = hr * 2 + S(18)

        pygame.draw.ellipse(screen, hat_c,
                            (cx - dome_w // 2, brim_y - dome_h, dome_w, dome_h * 2))
        pygame.draw.ellipse(screen, hat_c,
                            (cx - brim_w // 2, brim_y - S(2), brim_w, S(8)))
        # 紅色帽帶
        pygame.draw.arc(screen, (195, 32, 32),
                        (cx - dome_w // 2, brim_y - dome_h, dome_w, dome_h * 2),
                        math.pi * 0.45, math.pi * 1.55, S(3))
        # 帽緣輪廓
        pygame.draw.ellipse(screen, (158, 125, 36),
                            (cx - brim_w // 2, brim_y - S(2), brim_w, S(8)), 1)
        pygame.draw.ellipse(screen, (158, 125, 36),
                            (cx - dome_w // 2, brim_y - dome_h, dome_w, dome_h * 2), 1)

    elif cid == "zoro":
        # 綠色頭巾
        pygame.draw.rect(screen, det_c,
                         (cx - hr - S(1), hy - hr // 3, hr * 2 + S(2), S(5)), border_radius=S(2))
        # 頭巾結
        pygame.draw.circle(screen, det_c, (cx + hr, hy - hr // 3 + S(2)), S(4))
        pygame.draw.line(screen, det_c, (cx + hr, hy - S(1)),
                         (cx + hr + S(7), hy + S(3)), S(2))
        pygame.draw.line(screen, det_c, (cx + hr, hy - S(1)),
                         (cx + hr + S(7), hy - S(5)), S(2))

    elif cid == "nami":
        # 橘色小飾品（pinwheel 風車）
        px = cx + hr - S(1)
        py = hy - hr + S(4)
        pygame.draw.circle(screen, (255, 185, 30), (px, py), S(4))
        pygame.draw.circle(screen, (255, 228, 90), (px, py), S(2))
        # 小棍
        pygame.draw.line(screen, (170, 130, 60), (px, py), (px, py + S(8)), S(1))

    elif cid == "sanji":
        # 香菸
        cig_x = cx + hr - S(1)
        cig_y = hy + S(9)
        pygame.draw.line(screen, (238, 228, 215),
                         (cig_x, cig_y), (cig_x + S(9), cig_y - S(2)), S(3))
        pygame.draw.circle(screen, (255, 115, 28), (cig_x + S(9), cig_y - S(2)), S(2))
        smoke_off = int(math.sin(t * 2.2) * S(1))
        pygame.draw.circle(screen, (175, 175, 175),
                           (cig_x + S(9) + smoke_off, cig_y - S(6)), S(2))

    elif cid == "law":
        # 大型白色豹紋帽（非常標誌性）
        brim_y = hy - hr + S(5)
        dome_w = hr * 2 + S(6)
        dome_h = S(15)
        brim_w = hr * 2 + S(10)
        # 帽子主體（白色）
        pygame.draw.ellipse(screen, (242, 240, 236),
                            (cx - dome_w // 2, brim_y - dome_h, dome_w, dome_h * 2))
        # 黑色斑點（豹紋）
        for dx, dy in [(-S(5), -S(7)), (S(5), -S(9)), (-S(1), -S(3)),
                       (S(8), -S(5)), (-S(8), -S(2)), (S(2), -S(11))]:
            pygame.draw.circle(screen, (22, 18, 26), (cx + dx, brim_y - dome_h // 2 + dy), S(3))
        # 帽緣
        pygame.draw.ellipse(screen, (242, 240, 236),
                            (cx - brim_w // 2, brim_y - S(3), brim_w, S(8)))
        pygame.draw.ellipse(screen, (178, 174, 166),
                            (cx - brim_w // 2, brim_y - S(3), brim_w, S(8)), 1)
        pygame.draw.ellipse(screen, (178, 174, 166),
                            (cx - dome_w // 2, brim_y - dome_h, dome_w, dome_h * 2), 1)


# ── 武器 / 特殊配件 ───────────────────────────────────────────────────────────

def _chibi_weapon(screen, cid, cx, cy, bt_y, bw, hy, hr, det_c, S):
    if cid == "zoro":
        # 嘴裡咬著的刀
        sx1 = cx + hr - S(2)
        sy1 = hy + S(8)
        pygame.draw.line(screen, (188, 178, 160), (sx1, sy1), (sx1 + S(16), sy1 - S(3)), S(2))
        pygame.draw.rect(screen, (115, 80, 42), (sx1 - S(3), sy1 - S(3), S(5), S(6)), border_radius=S(1))
        # 腰間兩把刀（刀柄）
        for i, (side, dx) in enumerate([(-1, -S(14)), (1, S(7))]):
            hx = cx + dx
            hy2 = bt_y + S(16)
            pygame.draw.line(screen, (188, 178, 160), (hx, hy2), (hx + side * S(7), hy2 - S(12)), S(2))
            # 刀鍔
            pygame.draw.rect(screen, (115, 80, 42), (hx - S(2), hy2 - S(3), S(4), S(5)), border_radius=S(1))

    elif cid == "nami":
        # 天氣棒（左側）
        wx = cx - bw // 2 - S(9)
        pygame.draw.line(screen, (190, 158, 75), (wx, cy - S(14)), (wx, cy + S(18)), S(2))
        pygame.draw.circle(screen, (55, 140, 215), (wx, cy - S(16)), S(5))
        pygame.draw.circle(screen, (130, 198, 248), (wx, cy - S(16)), S(3))

    elif cid == "law":
        # 剃刀（右側長刀）
        wx = cx + bw // 2 + S(7)
        pygame.draw.line(screen, (188, 182, 168), (wx, cy - S(20)), (wx, cy + S(24)), S(2))
        # 刀鍔
        pygame.draw.rect(screen, (78, 68, 52), (wx - S(5), cy - S(4), S(10), S(4)), border_radius=S(1))
        # 刀柄
        pygame.draw.line(screen, (115, 80, 42), (wx, cy - S(4)), (wx, cy + S(24)), S(3))
