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
    """Bold modern EN cover — huge logo character, floating orbs, thick outlines."""
    img = Image.new("RGB", (SIZE, SIZE), "#0f0f23")
    draw = ImageDraw.Draw(img)

    cx, cy = SIZE // 2, 500

    # ── Floating orbs in background ──
    orb_data = [
        (120, 180, 55, (255, 120, 70, 180)),
        (1280, 150, 40, (255, 180, 50, 160)),
        (80, 600, 70, (255, 90, 60, 140)),
        (1320, 550, 48, (255, 200, 60, 150)),
        (200, 950, 60, (255, 140, 80, 130)),
        (1200, 900, 50, (245, 190, 55, 140)),
        (160, 1200, 38, (255, 110, 65, 120)),
        (1240, 1150, 44, (255, 170, 50, 130)),
        (400, 140, 30, (255, 150, 70, 160)),
        (1000, 100, 36, (255, 190, 55, 150)),
        (60, 380, 25, (255, 130, 75, 170)),
        (1340, 350, 28, (255, 160, 50, 165)),
    ]
    for ox, oy, r, color in orb_data:
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=color[:3])
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], outline="#0f0f23", width=8)
        # Inner highlight
        draw.ellipse([ox - r//3, oy - r//3, ox + r//3, oy + r//3], fill=(min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255)))

    # ── Giant geometric burst behind character ──
    burst_colors = [
        (255, 90, 60), (255, 180, 50), (255, 120, 80),
        (245, 200, 60), (255, 100, 70), (255, 160, 45),
    ]
    for i in range(6):
        angle = math.radians(i * 60 - 15)
        r = 480
        x1 = cx + math.cos(angle) * 80
        y1 = cy + math.sin(angle) * 80
        x2 = cx + math.cos(angle + 0.35) * r
        y2 = cy + math.sin(angle + 0.35) * r
        x3 = cx + math.cos(angle - 0.35) * r
        y3 = cy + math.sin(angle - 0.35) * r
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=burst_colors[i])
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], outline="#0f0f23", width=16)

    # ── Central circle ──
    for r in range(360, 0, -2):
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(255, 245, 230) if r % 4 == 0 else (255, 252, 242),
        )
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline="#0f0f23", width=20)

    # ═══════════════════════════════════════════════
    # 🎤 HUGE LOGO CHARACTER — fills the circle
    # ═══════════════════════════════════════════════

    # ── Head (MASSIVE, fills 90% of circle) ──
    head_r = 290
    draw.ellipse(
        [cx - head_r, cy - 260, cx + head_r, cy + 250],
        fill=(255, 205, 155), outline="#0f0f23", width=16,
    )

    # ── Hair (bold geometric block) ──
    hair_color = (45, 25, 15)
    draw.ellipse([cx - 310, cy - 300, cx + 310, cy - 40], fill=hair_color)
    draw.ellipse([cx - 310, cy - 300, cx + 310, cy - 40], outline="#0f0f23", width=14)
    # Side hair swoops
    for side, sx in [(-1, cx - 290), (1, cx + 130)]:
        pts = [
            (sx, cy - 200), (sx + side * 120, cy - 140),
            (sx + side * 70, cy + 40), (sx + side * 15, cy - 60),
        ]
        draw.polygon(pts, fill=hair_color, outline="#0f0f23", width=12)

    # ── EYES (BIG BOLD, scaled up) ──
    eye_y = cy - 90
    eye_spacing = 100
    for ex in [cx - eye_spacing, cx + eye_spacing]:
        eye_w, eye_h = 70, 62
        # White
        draw.ellipse(
            [ex - eye_w, eye_y - eye_h, ex + eye_w, eye_y + eye_h],
            fill="white", outline="#0f0f23", width=14,
        )
        # Iris
        iris_r = 40
        draw.ellipse(
            [ex - iris_r, eye_y - 30, ex + iris_r, eye_y + 50],
            fill=(75, 35, 18), outline="#0f0f23", width=10,
        )
        # Pupil
        draw.ellipse([ex - 18, eye_y - 4, ex + 18, eye_y + 36], fill="#0f0f23")
        # Big sparkle
        draw.ellipse([ex - 30, eye_y - 42, ex - 10, eye_y - 22], fill="white")
        draw.ellipse([ex + 6, eye_y - 6, ex + 16, eye_y + 4], fill="white")

    # Eyebrows
    for ex in [cx - eye_spacing, cx + eye_spacing]:
        draw.line([(ex - 65, eye_y - 72), (ex + 65, eye_y - 72)], fill="#0f0f23", width=20)

    # ── Blush (big circles) ──
    for bx in [cx - 160, cx + 160]:
        draw.ellipse([bx - 45, eye_y + 28, bx + 45, eye_y + 78], fill=(255, 165, 165), outline="#0f0f23", width=8)

    # ── Nose ──
    draw.ellipse([cx - 18, eye_y + 42, cx + 18, eye_y + 78], fill=(255, 165, 128), outline="#0f0f23", width=8)

    # ── BIG SMILE ──
    mouth_y = eye_y + 115
    draw.arc([cx - 55, mouth_y - 18, cx + 55, mouth_y + 45], start=0, end=170, fill="#0f0f23", width=14)

    # ── CHUNKY HEADPHONES (bigger, bolder) ──
    hp_color = (255, 50, 80)
    hp_top = cy - 330
    draw.arc([cx - 300, hp_top, cx + 300, hp_top + 200], start=0, end=360, fill="#0f0f23", width=26)
    draw.arc([cx - 300, hp_top + 13, cx + 300, hp_top + 174], start=0, end=360, fill=hp_color, width=22)
    for ecx in [cx - 315, cx + 315]:
        draw.ellipse([ecx - 60, hp_top + 60, ecx + 60, hp_top + 170], fill=hp_color, outline="#0f0f23", width=14)
        draw.ellipse([ecx - 36, hp_top + 85, ecx + 36, hp_top + 150], fill=(255, 130, 150), outline="#0f0f23", width=8)

    # ── GIANT MIC (on the side, bold) ──
    mic_x, mic_y = cx + 270, cy - 60
    draw.rounded_rectangle([mic_x - 18, mic_y, mic_x + 18, mic_y + 80], radius=8, fill=(45, 45, 55), outline="#0f0f23", width=12)
    draw.ellipse([mic_x - 32, mic_y - 75, mic_x + 32, mic_y - 8], fill=(75, 75, 95), outline="#0f0f23", width=12)
    for dy in range(-62, -18, 8):
        draw.line([(mic_x - 20, mic_y + dy), (mic_x + 20, mic_y + dy)], fill="#0f0f23", width=6)

    # ═══════════════════════════════════════════════
    # ✨ BOLD TYPOGRAPHY — massive, readable
    # ═══════════════════════════════════════════════
    try:
        huge_font = load_font(EN_FONT, 130, index=2)
    except Exception:
        huge_font = ImageFont.load_default()
    try:
        small_font = load_font(EN_FONT, 32, index=0)
    except Exception:
        small_font = huge_font

    # Text background bar
    draw.rectangle([0, 1050, SIZE, SIZE], fill="#0f0f23")
    draw.rectangle([0, 1050, SIZE, 1058], fill=(255, 90, 60))

    for text, y, color in [
        ("DAILY", 1090, (255, 255, 255)),
        ("NEWS", 1230, (255, 220, 50)),
    ]:
        tw = draw.textlength(text, font=huge_font)
        dx = (SIZE - tw) / 2
        for off in [(-5,-5),(5,-5),(-5,5),(5,5),(-4,0),(4,0),(0,-4),(0,4)]:
            draw.text((dx+off[0], y+off[1]), text, fill="#0f0f23", font=huge_font)
        draw.text((dx, y), text, fill=color, font=huge_font)

    credit = "by Rinちゃん ⚡  ·  Every Morning 7am SGT"
    cw = draw.textlength(credit, font=small_font)
    draw.text(((SIZE - cw) / 2, 1380), credit, fill=(180, 170, 190), font=small_font)

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
