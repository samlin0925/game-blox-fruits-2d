"""
生成遊戲圖示 icon.ico
使用 pygame 程式繪製惡魔果實圖示，無需外部圖片
執行：python release/generate_icon.py
輸出：release/icon.ico
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import math


def draw_icon(surface, size):
    cx, cy = size // 2, size // 2
    r = size // 2 - 2

    # 背景漸層（深紫到深藍）
    for y in range(size):
        ratio = y / size
        c = (int(20 + 15 * ratio), int(5 + 10 * ratio), int(40 + 20 * ratio))
        pygame.draw.line(surface, c, (0, y), (size, y))

    # 外圈金色光環
    pygame.draw.circle(surface, (180, 140, 0), (cx, cy), r, max(1, size // 16))
    pygame.draw.circle(surface, (255, 200, 50), (cx, cy), r - max(1, size // 16), max(1, size // 20))

    # 果實主體（橙紅色）
    fruit_r = int(r * 0.6)
    pygame.draw.circle(surface, (220, 60, 20), (cx, cy), fruit_r)
    pygame.draw.circle(surface, (255, 100, 40), (cx, cy - fruit_r // 6), int(fruit_r * 0.85))
    pygame.draw.circle(surface, (255, 160, 80), (cx - fruit_r // 4, cy - fruit_r // 4),
                       int(fruit_r * 0.3))

    # 果實螺旋紋（Blox Fruits 風格）
    swirl_r = int(fruit_r * 0.7)
    steps = 60
    for i in range(steps):
        a = math.radians(i * 6)
        dist = swirl_r * (i / steps)
        px2 = cx + int(math.cos(a) * dist)
        py2 = cy + int(math.sin(a) * dist)
        pr2 = max(1, int(size * 0.04 * (1 - i / steps)))
        pygame.draw.circle(surface, (255, 220, 100), (px2, py2), pr2)

    # 葉莖
    stem_w = max(2, size // 20)
    stem_h = max(4, size // 8)
    stem_x = cx - stem_w // 2
    stem_y = cy - fruit_r
    pygame.draw.rect(surface, (40, 120, 30),
                     (stem_x, stem_y - stem_h, stem_w, stem_h),
                     border_radius=stem_w // 2)
    # 小葉片
    leaf_pts = [
        (cx, stem_y - stem_h),
        (cx + size // 6, stem_y - stem_h - size // 8),
        (cx + size // 10, stem_y - stem_h + size // 12),
    ]
    if len(leaf_pts) >= 3:
        pygame.draw.polygon(surface, (60, 160, 40), leaf_pts)


def save_ico(sizes=(256, 128, 64, 48, 32, 16)):
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)

    surfaces = []
    for size in sizes:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        draw_icon(surf, size)
        surfaces.append(surf)

    # Save as PNG first (largest), then convert to ICO using PIL if available
    out_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(out_dir, "icon.png")
    ico_path = os.path.join(out_dir, "icon.ico")

    pygame.image.save(surfaces[0], png_path)
    print(f"Saved icon PNG: {png_path}")

    try:
        from PIL import Image
        imgs = []
        for surf in surfaces:
            raw = pygame.image.tostring(surf, "RGBA")
            img = Image.frombytes("RGBA", surf.get_size(), raw)
            imgs.append(img)
        imgs[0].save(ico_path, format="ICO",
                     sizes=[(s.get_width(), s.get_height()) for s in surfaces])
        print(f"Saved icon ICO: {ico_path}")
    except ImportError:
        print("Pillow not installed. Only PNG saved.")
        print("Install with: pip install Pillow")
        print("Or use an online converter to convert icon.png → icon.ico")

    pygame.quit()


if __name__ == "__main__":
    save_ico()
