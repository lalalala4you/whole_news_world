#!/bin/bash
# Update podcast RSS feeds, push to GitHub
set -e
cd "$(dirname "$0")"

echo "📻 Generating RSS feeds..."
# DEFAULT_FEED_URL is set in generate_rss.py — just run it
python3 generate_rss.py en ja

echo "📤 Pushing to GitHub..."
git add podcast-en.xml podcast-ja.xml
git commit -m "📰 Update daily news feeds" || echo "(no changes to commit)"
git push origin main

echo "✅ Done!"
echo "🔗 Live at: https://cdn.statically.io/gh/lalalala4you/whole_news_world/main/podcast-en.xml"
