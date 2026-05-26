#!/usr/bin/env python3
"""Generate podcast cover art — dynamic EN + bold readable JP."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 1400
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

NOTO_JP = "/tmp/NotoSansJP.ttf"
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
    print(f"✅ JP cover: {path} ({os.path.getsize(path)/1024:.0f} KB)")
    return path


def make_en_cover():
    """Dynamic English cover — big Duolingo-style owl mascot, warm energetic colors."""
    img = Image.new("RGB", (SIZE, SIZE), "#fff5e8")
    draw = ImageDraw.Draw(img)

    # ── Warm gradient background: cream → golden → coral ──
    for y in range(SIZE):
        ratio = y / SIZE
        if ratio < 0.35:
            r = int(255 - ratio / 0.35 * 15)
            g = int(245 - ratio / 0.35 * 40)
            b = int(232 - ratio / 0.35 * 50)
        elif ratio < 0.7:
            r = int(240 - (ratio - 0.35) / 0.35 * 30)
            g = int(205 - (ratio - 0.35) / 0.35 * 40)
            b = int(182 - (ratio - 0.35) / 0.35 * 30)
        else:
            r = int(210 - (ratio - 0.7) / 0.3 * 40)
            g = int(165 - (ratio - 0.7) / 0.3 * 30)
            b = int(152 - (ratio - 0.7) / 0.3 * 20)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))

    # ── Sunburst rays from top-right ──
    sun_cx, sun_cy = SIZE - 100, -50
    for angle in range(0, 180, 12):
        rad = math.radians(angle)
        end_x = sun_cx + math.cos(rad) * 1600
        end_y = sun_cy + math.sin(rad) * 1600
        for t in [0.1, 0.3, 0.6]:
            mid_x = sun_cx + (end_x - sun_cx) * t
            mid_y = sun_cy + (end_y - sun_cy) * t
            draw.ellipse(
                [mid_x - 3, mid_y - 3, mid_x + 3, mid_y + 3],
                fill=(255, 220, 100) if t > 0.3 else (255, 240, 180),
            )
    # Sun disc
    draw.ellipse([sun_cx - 120, sun_cy - 120, sun_cx + 120, sun_cy + 120], fill=(255, 210, 80))

    # ── Floating accent shapes ──
    shapes = [
        ("circle", 80, 300, 55, (255, 160, 100, 180)),
        ("circle", 150, 750, 70, (255, 180, 120, 150)),
        ("circle", 1250, 250, 45, (255, 140, 80, 170)),
        ("circle", 1200, 850, 60, (255, 170, 110, 160)),
        ("circle", 300, 1050, 35, (255, 190, 140, 140)),
        ("circle", 1100, 600, 40, (255, 150, 90, 140)),
    ]
    for shape, cx, cy, r, color in shapes:
        if shape == "circle":
            # Semi-transparent glow
            draw.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8],
                         fill=(color[0], color[1], color[2]), outline=None)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(min(color[0]+40, 255), min(color[1]+40, 255), min(color[2]+40, 255)))

    # ── Sparkle/stars ──
    for sx, sy, ss in [
        (200, 150, 20), (450, 100, 14), (700, 80, 18),
        (950, 120, 12), (1150, 160, 22), (100, 500, 16),
        (1280, 480, 14), (350, 1200, 18), (1000, 1100, 20),
    ]:
        # 4-point star
        pts = [
            (sx, sy - ss), (sx + ss//3, sy - ss//3), (sx + ss, sy),
            (sx + ss//3, sy + ss//3), (sx, sy + ss), (sx - ss//3, sy + ss//3),
            (sx - ss, sy), (sx - ss//3, sy - ss//3),
        ]
        draw.polygon(pts, fill=(255, 230, 120))

    # ═══════════════════════════════════════════
    # 🦉 BIG DUOLINGO-STYLE OWL MASCOT (center)
    # ═══════════════════════════════════════════
    owl_cx, owl_cy = 700, 340

    # Shadow under owl
    draw.ellipse([owl_cx - 70, owl_cy + 70, owl_cx + 70, owl_cy + 90],
                 fill=(0, 0, 0, 30))

    # Body (big rounded green)
    body_x, body_y, body_w, body_h = owl_cx - 70, owl_cy - 20, 140, 110
    draw.rounded_rectangle(
        [body_x, body_y, body_x + body_w, body_y + body_h],
        radius=55, fill=(88, 204, 2)
    )

    # Belly (lighter green, rounded)
    belly_x, belly_y = owl_cx - 48, owl_cy + 10
    draw.rounded_rectangle(
        [belly_x, belly_y, belly_x + 96, belly_y + 75],
        radius=35, fill=(168, 255, 88)
    )

    # Head
    draw.ellipse([owl_cx - 68, owl_cy - 105, owl_cx + 68, owl_cy + 25],
                 fill=(88, 204, 2))

    # Ears (feather tufts)
    ear_l = [(owl_cx - 55, owl_cy - 100), (owl_cx - 75, owl_cy - 155), (owl_cx - 35, owl_cy - 110)]
    ear_r = [(owl_cx + 55, owl_cy - 100), (owl_cx + 75, owl_cy - 155), (owl_cx + 35, owl_cy - 110)]
    draw.polygon(ear_l, fill=(70, 180, 0))
    draw.polygon(ear_r, fill=(70, 180, 0))

    # Eyes — big white circles
    eye_y = owl_cy - 68
    draw.ellipse([owl_cx - 42, eye_y - 28, owl_cx - 2, eye_y + 8], fill="white")
    draw.ellipse([owl_cx + 2, eye_y - 28, owl_cx + 42, eye_y + 8], fill="white")
    # Eye outline
    draw.ellipse([owl_cx - 42, eye_y - 28, owl_cx - 2, eye_y + 8], outline=(50, 150, 0), width=3)
    draw.ellipse([owl_cx + 2, eye_y - 28, owl_cx + 42, eye_y + 8], outline=(50, 150, 0), width=3)

    # Pupils — big, slightly contrasting
    draw.ellipse([owl_cx - 28, eye_y - 24, owl_cx - 12, eye_y - 4], fill="#1a0533")
    draw.ellipse([owl_cx + 12, eye_y - 24, owl_cx + 28, eye_y - 4], fill="#1a0533")
    # Pupil sparkle
    draw.ellipse([owl_cx - 24, eye_y - 21, owl_cx - 18, eye_y - 15], fill="white")
    draw.ellipse([owl_cx + 18, eye_y - 21, owl_cx + 24, eye_y - 15], fill="white")

    # Beak
    beak = [(owl_cx - 14, eye_y - 2), (owl_cx + 14, eye_y - 2), (owl_cx, eye_y + 18)]
    draw.polygon(beak, fill=(255, 160, 50))
    draw.polygon(beak, outline=(230, 130, 30), width=2)

    # Blush — soft pink
    draw.ellipse([owl_cx - 55, eye_y - 12, owl_cx - 38, eye_y + 5], fill=(255, 140, 160, 140))
    draw.ellipse([owl_cx + 38, eye_y - 12, owl_cx + 55, eye_y + 5], fill=(255, 140, 160, 140))

    # Eyebrows — expressive!
    draw.line([(owl_cx - 40, eye_y - 38), (owl_cx - 8, eye_y - 44)], fill=(50, 150, 0), width=6)
    draw.line([(owl_cx + 8, eye_y - 44), (owl_cx + 40, eye_y - 38)], fill=(50, 150, 0), width=6)

    # Wings
    draw.ellipse([owl_cx - 95, owl_cy - 15, owl_cx - 60, owl_cy + 45], fill=(70, 180, 0))
    draw.ellipse([owl_cx + 60, owl_cy - 15, owl_cx + 95, owl_cy + 45], fill=(70, 180, 0))

    # Feet
    for fx in [owl_cx - 25, owl_cx + 25]:
        draw.ellipse([fx - 15, owl_cy + 80, fx + 15, owl_cy + 95], fill=(255, 170, 70))
        # Toes
        for tx in [-8, 0, 8]:
            draw.ellipse([fx + tx - 6, owl_cy + 88, fx + tx + 6, owl_cy + 100], fill=(255, 180, 80))

    # 🎤 Microphone (owl is holding it!)
    mic_x, mic_y = owl_cx + 55, owl_cy + 10
    draw.rounded_rectangle([mic_x, mic_y - 25, mic_x + 12, mic_y + 30], radius=5, fill=(80, 80, 90))
    draw.ellipse([mic_x - 4, mic_y - 45, mic_x + 16, mic_y - 15], fill=(60, 60, 70))
    draw.ellipse([mic_x - 2, mic_y - 42, mic_x + 14, mic_y - 18], fill=(90, 90, 100))
    # Mic mesh dots
    for dy in range(-38, -20, 4):
        draw.line([(mic_x + 1, mic_y + dy), (mic_x + 11, mic_y + dy)], fill=(50, 50, 60), width=2)

    # 🎧 Headphones on owl
    headphone_y = owl_cy - 115
    draw.arc([owl_cx - 70, headphone_y, owl_cx + 70, headphone_y + 50],
             0, 360, fill=(255, 70, 110), width=10)
    draw.ellipse([owl_cx - 72, headphone_y + 5, owl_cx - 52, headphone_y + 30], fill=(255, 70, 110))
    draw.ellipse([owl_cx + 52, headphone_y + 5, owl_cx + 72, headphone_y + 30], fill=(255, 70, 110))

    # ── CHART BARS (off to the side — news/market theme) ──
    bar_base = 800
    bar_data = [
        (70, (255, 100, 60)), (55, (255, 150, 80)),
        (90, (255, 200, 50)), (50, (100, 200, 255)),
        (65, (150, 120, 255)),
    ]
    for i, (height, color) in enumerate(bar_data):
        bx = bar_base + i * 30
        by = bar_base - height
        draw.rounded_rectangle([bx, by, bx + 20, bar_base], radius=6, fill=color)

    # ── GLOBE icon (bottom-left, subtle) ──
    globe_cx, globe_cy = 120, 820
    for r in range(60, 0, -1):
        draw.ellipse(
            [globe_cx - r, globe_cy - r, globe_cx + r, globe_cy + r],
            fill=(80, 180, 240) if r > 40 else (100, 200, 255),
        )
    # Grid lines on globe
    draw.ellipse([globe_cx - 30, globe_cy - 60, globe_cx + 30, globe_cy + 60],
                 outline=(40, 150, 210), width=2)
    draw.line([(globe_cx - 60, globe_cy), (globe_cx + 60, globe_cy)], fill=(40, 150, 210), width=2)

    # ── TEXT ──
    try:
        title_font = load_font(EN_FONT, 82, index=2)  # Helvetica Neue Bold
    except Exception:
        title_font = ImageFont.load_default()
    try:
        sub_font = load_font(EN_FONT, 32, index=0)
    except Exception:
        sub_font = title_font
    try:
        tag_font = load_font(EN_FONT, 26, index=0)
    except Exception:
        tag_font = sub_font

    # Title block with shadow
    t1 = "Rin-chan's"
    tw = draw.textlength(t1, font=title_font)
    x = (SIZE - tw) / 2
    draw.text((x + 4, 574), t1, fill=(0, 0, 0, 80), font=title_font)
    draw.text((x, 570), t1, fill="#ffffff", font=title_font)

    t2 = "Daily News"
    tw2 = draw.textlength(t2, font=title_font)
    x2 = (SIZE - tw2) / 2
    draw.text((x2 + 4, 664), t2, fill=(0, 0, 0, 80), font=title_font)
    draw.text((x2, 660), t2, fill=(255, 225, 60), font=title_font)

    # Subtitle — curved placement feels dynamic
    sub = "✦ Top 5 Global Stories · Every Morning · 7am SGT ✦"
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((SIZE - sw) / 2, 760), sub, fill=(80, 55, 50), font=sub_font)

    # Divider line
    draw.rectangle([200, 830, 1200, 834], fill=(255, 180, 80))

    # Region tags
    regions = "🇸🇬 Singapore  ·  🇺🇸 United States  ·  🇨🇳 China  ·  🇪🇺 Europe  ·  🇯🇵 Japan"
    rw = draw.textlength(regions, font=tag_font)
    draw.text(((SIZE - rw) / 2, 855), regions, fill=(100, 70, 55), font=tag_font)

    source = "📡 BBC · Reuters · AP · Straits Times  |  AI-Curated by Rinちゃん⚡"
    sw3 = draw.textlength(source, font=tag_font)
    draw.text(((SIZE - sw3) / 2, SIZE - 85), source, fill=(150, 130, 120), font=tag_font)

    path = os.path.join(OUT_DIR, "cover-en.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"✅ EN cover: {path} ({os.path.getsize(path)/1024:.0f} KB)")
    return path


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_jp_cover()
    make_en_cover()
    print("Done! Both covers generated.")
