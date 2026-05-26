#!/usr/bin/env python3
"""Generate podcast RSS feed for daily news."""
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
import sys
import glob

# Try to import config, fall back to placeholder
try:
    from config import BASE_URL
except ImportError:
    BASE_URL = "https://YOUR_USERNAME.github.io/rin-daily-news"
NEWS_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(NEWS_DIR, "audio")

def generate_rss(lang: str):
    """Generate RSS feed for a given language."""
    fg = FeedGenerator()
    fg.load_extension("podcast")
    
    if lang == "en":
        title = "Rinちゃん's Daily News Brief"
        description = "Top 5 global news stories every morning, curated by Rinちゃん. Politics, tech, economy, and more from Singapore, US, China, EU, Japan."
    else:
        title = "Rinちゃんの今日のニュース"
        description = "毎朝お届けする世界の重要ニューストップ5。政治、テクノロジー、経済など、シンガポール・米国・中国・EU・日本から厳選。"
    
    fg.title(title)
    fg.description(description)
    fg.link(href=BASE_URL, rel="self")
    fg.language(lang)
    fg.podcast.itunes_category("News", "Daily News")
    
    # Cover art (1400x1400 JPG for Apple Podcasts)
    cover_url = f"{BASE_URL}/audio/cover-{lang}.jpg"
    fg.image(cover_url)
    fg.podcast.itunes_image(cover_url)
    
    # Find all audio files for this language, sorted by date (newest first)
    pattern = os.path.join(AUDIO_DIR, f"daily-news-{lang}-*.m4a")
    audio_files = sorted(glob.glob(pattern), reverse=True)
    
    # Also look for corresponding text summaries
    archive = os.path.join(NEWS_DIR, "archive")
    text_files = sorted(glob.glob(os.path.join(archive, f"daily-news-{lang}-*.md")), reverse=True)
    
    # Match audio with text files, use last 14 days
    date_pairs = []
    for af in audio_files[:14]:
        date_str = af.split(f"daily-news-{lang}-")[-1].replace(".m4a", "")
        # Find matching text
        txt = os.path.join(archive, f"daily-news-{lang}-{date_str}.md")
        if os.path.exists(txt):
            date_pairs.append((date_str, af, txt))
        else:
            date_pairs.append((date_str, af, None))
    
    for date_str, audio_path, text_path in date_pairs:
        fe = fg.add_entry()
        date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
        fe.title(f"News Brief - {date_display}")
        
        if text_path:
            with open(text_path) as f:
                description_text = f.read()[:2000]
            fe.description(description_text)
        
        # Podcast requires an audio enclosure
        audio_filename = os.path.basename(audio_path)
        fe.enclosure(f"{BASE_URL}/audio/{audio_filename}", 
                     str(os.path.getsize(audio_path)), 
                     "audio/mp4")
        
        fe.pubDate(datetime.strptime(date_str, "%Y-%m-%d").strftime("%a, %d %b %Y 07:00:00 +0800"))
        fe.guid(f"rin-daily-news-{lang}-{date_str}", permalink=False)
    
    # Write RSS XML
    rss_path = os.path.join(NEWS_DIR, f"podcast-{lang}.xml")
    fg.rss_file(rss_path)
    print(f"✅ RSS feed generated: {rss_path} ({len(date_pairs)} episodes)")
    return rss_path

if __name__ == "__main__":
    langs = sys.argv[1:] if len(sys.argv) > 1 else ["en", "ja"]
    for lang in langs:
        generate_rss(lang)
