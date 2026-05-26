#!/usr/bin/env python3
"""Generate podcast cover art — vibrant EN + proper JP."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SIZE = 1400
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# Fonts
JP_FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
JP_FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
NOTO_JP = "/tmp/NotoSansJP.ttf"
EN_FONT = "/System/Library/Fonts/HelveticaNeue.ttc"

def get_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except:
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

def make_jp_cover():
    """Japanese cover with proper CJK font rendering."""
    img = Image.new("RGB", (SIZE, SIZE), "#0d0d1f")
    draw = ImageDraw.Draw(img)
    
    # Background gradient
    for y in range(SIZE):
        r = int(13 + (y / SIZE) * 18)
        g = int(13 + (y / SIZE) * 22)
        b = int(31 + (y / SIZE) * 35)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b))
    
    # Glowing accent circle (top-right)
    for r in range(350, 0, -1):
        alpha = int(25 * (1 - r/350))
        draw.ellipse(
            [SIZE-200 - r, -100 - r//2, SIZE-200 + r, -100 + r],
            fill=(220, 60, 40),
            outline=None
        )
    
    # Accent lines
    draw.rectangle([80, 500, 1320, 504], fill=(220, 80, 60))
    draw.rectangle([80, 860, 1320, 864], fill=(220, 80, 60))
    
    # Try Hiragino first, fall back to Noto
    try:
        title_font = ImageFont.truetype(JP_FONT, 68, index=0)
    except:
        try:
            title_font = ImageFont.truetype(NOTO_JP, 68)
        except:
            title_font = ImageFont.load_default()
    
    try:
        sub_font = ImageFont.truetype(JP_FONT, 32, index=0)
    except:
        try:
            sub_font = ImageFont.truetype(NOTO_JP, 32)
        except:
            sub_font = title_font
    
    try:
        tag_font = ImageFont.truetype(JP_FONT, 26, index=0)
    except:
        tag_font = sub_font
    
    # Title
    title = "Rinちゃんの今日のニュース"
    tw = draw.textlength(title, font=title_font)
    draw.text(((SIZE - tw)/2, 580), title, fill="#ffffff", font=title_font)
    
    # Subtitle
    subtitle = "毎朝お届け・世界の重要ニュース トップ5"
    sw = draw.textlength(subtitle, font=sub_font)
    draw.text(((SIZE - sw)/2, 680), subtitle, fill=(200, 180, 180), font=sub_font)
    
    # Source line
    sources = "📡 BBC · Reuters · AP · Straits Times"
    sw2 = draw.textlength(sources, font=tag_font)
    draw.text(((SIZE - sw2)/2, 750), sources, fill=(140, 130, 140), font=tag_font)
    
    # Bottom tag
    tag = "✦ AIキュレーション ✦ 毎朝7時配信 ✦"
    tw3 = draw.textlength(tag, font=tag_font)
    draw.text(((SIZE - tw3)/2, SIZE - 80), tag, fill=(100, 90, 100), font=tag_font)
    
    path = os.path.join(OUT_DIR, "cover-ja.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"✅ JP cover: {path} ({os.path.getsize(path)/1024:.0f} KB)")
    return path


def make_en_cover():
    """Energetic English cover with Duolingo-style mascot and shapes."""
    img = Image.new("RGB", (SIZE, SIZE), "#1a0533")
    draw = ImageDraw.Draw(img)
    
    # Vibrant gradient background (purple → magenta → orange)
    for y in range(SIZE):
        ratio = y / SIZE
        if ratio < 0.5:
            r = int(26 + ratio * 2 * 220)
            g = int(5 + ratio * 2 * 30)
            b = int(51 + ratio * 2 * 100)
        else:
            r = int(246 - (ratio-0.5) * 2 * 40)
            g = int(35 + (ratio-0.5) * 2 * 100)
            b = int(151 - (ratio-0.5) * 2 * 100)
        draw.line([(0, y), (SIZE, y)], fill=(min(r,255), min(g,255), min(b,255)))
    
    # Large decorative shapes
    # Circle top-left
    draw.ellipse([-80, -80, 350, 350], fill=(255, 200, 50, 180), outline=None)
    # Smaller circle top-right  
    draw.ellipse([SIZE-250, 50, SIZE+50, 350], fill=(255, 100, 150, 150), outline=None)
    
    # Triangle accent (bottom left)
    tri = [(50, SIZE-200), (250, SIZE-350), (250, SIZE-50)]
    draw.polygon(tri, fill=(80, 220, 255))
    
    # Small floating dots/circles
    for pos, color in [
        ((300, 200), (255, 255, 100)),
        ((1050, 150), (100, 255, 200)),
        ((200, 400), (255, 150, 200)),
        ((1100, 350), (255, 200, 100)),
        ((1200, 500), (150, 200, 255)),
        ((180, 650), (255, 255, 150)),
    ]:
        draw.ellipse([pos[0]-15, pos[1]-15, pos[0]+15, pos[1]+15], fill=color)
    
    # === DUOLINGO-STYLE OWL MASCOT (center-ish, smaller) ===
    owl_cx, owl_cy = 700, 350
    # Body (green rounded shape)
    draw.ellipse([owl_cx-55, owl_cy-30, owl_cx+55, owl_cy+75], fill=(88, 204, 2))
    # Belly (lighter green)
    draw.ellipse([owl_cx-38, owl_cy+5, owl_cx+38, owl_cy+70], fill=(168, 255, 88))
    # Head (bigger circle on top)
    draw.ellipse([owl_cx-50, owl_cy-80, owl_cx+50, owl_cy+20], fill=(88, 204, 2))
    # Eyes (big white circles)
    draw.ellipse([owl_cx-32, owl_cy-60, owl_cx-2, owl_cy-30], fill="white")
    draw.ellipse([owl_cx+2, owl_cy-60, owl_cx+32, owl_cy-30], fill="white")
    # Pupils (big dark circles, slightly cross-eyed for cute)
    draw.ellipse([owl_cx-20, owl_cy-55, owl_cx-8, owl_cy-35], fill="#1a0533")
    draw.ellipse([owl_cx+8, owl_cy-55, owl_cx+20, owl_cy-35], fill="#1a0533")
    # Eye highlights
    draw.ellipse([owl_cx-17, owl_cy-52, owl_cx-12, owl_cy-47], fill="white")
    draw.ellipse([owl_cx+12, owl_cy-52, owl_cx+17, owl_cy-47], fill="white")
    # Beak (orange triangle)
    beak = [(owl_cx-10, owl_cy-32), (owl_cx+10, owl_cy-32), (owl_cx, owl_cy-15)]
    draw.polygon(beak, fill=(255, 140, 50))
    # Blush circles
    draw.ellipse([owl_cx-45, owl_cy-35, owl_cx-30, owl_cy-22], fill=(255, 130, 150, 120))
    draw.ellipse([owl_cx+30, owl_cy-35, owl_cx+45, owl_cy-22], fill=(255, 130, 150, 120))
    # Tiny wings
    draw.ellipse([owl_cx-70, owl_cy-10, owl_cx-45, owl_cy+30], fill=(70, 180, 0))
    draw.ellipse([owl_cx+45, owl_cy-10, owl_cx+70, owl_cy+30], fill=(70, 180, 0))
    # Headphones on the owl!
    draw.arc([owl_cx-55, owl_cy-95, owl_cx+55, owl_cy-50], start=190, end=350, fill=(255, 80, 120), width=8)
    headphone_l = (owl_cx-55, owl_cy-70, owl_cx-40, owl_cy-55)
    headphone_r = (owl_cx+40, owl_cy-70, owl_cx+55, owl_cy-55)
    draw.ellipse(headphone_l, fill=(255, 80, 120))
    draw.ellipse(headphone_r, fill=(255, 80, 120))
    
    # === TEXT ===
    try:
        title_font = ImageFont.truetype(EN_FONT, 80, index=2)  # Helvetica Neue Bold
    except:
        title_font = ImageFont.load_default()
    try:
        sub_font = ImageFont.truetype(EN_FONT, 34, index=0)
    except:
        sub_font = title_font
    try:
        tag_font = ImageFont.truetype(EN_FONT, 26, index=0)
    except:
        tag_font = sub_font
    
    # Title with shadow effect
    title = "Rin-chan's"
    tw = draw.textlength(title, font=title_font)
    x = (SIZE - tw) / 2
    # Shadow
    draw.text((x+4, 484), title, fill="rgba(0,0,0,80)", font=title_font)
    draw.text((x, 480), title, fill="#ffffff", font=title_font)
    
    title2 = "Daily News"
    tw2 = draw.textlength(title2, font=title_font)
    x2 = (SIZE - tw2) / 2
    draw.text((x2+4, 574), title2, fill="rgba(0,0,0,80)", font=title_font)
    draw.text((x2, 570), title2, fill=(255, 230, 80), font=title_font)
    
    # Subtitle
    sub = "Top 5 Global Stories · Every Morning · SG US CN EU JP"
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((SIZE - sw)/2, 670), sub, fill=(255, 255, 255, 200), font=sub_font)
    
    # Bottom line with accent
    draw.rectangle([150, 730, 1250, 734], fill=(255, 200, 50))
    
    # Source tag
    tag = "📡 BBC · Reuters · AP · Straits Times  ✦  Daily 7am SGT  ✦  AI-Curated by Rinちゃん"
    tw4 = draw.textlength(tag, font=tag_font)
    draw.text(((SIZE - tw4)/2, SIZE - 70), tag, fill=(220, 210, 230), font=tag_font)
    
    path = os.path.join(OUT_DIR, "cover-en.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"✅ EN cover: {path} ({os.path.getsize(path)/1024:.0f} KB)")
    return path


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_jp_cover()
    make_en_cover()
    print("Done! Both covers generated.")
