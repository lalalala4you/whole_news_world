#!/usr/bin/env python3
"""Send daily news audio + text to Telegram channel."""
import requests
import sys
import os
import argparse

# Load credentials from config (NOT in git — keep token private)
try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    print("❌ config.py not found or missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
    sys.exit(1)

BASE_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(chat_id: str, text: str) -> dict:
    """Send text message to Telegram chat."""
    resp = requests.post(
        f"{BASE_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )
    return resp.json()

def send_audio(chat_id: str, audio_path: str, caption: str = "") -> dict:
    """Send M4A audio file to Telegram chat."""
    with open(audio_path, "rb") as f:
        resp = requests.post(
            f"{BASE_API}/sendAudio",
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
            files={"audio": (os.path.basename(audio_path), f, "audio/mp4")},
            timeout=120,
        )
    return resp.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send daily news to Telegram")
    parser.add_argument("--chat-id", default=TELEGRAM_CHAT_ID, help="Telegram chat ID")
    parser.add_argument("--text", help="Path to text summary file")
    parser.add_argument("--audio", help="Path to MP3 audio file")
    parser.add_argument("--lang", default="en", help="Language code (en/ja)")
    args = parser.parse_args()

    chat_id = args.chat_id
    print(f"📱 Sending to Telegram chat {chat_id}...")

    # 1. Send a brief text header first
    if args.text and os.path.exists(args.text):
        with open(args.text) as f:
            summary = f.read()
        # Truncate for Telegram (4096 char limit)
        header = summary[:500] + ("…" if len(summary) > 500 else "")
        header_msg = f"🗞️ *Rinちゃん's Daily News* ({args.lang.upper()})\n\n{header}\n\n🎧 Full audio below ↓"
        result = send_message(chat_id, header_msg)
        if result.get("ok"):
            print(f"  ✅ Header sent")
        else:
            print(f"  ⚠️ Header failed: {result}")

    # 2. Send the audio file
    if args.audio and os.path.exists(args.audio):
        caption = f"🎙️ Daily News Brief — {os.path.basename(args.audio).replace('daily-news-', '').replace('.mp3', '')} ({args.lang.upper()})"
        result = send_audio(chat_id, args.audio, caption)
        if result.get("ok"):
            print(f"  ✅ Audio sent ({os.path.getsize(args.audio)/1024:.0f} KB)")
        else:
            print(f"  ⚠️ Audio send failed: {result}")

    print("✅ Telegram delivery complete!")
