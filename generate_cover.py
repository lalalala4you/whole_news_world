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
    """Bold sticker-style EN cover — cute headshot character, minimal text, high contrast."""
    img = Image.new("RGB", (SIZE, SIZE), "#2d0a3d")
    draw = ImageDraw.Draw(img)

    # ── Background: deep purple → warm magenta gradient ──
    for y in range(SIZE):
        ratio = y / SIZE
        r = int(45 + ratio * 80)
        g = int(10 + ratio * 40)
        b = int(61 + ratio * 80)
        draw.line([(0, y), (SIZE, y)], fill=(min(r, 255), min(g, 255), min(b, 255)))

    # ── Large glowing circle behind character ──
    for r in range(380, 0, -1):
        alpha = 0.4
        draw.ellipse(
            [700 - r, 340 - r, 700 + r, 340 + r],
            fill=(
                int(255 - r * 0.3),
                int(180 - r * 0.25),
                int(100 - r * 0.15),
            ),
        )

    # ── Radial sunburst from center ──
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        for dist in [200, 280, 360]:
            ex = 700 + math.cos(rad) * dist
            ey = 340 + math.sin(rad) * dist
            r = 4 if dist < 250 else 3
            draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(255, 220, 120))

    # ── Sparkle stars scattered ──
    for sx, sy, ss, col in [
        (120, 150, 28, (255, 230, 100)),
        (1280, 180, 22, (255, 200, 120)),
        (80, 650, 18, (255, 240, 140)),
        (1320, 600, 24, (255, 220, 100)),
        (200, 1100, 20, (255, 200, 120)),
        (1200, 1050, 26, (255, 230, 100)),
        (350, 1200, 16, (255, 240, 140)),
    ]:
        draw_star(draw, sx, sy, ss, col)

    # ═══════════════════════════════════════════════
    # 🎀 CUTE STICKER-STYLE HEADSHOT CHARACTER
    #    Round chubby face, sparkly anime eyes, headphones
    # ═══════════════════════════════════════════════
    cx, cy = 700, 340

    # ── Body (simple rounded shape below head) ──
    draw.ellipse([cx - 100, cy - 10, cx + 100, cy + 170], fill=(255, 140, 80))
    # Collar / shirt line
    draw.ellipse([cx - 85, cy + 40, cx + 85, cy + 110], fill=(255, 170, 120))

    # ── Head (big round, cute proportions) ──
    head_r = 125
    draw.ellipse(
        [cx - head_r, cy - 165, cx + head_r, cy + 60],
        fill=(255, 200, 160),
    )

    # ── Hair / bangs (messy cute style, dark brown) ──
    hair_color = (60, 30, 20)
    # Main hair blob
    draw.ellipse([cx - 135, cy - 185, cx + 135, cy - 60], fill=hair_color)
    # Side hair
    draw.ellipse([cx - 140, cy - 130, cx - 80, cy + 20], fill=hair_color)
    draw.ellipse([cx + 80, cy - 130, cx + 140, cy + 20], fill=hair_color)
    # Bangs across forehead
    for bx in range(-100, 110, 25):
        draw.ellipse([cx + bx - 20, cy - 190, cx + bx + 20, cy - 95], fill=hair_color)

    # ── EYES (big sparkly anime style) ──
    eye_y = cy - 80
    eye_spacing = 50
    eye_w, eye_h = 48, 52

    for ex in [cx - eye_spacing, cx + eye_spacing]:
        # White of eye
        draw.ellipse([ex - eye_w, eye_y - eye_h, ex + eye_w, eye_y + eye_h], fill="white")
        # Eye outline
        draw.ellipse(
            [ex - eye_w, eye_y - eye_h, ex + eye_w, eye_y + eye_h],
            outline=(30, 15, 10), width=4,
        )
        # Iris (big warm brown)
        iris_r = 30
        draw.ellipse(
            [ex - iris_r, eye_y - iris_r + 5, ex + iris_r, eye_y + iris_r + 5],
            fill=(80, 40, 20),
        )
        # Pupil
        draw.ellipse(
            [ex - 18, eye_y - 18, ex + 18, eye_y + 22],
            fill=(15, 5, 5),
        )
        # Sparkle highlights
        draw.ellipse([ex - 22, eye_y - 28, ex - 8, eye_y - 14], fill="white")
        draw.ellipse([ex + 5, eye_y - 10, ex + 14, eye_y - 1], fill="white")

    # ── Eyelashes (top) ──
    for ex in [cx - eye_spacing, cx + eye_spacing]:
        draw.line([(ex - eye_w + 5, eye_y - eye_h), (ex - eye_w - 5, eye_y - eye_h - 12)], fill=(30, 15, 10), width=4)
        draw.line([(ex + eye_w - 5, eye_y - eye_h), (ex + eye_w + 5, eye_y - eye_h - 12)], fill=(30, 15, 10), width=4)

    # ── Blush (pink circles under eyes) ──
    blush_y = eye_y + 40
    for bx in [cx - 80, cx + 80]:
        draw.ellipse([bx - 28, blush_y - 15, bx + 28, blush_y + 15], fill=(255, 150, 170))

    # ── Nose (tiny dot) ──
    draw.ellipse([cx - 6, eye_y + 35, cx + 6, eye_y + 47], fill=(255, 160, 130))

    # ── MOUTH (cute smile) ──
    mouth_y = eye_y + 60
    draw.arc(
        [cx - 20, mouth_y - 5, cx + 20, mouth_y + 25],
        start=0, end=180, fill=(220, 80, 60), width=5,
    )

    # ── HEADPHONES (bold coral, iconic) ──
    hp_color = (255, 75, 105)
    hp_top = cy - 180
    # Headband
    draw.arc(
        [cx - 130, hp_top, cx + 130, hp_top + 80],
        start=0, end=360, fill=hp_color, width=14,
    )
    # Ear cups
    draw.ellipse([cx - 145, hp_top + 15, cx - 115, hp_top + 55], fill=hp_color)
    draw.ellipse([cx + 115, hp_top + 15, cx + 145, hp_top + 55], fill=hp_color)
    # Ear cup highlights
    draw.ellipse([cx - 138, hp_top + 22, cx - 122, hp_top + 38], fill=(255, 130, 150))
    draw.ellipse([cx + 122, hp_top + 22, cx + 138, hp_top + 38], fill=(255, 130, 150))

    # ── TINY MIC (in front of character, floating) ──
    mic_x, mic_y = cx + 110, cy - 10
    draw.rounded_rectangle(
        [mic_x - 8, mic_y - 10, mic_x + 8, mic_y + 25],
        radius=4, fill=(60, 60, 70),
    )
    draw.ellipse([mic_x - 10, mic_y - 35, mic_x + 10, mic_y - 5], fill=(100, 100, 120))
    draw.ellipse([mic_x - 6, mic_y - 30, mic_x + 6, mic_y - 10], fill=(140, 140, 160))

    # ═══════════════════════════════════════════════
    # 📰 NEWSPAPER prop (bottom left, cute)
    # ═══════════════════════════════════════════════
    paper_x, paper_y = cx - 280, cy + 90
    draw.rounded_rectangle(
        [paper_x, paper_y, paper_x + 180, paper_y + 120],
        radius=8, fill="white",
    )
    draw.rounded_rectangle(
        [paper_x, paper_y, paper_x + 180, paper_y + 120],
        radius=8, outline=(200, 180, 170), width=3,
    )
    # Newspaper headline lines
    for i, (lw, lc) in enumerate([(140, (40, 30, 30)), (120, (80, 70, 70)), (100, (120, 110, 110)), (80, (150, 140, 140))]):
        ly = paper_y + 25 + i * 22
        draw.rectangle([paper_x + 20, ly, paper_x + 20 + lw, ly + 8], fill=lc)
    # Fold line
    draw.line(
        [(paper_x + 90, paper_y), (paper_x + 90, paper_y + 120)],
        fill=(220, 210, 200), width=2,
    )

    # ═══════════════════════════════════════════════
    # ✨ BOLD TEXT — minimal, huge, readable
    # ═══════════════════════════════════════════════
    try:
        huge_font = load_font(EN_FONT, 110, index=2)  # Helvetica Neue Bold
    except Exception:
        huge_font = ImageFont.load_default()
    try:
        tag_font = load_font(EN_FONT, 32, index=0)
    except Exception:
        tag_font = huge_font

    # Title: big, bold, white with strong shadow
    t1 = "DAILY"
    tw1 = draw.textlength(t1, font=huge_font)
    x1 = (SIZE - tw1) / 2
    # Thick outline
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-2, 0), (2, 0)]:
        draw.text((x1 + dx, 880 + dy), t1, fill="#1a0525", font=huge_font)
    draw.text((x1, 880), t1, fill="#ffffff", font=huge_font)

    t2 = "NEWS"
    tw2 = draw.textlength(t2, font=huge_font)
    x2 = (SIZE - tw2) / 2
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-2, 0), (2, 0)]:
        draw.text((x2 + dx, 1000 + dy), t2, fill="#1a0525", font=huge_font)
    draw.text((x2, 1000), t2, fill=(255, 200, 60), font=huge_font)

    # Small credit line
    credit = "by Rinちゃん⚡ · Every Morning 7am SGT"
    cw = draw.textlength(credit, font=tag_font)
    draw.text(((SIZE - cw) / 2, 1130), credit, fill=(200, 180, 190), font=tag_font)

    # Bottom accent bar
    draw.rectangle([300, 1190, 1100, 1196], fill=(255, 105, 120))

    # Tiny source line
    src = "📡 BBC · Reuters · AP · Straits Times"
    sw = draw.textlength(src, font=tag_font)
    draw.text(((SIZE - sw) / 2, 1220), src, fill=(140, 120, 135), font=tag_font)

    path = os.path.join(OUT_DIR, "cover-en.jpg")
    img.save(path, "JPEG", quality=92)
    # Save timestamped copy for cache busting
    ts_path = os.path.join(OUT_DIR, f"cover-en-{int(os.path.getmtime(path))}.jpg")
    shutil.copy2(path, ts_path)
    print(f"✅ EN cover: {path} ({os.path.getsize(path)/1024:.0f} KB) + {os.path.basename(ts_path)}")
    return path


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_jp_cover()
    make_en_cover()
    print("Done! Both covers generated.")
