#!/usr/bin/env python3
"""Send daily news audio + text to Telegram channel."""
import requests
import sys
import os
import argparse

TOKEN = "8899268721:AAF3i_WXMU2Yr22e8J2aRHc6rJATah08Wvo"
BASE_API = f"https://api.telegram.org/bot{TOKEN}"

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
            timeout=60,
        )
    return resp.json()

DEFAULT_CHAT_ID = "7712018868"  # Yilin

def get_chat_id() -> str:
    """Get chat ID from recent updates — works after user sends /start to bot."""
    resp = requests.get(f"{BASE_API}/getUpdates", timeout=10).json()
    if resp.get("ok") and resp["result"]:
        return str(resp["result"][-1]["message"]["chat"]["id"])
    return DEFAULT_CHAT_ID  # Fallback to known chat ID

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send daily news to Telegram")
    parser.add_argument("--chat-id", help="Telegram chat ID (optional, auto-detect if omitted)")
    parser.add_argument("--text", help="Path to text summary file")
    parser.add_argument("--audio", help="Path to M4A audio file")
    parser.add_argument("--lang", default="en", help="Language code (en/ja)")
    args = parser.parse_args()

    chat_id = args.chat_id or get_chat_id()
    if not chat_id:
        print("❌ No chat ID found. Please send /start to your bot first.")
        sys.exit(1)
    
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
        caption = f"🎙️ Daily News Brief — {os.path.basename(args.audio).replace('daily-news-', '').replace('.m4a', '')} ({args.lang.upper()})"
        result = send_audio(chat_id, args.audio, caption)
        if result.get("ok"):
            print(f"  ✅ Audio sent ({os.path.getsize(args.audio)/1024:.0f} KB)")
        else:
            print(f"  ⚠️ Audio send failed: {result}")
    
    print("✅ Telegram delivery complete!")
