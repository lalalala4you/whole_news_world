#!/usr/bin/env python3
"""Generate TTS audio from text using macOS `say` and convert to M4A."""
import subprocess
import sys
import os
from datetime import datetime

VOICES = {
    "en": "Samantha",   # Warm American English
    "ja": "Kyoko",      # Clear Japanese
}

def generate_tts(text: str, output_dir: str, lang: str, date_str: str) -> str:
    """Generate M4A audio from text. Returns path to M4A file."""
    voice = VOICES.get(lang, "Samantha")
    base_name = f"daily-news-{lang}-{date_str}"
    aiff_path = os.path.join(output_dir, f"{base_name}.aiff")
    m4a_path = os.path.join(output_dir, f"{base_name}.m4a")
    
    # Step 1: Generate AIFF with macOS say
    print(f"Generating {lang} TTS with voice {voice}...")
    subprocess.run(
        ["say", "-v", voice, "-o", aiff_path, text],
        check=True
    )
    
    # Step 2: Convert to M4A (AAC) - podcast standard
    print(f"Converting to M4A...")
    subprocess.run(
        ["afconvert", "-f", "m4af", "-d", "aac", aiff_path, "-o", m4a_path],
        check=True
    )
    
    # Clean up AIFF
    os.remove(aiff_path)
    
    size_kb = os.path.getsize(m4a_path) / 1024
    print(f"✅ Generated: {m4a_path} ({size_kb:.0f} KB)")
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
