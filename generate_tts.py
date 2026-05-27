#!/usr/bin/env python3
"""Generate TTS audio using Microsoft Edge neural voices (free, high quality).

Uses edge-tts for natural intonation, pacing, and breathing.
Voices: Christopher (EN news), Nanami (JA)
"""
import subprocess
import sys
import os
import re

VOICES = {
    "en": "en-US-AriaNeural",         # Female, News anchor voice
    "ja": "ja-JP-NanamiNeural",         # Female, natural Japanese
}

# Speech rate adjustment (-50% to +100%, 0 = default)
RATE = "-5%"  # Slightly slower for podcast feel


def preprocess_for_tts(text: str, lang: str) -> str:
    """Convert markdown to clean text with natural SSML-like formatting.
    Edge-TTS auto-detects sentence boundaries and adds natural pauses."""
    
    # Strip markdown formatting symbols that TTS might read literally
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold → plain
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links → text only
    
    # Remove markdown header markers, add period for TTS pause
    text = re.sub(r'^#{1,3}\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove emoji that TTS might stumble on
    text = re.sub(r'[🌍🏷️🎙️📰🇺🇸🇬🇧🇯🇵🇨🇳🇪🇺🇸🇬🇮🇳🇦🇺🇰🇷🇫🇷🇩🇪]', '', text)
    
    # Add explicit pauses where we want them (edge-tts supports SSML)
    # But edge-tts CLI doesn't support inline SSML easily
    # Instead, use sentence breaks and paragraph spacing
    
    # Ensure proper spacing between sections
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
    
    # Clean up stray characters
    text = text.replace('|', ',')  # Replace pipe with comma
    
    return text.strip()


def generate_tts(text: str, output_dir: str, lang: str, date_str: str) -> str:
    """Generate M4A audio using edge-tts. Returns path to M4A file."""
    voice = VOICES.get(lang, VOICES["en"])
    base_name = f"daily-news-{lang}-{date_str}"
    m4a_path = os.path.join(output_dir, f"{base_name}.m4a")
    
    # Preprocess text for TTS
    processed = preprocess_for_tts(text, lang)
    
    print(f"🎙️  Generating {lang.upper()} TTS with {voice}...")
    result = subprocess.run(
        [
            "edge-tts",
            "--voice", voice,
            f"--rate={RATE}",
            "--text", processed,
            "--write-media", m4a_path,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    
    if result.returncode != 0:
        print(f"❌ edge-tts failed: {result.stderr}")
        raise RuntimeError(f"edge-tts failed: {result.stderr}")
    
    size_kb = os.path.getsize(m4a_path) / 1024
    print(f"✅ {base_name}.m4a ({size_kb:.0f} KB)")
    return m4a_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: generate_tts.py <text_file> <output_dir> <lang> <date_str>")
        sys.exit(1)
    
    text_file = sys.argv[1]
    output_dir = sys.argv[2]
    lang = sys.argv[3]
    date_str = sys.argv[4]
    
    with open(text_file, "r") as f:
        text = f.read()
    
    generate_tts(text, output_dir, lang, date_str)
