#!/usr/bin/env python3
"""Generate podcast cover art — dynamic EN + bold readable JP."""
from PIL import Image, ImageDraw, ImageFont
import math, os, glob, shutil

SIZE = 1400
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

EN_FONT = "/System/Library/Fonts/HelveticaNeue.ttc"


def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()


def draw_centered_text(draw, text, font, y, fill, img_w=SIZE, shadow=False):
    """Draw centered text with optional drop shadow."""
    tw = draw.textlength(text, font=font)
    x = (img_w - tw) / 2
    if shadow:
        draw.text((x + 3, y + 3), text, fill=(0, 0, 0, 100), font=font)
    draw.text((x, y), text, fill=fill, font=font)
    return x, tw


def make_jp_cover():
    """Japanese cover — bold Hiragino Heavy for reliable iOS rendering."""
    img = Image.new("RGB", (SIZE, SIZE), "#0d0d1f")
    draw = ImageDraw.Draw(img)

    # Gradient: deep navy → midnight blue → dark teal
    for y in range(SIZE):
        ratio = y / SIZE
        r = int(13 + ratio * 25)
        g = int(13 + ratio * 28)
        b = int(31 + ratio * 40)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))

    # Large glowing accent circle top-right
    for r in range(400, 0, -1):
        draw.ellipse(
            [SIZE - 150 - r, -80 - r, SIZE - 150 + r, -80 + r],
            fill=(200, 50, 35) if r % 3 == 0 else (215, 55, 40),
        )

    # Accent bars
    draw.rectangle([60, 470, 1340, 476], fill=(210, 60, 42))
    draw.rectangle([60, 910, 1340, 916], fill=(210, 60, 42))

    # Decorative dots
    for cx, cy, r, color in [
        (80, 180, 22, (210, 85, 55)),
        (1320, 160, 18, (210, 85, 55)),
        (100, 980, 16, (190, 100, 75)),
        (1300, 1020, 20, (190, 100, 75)),
        (90, 1180, 14, (210, 85, 55)),
        (1310, 1220, 12, (210, 85, 55)),
    ]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # ── Fonts: use Hiragino (proven macOS rendering) ──
    font_bold = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"  # W9 = Heavy
    font_reg = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"   # W8 = Bold
    title_font = load_font(font_bold, 76, index=0)
    sub_font = load_font(font_reg, 36, index=0)
    tag_font = load_font(font_reg, 28, index=0)

    # Dark band behind text for maximum contrast
    draw.rectangle([0, 440, SIZE, 820], fill=(8, 8, 22, 200))

    # Title — bold white, triple-shadow for pop
    title = "Rinちゃんの今日のニュース"
    tw = draw.textlength(title, font=title_font)
    x = (SIZE - tw) / 2
    # Thick shadow/outline
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw.text((x + dx, 545 + dy), title, fill="#000000", font=title_font)
    draw.text((x, 545), title, fill="#ffffff", font=title_font)

    # Subtitle
    subtitle = "毎朝お届け・世界の重要ニュース トップ5"
    sw = draw.textlength(subtitle, font=sub_font)
    sx = (SIZE - sw) / 2
    draw.text((sx + 2, 655 + 2), subtitle, fill="#000000", font=sub_font)
    draw.text((sx, 655), subtitle, fill=(230, 200, 195), font=sub_font)

    # Accent text
    sub2 = "政治・経済・テクノロジー・国際情勢"
    s2w = draw.textlength(sub2, font=sub_font)
    s2x = (SIZE - s2w) / 2
    draw.text((s2x + 2, 720 + 2), sub2, fill="#000000", font=sub_font)
    draw.text((s2x, 720), sub2, fill=(190, 165, 155), font=sub_font)

    # Source line
    sources = "📡 BBC · Reuters · AP · Straits Times  |  毎朝7時 (SGT) 配信"
    sw3 = draw.textlength(sources, font=tag_font)
    s3x = (SIZE - sw3) / 2
    draw.text((s3x, 795), sources, fill=(170, 150, 145), font=tag_font)

    # Bottom tag
    tag = "✦ AIキュレーション ✦ 毎日更新 ✦"
    tw4 = draw.textlength(tag, font=tag_font)
    draw.text(((SIZE - tw4) / 2, SIZE - 100), tag, fill=(120, 110, 120), font=tag_font)

    # Logo mark
    logo_text = "⚡Rinちゃん⚡"
    logo_font = load_font(font_reg, 44, index=0)
    lw = draw.textlength(logo_text, font=logo_font)
    draw.text(((SIZE - lw) / 2 + 2, SIZE - 172), logo_text, fill="#000000", font=logo_font)
    draw.text(((SIZE - lw) / 2, SIZE - 170), logo_text, fill=(230, 100, 80), font=logo_font)

    path = os.path.join(OUT_DIR, "cover-ja.jpg")
    img.save(path, "JPEG", quality=92)
    # Save timestamped copy for cache busting
    ts_path = os.path.join(OUT_DIR, f"cover-ja-{int(os.path.getmtime(path))}.jpg")
    shutil.copy2(path, ts_path)
    print(f"✅ JP cover: {path} ({os.path.getsize(path)/1024:.0f} KB) + {os.path.basename(ts_path)}")
    return path


