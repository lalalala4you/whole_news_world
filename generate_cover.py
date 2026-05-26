#!/usr/bin/env python3
"""Generate podcast cover art for both EN and JA feeds."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

SIZE = 1400
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

def make_cover(title: str, subtitle: str, filename: str, accent_color=(0, 180, 216)):
    """Create a modern podcast cover image."""
    img = Image.new("RGB", (SIZE, SIZE), "#0a0a1a")
    draw = ImageDraw.Draw(img)
    
    # Background gradient (subtle)
    for y in range(SIZE):
        r = int(10 + (y / SIZE) * 15)
        g = int(10 + (y / SIZE) * 20)
        b = int(26 + (y / SIZE) * 40)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))
    
    # Decorative circle (top-left glow)
    for r in range(300, 0, -1):
        alpha = int(30 * (1 - r/300))
        draw.ellipse(
            [-100 - r//2, -100 - r//2, -100 + r, -100 + r],
            fill=(accent_color[0], accent_color[1], accent_color[2]),
            outline=None
        )
    
    # Decorative line accents
    draw.rectangle([100, 520, 1300, 522], fill=accent_color)
    draw.rectangle([100, 880, 1300, 882], fill=accent_color)
    
    # Try to find a good font
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    
    title_font = None
    sub_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                title_font = ImageFont.truetype(fp, 72)
                sub_font = ImageFont.truetype(fp, 36)
                break
            except:
                continue
    
    if title_font is None:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
    
    # Draw title (centered)
    # Split long titles into lines
    words = title.split()
    lines = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        if draw.textlength(test, font=title_font) > 1100:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    
    y_start = 580
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=title_font)
        x = (SIZE - tw) / 2
        draw.text((x, y_start + i * 90), line, fill="#ffffff", font=title_font)
    
    # Draw subtitle
    sub_y = y_start + len(lines) * 90 + 30
    sw = draw.textlength(subtitle, font=sub_font)
    draw.text(((SIZE - sw)/2, sub_y), subtitle, fill=(180, 200, 220), font=sub_font)
    
    # Small tag at bottom
    tag = "✦ curated by AI ✦ daily at 7am SGT ✦"
    try:
        tag_font = ImageFont.truetype(font_paths[0], 28)
    except:
        tag_font = sub_font
    tw = draw.textlength(tag, font=tag_font)
    draw.text(((SIZE - tw)/2, SIZE - 80), tag, fill=(100, 110, 130), font=tag_font)
    
    out_path = os.path.join(OUT_DIR, filename)
    img.save(out_path, "JPEG", quality=92)
    print(f"✅ {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)")
    return out_path

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # English cover
    make_cover(
        "Rin-chan's Daily News",
        "Top 5 Global Stories Every Morning",
        "cover-en.jpg",
        accent_color=(0, 200, 240)
    )
    
    # Japanese cover
    make_cover(
        "Rinちゃんの今日のニュース",
        "毎朝お届け・世界の重要ニュース トップ5",
        "cover-ja.jpg",
        accent_color=(240, 80, 60)
    )
    
    print("Done!")
