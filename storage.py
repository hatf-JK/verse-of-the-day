#!/usr/bin/env python3
"""Local persistence module for saving and viewing favorite Quran verses."""

import json
from pathlib import Path

JSON_BOOKMARKS_FILE = Path("saved_verses.json")
MARKDOWN_LOG_FILE = Path("saved_verses.md")


def load_saved_verses() -> list[dict]:
    """Load saved verses from the local JSON file if it exists."""
    if not JSON_BOOKMARKS_FILE.exists():
        return []
    try:
        with JSON_BOOKMARKS_FILE.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_verse_locally(verse: dict) -> tuple[bool, Path, Path]:
    """
    Save a verse dictionary to saved_verses.json (deduplicated by global_number)
    and append a formatted block to saved_verses.md.
    """
    records = load_saved_verses()
    already_exists = any(item.get("global_number") == verse["global_number"] for item in records)

    if not already_exists:
        records.append(verse)
        with JSON_BOOKMARKS_FILE.open("w", encoding="utf-8") as json_file:
            json.dump(records, json_file, ensure_ascii=False, indent=2)

        append_to_markdown(verse)

    return (not already_exists, JSON_BOOKMARKS_FILE, MARKDOWN_LOG_FILE)


def append_to_markdown(verse: dict) -> None:
    """Append a human-readable entry to saved_verses.md."""
    is_new_file = not MARKDOWN_LOG_FILE.exists()
    with MARKDOWN_LOG_FILE.open("a", encoding="utf-8") as md_file:
        if is_new_file:
            md_file.write("# Saved Quran Verses Log\n\n")

        md_file.write(
            f"## Surah {verse['surah_english']} ({verse['surah_meaning']}) — {verse['reference']}\n"
            f"- **Global Ayah:** #{verse['global_number']} | **Juz:** {verse['juz']} | **Saved:** {verse['fetched_at']}\n"
            f"- **Audio:** [Listen (Mishary Alafasy)]({verse['audio_url']})\n\n"
            f"> {verse['arabic_text']}\n\n"
        )
        for trans in verse["translations"]:
            md_file.write(f"**[{trans['language']}] {trans['translator']}:** {trans['text']}\n\n")
        md_file.write("---\n\n")
