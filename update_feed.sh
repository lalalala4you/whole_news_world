#!/bin/bash
# Update podcast RSS feeds, push to GitHub, and purge jsDelivr cache
set -e
cd "$(dirname "$0")"

# jsDelivr URLs for the podcast feeds
EN_FEED_URL="https://cdn.statically.io/gh/lalalala4you/whole_news_world/main/podcast-en.xml"
JA_FEED_URL="https://cdn.statically.io/gh/lalalala4you/whole_news_world/main/podcast-ja.xml"

echo "📻 Generating RSS feeds..."
python3 -c "
import sys; sys.path.insert(0, '.')
import generate_rss as gr
gr.DEFAULT_FEED_URL = '${EN_FEED_URL}'
gr.generate_rss('en')
gr.DEFAULT_FEED_URL = '${JA_FEED_URL}'
gr.generate_rss('ja')
"

echo "📤 Pushing to GitHub..."
git add podcast-en.xml podcast-ja.xml
git commit -m "📰 Update daily news feeds" || echo "(no changes to commit)"
git push origin main

echo "🧹 Purging jsDelivr cache..."
curl -s "https://purge.jsdelivr.net/gh/lalalala4you/whole_news_world@main/podcast-en.xml" > /dev/null
curl -s "https://purge.jsdelivr.net/gh/lalalala4you/whole_news_world@main/podcast-ja.xml" > /dev/null
echo "✅ Done!"