def draw_star(draw, cx, cy, size, color, points=4):
    """Draw a sparkle star."""
    if points == 4:
        pts = [
            (cx, cy - size), (cx + size // 3, cy - size // 3),
            (cx + size, cy), (cx + size // 3, cy + size // 3),
            (cx, cy + size), (cx - size // 3, cy + size // 3),
            (cx - size, cy), (cx - size // 3, cy - size // 3),
        ]
        draw.polygon(pts, fill=color)


def make_en_cover():
    """Bold modern EN cover — thick outlines, flat colors, oversized icon, app-icon style."""
    img = Image.new("RGB", (SIZE, SIZE), "#0f0f23")
    draw = ImageDraw.Draw(img)

    cx, cy = SIZE // 2, 480

    # ── Giant geometric burst behind character ──
    burst_colors = [
        (255, 90, 60), (255, 180, 50), (255, 120, 80),
        (245, 200, 60), (255, 100, 70), (255, 160, 45),
    ]
    for i in range(6):
        angle = math.radians(i * 60 - 15)
        r = 440
        x1 = cx + math.cos(angle) * 80
        y1 = cy + math.sin(angle) * 80
        x2 = cx + math.cos(angle + 0.35) * r
        y2 = cy + math.sin(angle + 0.35) * r
        x3 = cx + math.cos(angle - 0.35) * r
        y3 = cy + math.sin(angle - 0.35) * r
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=burst_colors[i])
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], outline="#0f0f23", width=14)

    # ── Central circle behind character ──
    for r in range(340, 0, -2):
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(255, 240, 220) if r % 4 == 0 else (255, 250, 235),
        )
    draw.ellipse([cx - 340, cy - 340, cx + 340, cy + 340], outline="#0f0f23", width=18)

    # ═══════════════════════════════════════════════
    # 🎤 BOLD CHARACTER — thick outlines, flat colors
    # ═══════════════════════════════════════════════
    hx, hy = cx, cy - 10

    # Neck
    draw.rectangle([hx - 50, hy + 130, hx + 50, hy + 240], fill=(255, 190, 140))
    draw.rectangle([hx - 50, hy + 130, hx + 50, hy + 240], outline="#0f0f23", width=12)
    # Collar (teal)
    collar = (50, 210, 180)
    draw.polygon(
        [(hx - 90, hy + 160), (hx, hy + 200), (hx + 90, hy + 160), (hx, hy + 140)],
        fill=collar, outline="#0f0f23", width=10,
    )

    # Head
    head_r = 175
    draw.ellipse(
        [hx - head_r, hy - 165, hx + head_r, hy + 145],
        fill=(255, 200, 150), outline="#0f0f23", width=14,
    )

    # Hair (bold geometric block, thick outline)
    hair_color = (45, 25, 15)
    draw.ellipse([hx - 190, hy - 195, hx + 190, hy - 25], fill=hair_color)
    draw.ellipse([hx - 190, hy - 195, hx + 190, hy - 25], outline="#0f0f23", width=12)
    for side, sx in [(-1, hx - 180), (1, hx + 50)]:
        pts = [
            (sx, hy - 120), (sx + side * 80, hy - 80),
            (sx + side * 40, hy + 20), (sx + side * 10, hy - 40),
        ]
        draw.polygon(pts, fill=hair_color, outline="#0f0f23", width=10)

    # ── EYES (big bold, thick outlines) ──
    eye_y = hy - 55
    eye_spacing = 64
    for ex in [hx - eye_spacing, hx + eye_spacing]:
        eye_w, eye_h = 52, 46
        draw.ellipse(
            [ex - eye_w, eye_y - eye_h, ex + eye_w, eye_y + eye_h],
            fill="white", outline="#0f0f23", width=12,
        )
        iris_r = 29
        draw.ellipse(
            [ex - iris_r, eye_y - 22, ex + iris_r, eye_y + 36],
            fill=(70, 30, 15), outline="#0f0f23", width=8,
        )
        draw.ellipse([ex - 14, eye_y - 4, ex + 14, eye_y + 26], fill="#0f0f23")
        draw.ellipse([ex - 22, eye_y - 30, ex - 6, eye_y - 14], fill="white")
        draw.ellipse([ex + 4, eye_y - 2, ex + 12, eye_y + 6], fill="white")

    # Eyebrows
    for ex in [hx - eye_spacing, hx + eye_spacing]:
        draw.line([(ex - 48, eye_y - 54), (ex + 48, eye_y - 54)], fill="#0f0f23", width=16)

    # Nose
    draw.ellipse([hx - 14, eye_y + 30, hx + 14, eye_y + 58], fill=(255, 160, 120))
    draw.arc([hx - 16, eye_y + 28, hx + 16, eye_y + 58], start=0, end=180, fill="#0f0f23", width=6)

    # Mouth
    mouth_y = eye_y + 82
    draw.arc([hx - 38, mouth_y - 12, hx + 38, mouth_y + 32], start=0, end=170, fill="#0f0f23", width=10)

    # Blush
    for bx in [hx - 105, hx + 105]:
        draw.ellipse([bx - 32, eye_y + 18, bx + 32, eye_y + 52], fill=(255, 160, 160), outline="#0f0f23", width=6)

    # ── CHUNKY HEADPHONES ──
    hp_color = (255, 55, 85)
    hp_top = hy - 205
    draw.arc([hx - 185, hp_top, hx + 185, hp_top + 125], start=0, end=360, fill="#0f0f23", width=22)
    draw.arc([hx - 185, hp_top + 11, hx + 185, hp_top + 103], start=0, end=360, fill=hp_color, width=18)
    for ecx in [hx - 200, hx + 200]:
        draw.ellipse([ecx - 42, hp_top + 42, ecx + 42, hp_top + 115], fill=hp_color, outline="#0f0f23", width=12)
        draw.ellipse([ecx - 24, hp_top + 58, ecx + 24, hp_top + 100], fill=(255, 130, 150), outline="#0f0f23", width=6)

    # ── GIANT MIC ──
    mic_x, mic_y = hx + 175, hy - 35
    draw.rounded_rectangle([mic_x - 14, mic_y, mic_x + 14, mic_y + 60], radius=7, fill=(50, 50, 60), outline="#0f0f23", width=10)
    draw.ellipse([mic_x - 24, mic_y - 58, mic_x + 24, mic_y - 5], fill=(80, 80, 100), outline="#0f0f23", width=10)
    for dy in range(-48, -12, 6):
        draw.line([(mic_x - 15, mic_y + dy), (mic_x + 15, mic_y + dy)], fill="#0f0f23", width=5)

    # ── Sparkle stars ──
    for sx, sy, ss in [
        (220, 130, 28), (1180, 100, 24), (150, 750, 20),
        (1250, 680, 26), (280, 1050, 18), (1120, 1020, 22),
    ]:
        pts = [
            (sx, sy - ss), (sx + ss//3, sy - ss//3),
            (sx + ss, sy), (sx + ss//3, sy + ss//3),
            (sx, sy + ss), (sx - ss//3, sy + ss//3),
            (sx - ss, sy), (sx - ss//3, sy - ss//3),
        ]
        draw.polygon(pts, fill=(255, 220, 60), outline="#0f0f23", width=6)

    # ═══════════════════════════════════════════════
    # ✨ BOLD TYPOGRAPHY — modern, oversized
    # ═══════════════════════════════════════════════
    try:
        huge_font = load_font(EN_FONT, 120, index=2)
    except Exception:
        huge_font = ImageFont.load_default()
    try:
        small_font = load_font(EN_FONT, 30, index=0)
    except Exception:
        small_font = huge_font

    # Dark band at bottom for text
    draw.rectangle([0, 1000, SIZE, SIZE], fill="#0f0f23")
    draw.rectangle([0, 1000, SIZE, 1006], fill=(255, 90, 60))

    for text, y, color in [
        ("DAILY", 1030, "white"),
        ("NEWS", 1160, (255, 210, 50)),
    ]:
        tw = draw.textlength(text, font=huge_font)
        dx = (SIZE - tw) / 2
        for off in [(-4,-4),(4,-4),(-4,4),(4,4),(-3,0),(3,0),(0,-3),(0,3)]:
            draw.text((dx+off[0], y+off[1]), text, fill="#0f0f23", font=huge_font)
        draw.text((dx, y), text, fill=color, font=huge_font)

    credit = "by Rinちゃん ⚡  ·  Every Morning 7am SGT"
    cw = draw.textlength(credit, font=small_font)
    draw.text(((SIZE - cw) / 2, 1330), credit, fill=(180, 170, 190), font=small_font)

    path = os.path.join(OUT_DIR, "cover-en.jpg")
    img.save(path, "JPEG", quality=92)
    ts_path = os.path.join(OUT_DIR, f"cover-en-{int(os.path.getmtime(path))}.jpg")
    shutil.copy2(path, ts_path)
    print(f"✅ EN cover: {path} ({os.path.getsize(path)/1024:.0f} KB) + {os.path.basename(ts_path)}")
    return path


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_jp_cover()
    make_en_cover()
    print("Done! Both covers generated.")
