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
    """Stylish EN cover — logo monogram center, JP-style orbs, bold 'Rin's DAILY NEWS'."""
    img = Image.new("RGB", (SIZE, SIZE), "#0d0d1f")
    draw = ImageDraw.Draw(img)

    cx, cy = SIZE // 2, 500

    # ── Background: deep navy gradient (matching JP) ──
    for y in range(SIZE):
        ratio = y / SIZE
        r = int(13 + ratio * 25)
        g = int(13 + ratio * 28)
        b = int(31 + ratio * 40)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))

    # ── Large glowing accent circle top-right (matching JP) ──
    for r in range(380, 0, -1):
        draw.ellipse(
            [SIZE - 130 - r, -70 - r, SIZE - 130 + r, -70 + r],
            fill=(200, 50, 35) if r % 3 == 0 else (215, 55, 40),
        )

    # ── Subtle decorative orbs (JP-style: small, simple) ──
    for ox, oy, r, color in [
        (100, 200, 22, (200, 80, 60)),
        (130, 950, 16, (180, 100, 80)),
        (1280, 1000, 20, (180, 100, 80)),
        (100, 1150, 14, (200, 80, 60)),
        (1290, 1200, 12, (200, 80, 60)),
        (250, 350, 10, (210, 90, 65)),
        (80, 600, 8, (190, 110, 85)),
        (1320, 650, 10, (190, 110, 85)),
    ]:
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=color)

    # ── Giant geometric burst ──
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
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], outline="#0d0d1f", width=16)

    # ── Central circle ──
    for r in range(340, 0, -2):
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(255, 248, 238) if r % 4 == 0 else (255, 252, 245),
        )
    draw.ellipse([cx - 340, cy - 340, cx + 340, cy + 340], outline="#0d0d1f", width=20)

    # ═══════════════════════════════════════════════
    # ✦ STYLISH LOGO MONOGRAM — "R⚡" center
    # ═══════════════════════════════════════════════
    # Dark rounded square backdrop
    draw.rounded_rectangle(
        [cx - 200, cy - 200, cx + 200, cy + 200],
        radius=40, fill="#0d0d1f",
    )
    draw.rounded_rectangle(
        [cx - 200, cy - 200, cx + 200, cy + 200],
        radius=40, outline="#0d0d1f", width=8,
    )

    # "R" — big bold letter as logo
    try:
        logo_font = load_font(EN_FONT, 280, index=2)  # Helvetica Neue Bold
    except Exception:
        logo_font = ImageFont.load_default()

    letter_r = "R"
    rw = draw.textlength(letter_r, font=logo_font)
    rx = cx - rw / 2
    ry = cy - 155
    # Outline
    for off in [(-4,-4),(4,-4),(-4,4),(4,4),(-3,0),(3,0),(0,-3),(0,3)]:
        draw.text((rx+off[0], ry+off[1]), letter_r, fill="#0d0d1f", font=logo_font)
    draw.text((rx, ry), letter_r, fill=(255, 200, 50), font=logo_font)

    # Small lightning bolt accent on the R (top-right of letter)
    bolt_color = (255, 140, 40)
    bolt_cx, bolt_cy = cx + 110, cy - 130
    bolt = [
        (bolt_cx, bolt_cy - 30),
        (bolt_cx - 18, bolt_cy + 5),
        (bolt_cx + 2, bolt_cy + 5),
        (bolt_cx - 8, bolt_cy + 35),
        (bolt_cx + 14, bolt_cy - 10),
        (bolt_cx - 6, bolt_cy - 10),
        (bolt_cx + 10, bolt_cy - 30),
    ]
    draw.polygon(bolt, fill=bolt_color)
    draw.polygon(bolt, outline="#0d0d1f", width=6)

    # ── Accent bars (matching JP) ──
    draw.rectangle([60, 470, 1340, 476], fill=(210, 60, 42))
    draw.rectangle([60, 920, 1340, 926], fill=(210, 60, 42))

    # ═══════════════════════════════════════════════
    # ✨ "Rin's DAILY NEWS" — bold typography
    # ═══════════════════════════════════════════════
    try:
        title_font = load_font(EN_FONT, 110, index=2)
    except Exception:
        title_font = ImageFont.load_default()
    try:
        small_font = load_font(EN_FONT, 32, index=0)
    except Exception:
        small_font = title_font

    # Text area
    draw.rectangle([0, 1050, SIZE, SIZE], fill="#0d0d1f")
    draw.rectangle([0, 1050, SIZE, 1058], fill=(210, 60, 42))

    for text, y, color in [
        ("Rin's", 1080, (255, 180, 60)),
        ("DAILY NEWS", 1200, (255, 255, 255)),
    ]:
        tw = draw.textlength(text, font=title_font)
        dx = (SIZE - tw) / 2
        for off in [(-4,-4),(4,-4),(-4,4),(4,4),(-3,0),(3,0),(0,-3),(0,3)]:
            draw.text((dx+off[0], y+off[1]), text, fill="#0d0d1f", font=title_font)
        draw.text((dx, y), text, fill=color, font=title_font)

    credit = "by Rinちゃん ⚡  ·  Every Morning 7am SGT"
    cw = draw.textlength(credit, font=small_font)
    draw.text(((SIZE - cw) / 2, 1360), credit, fill=(180, 170, 190), font=small_font)

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
