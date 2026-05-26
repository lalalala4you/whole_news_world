#!/usr/bin/env python3
"""Generate podcast RSS feed for daily news — Apple Podcasts compliant."""
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
import sys
import glob
import subprocess
import json

# Try to import config, fall back to placeholder
try:
    from config import BASE_URL
except ImportError:
    BASE_URL = "https://YOUR_USERNAME.github.io/rin-daily-news"

NEWS_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(NEWS_DIR, "audio")

PODCAST_AUTHOR = "Rinちゃん"
PODCAST_OWNER_NAME = "Rinちゃん"
PODCAST_OWNER_EMAIL = "rin@daily-news.local"


def get_audio_duration(filepath):
    """Get audio duration in HH:MM:SS format using macOS afinfo."""
    try:
        result = subprocess.run(
            ['afinfo', filepath],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            if 'duration' in line:
                # "estimated duration: 322.729615 sec"
                secs = float(line.strip().split()[-2])
                h = int(secs // 3600)
                m = int((secs % 3600) // 60)
                s = int(secs % 60)
                return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        pass
    # Fallback: try ffprobe
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json',
             '-show_format', filepath],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        secs = float(data['format']['duration'])
        h = int(secs // 3600)
        m = int((secs % 3600) // 60)
        s = int(secs % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "00:05:00"


def generate_rss(lang: str):
    """Generate RSS feed for a given language."""
    fg = FeedGenerator()
    fg.load_extension("podcast")

    feed_url = f"{BASE_URL}/podcast-{lang}.xml"

    if lang == "en":
        title = "Rinちゃん's Daily News Brief"
        description = (
            "Top 5 global news stories every morning, curated by Rinちゃん. "
            "Politics, tech, economy, and more from Singapore, US, China, EU, Japan."
        )
        summary = description
    else:
        title = "Rinちゃんの今日のニュース"
        description = (
            "毎朝お届けする世界の重要ニューストップ5。"
            "政治、テクノロジー、経済など、シンガポール・米国・中国・EU・日本から厳選。"
        )
        summary = description

    # ── Required Apple Podcasts channel-level tags ──
    fg.title(title)
    fg.description(description)
    fg.language(lang)
    fg.podcast.itunes_author(PODCAST_AUTHOR)
    fg.podcast.itunes_summary(summary)
    fg.podcast.itunes_owner(PODCAST_OWNER_NAME, PODCAST_OWNER_EMAIL)
    fg.podcast.itunes_explicit("no")
    fg.podcast.itunes_type("episodic")
    fg.podcast.itunes_category("News", "Daily News")

    # Links: set atom:link FIRST, then <link> (feedgen order matters!)
    fg.link(href=feed_url, rel="self", type="application/rss+xml")  # <atom:link>
    fg.link(href=BASE_URL)  # <link> to website

    # Cover art (1400×1400 JPG)
    cover_url = f"{BASE_URL}/audio/cover-{lang}.jpg"
    fg.image(url=cover_url, title=title, link=BASE_URL)
    fg.podcast.itunes_image(cover_url)

    # ── Episodes ──
    pattern = os.path.join(AUDIO_DIR, f"daily-news-{lang}-*.m4a")
    audio_files = sorted(glob.glob(pattern), reverse=True)
    archive = os.path.join(NEWS_DIR, "archive")

    date_pairs = []
    for af in audio_files[:14]:
        date_str = af.split(f"daily-news-{lang}-")[-1].replace(".m4a", "")
        txt = os.path.join(archive, f"daily-news-{lang}-{date_str}.md")
        date_pairs.append((date_str, af, txt if os.path.exists(txt) else None))

    for date_str, audio_path, text_path in date_pairs:
        fe = fg.add_entry()

        date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
        if lang == "ja":
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_display = date_obj.strftime("%Y年%m月%d日")

        episode_title = (
            f"News Brief - {date_display}" if lang == "en"
            else f"ニュース速報 - {date_display}"
        )
        fe.title(episode_title)

        # Episode description & summary
        if text_path:
            with open(text_path) as f:
                desc = f.read()[:4000]
            fe.description(desc)
            # First 200 chars as short summary
            short = desc[:200].rsplit(" ", 1)[0] if lang == "en" else desc[:200]
            fe.podcast.itunes_summary(short)

        # Required per-episode iTunes tags
        fe.podcast.itunes_author(PODCAST_AUTHOR)
        fe.podcast.itunes_explicit("no")
        fe.podcast.itunes_duration(get_audio_duration(audio_path))

        # Audio enclosure
        audio_filename = os.path.basename(audio_path)
        fe.enclosure(
            f"{BASE_URL}/audio/{audio_filename}",
            str(os.path.getsize(audio_path)),
            "audio/mp4"
        )

        pub = datetime.strptime(date_str, "%Y-%m-%d").strftime(
            "%a, %d %b %Y 07:00:00 +0800"
        )
        fe.pubDate(pub)
        fe.guid(f"rin-daily-news-{lang}-{date_str}", permalink=False)

    # Write RSS XML
    rss_path = os.path.join(NEWS_DIR, f"podcast-{lang}.xml")
    fg.rss_file(rss_path)
    episode_count = len(date_pairs)
    print(f"✅ RSS feed: {rss_path} ({episode_count} episodes)")


if __name__ == "__main__":
    langs = sys.argv[1:] if len(sys.argv) > 1 else ["en", "ja"]
    for lang in langs:
        generate_rss(lang)
