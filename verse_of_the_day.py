#!/usr/bin/env python3
"""Verse of the Day - Core AlQuran Cloud API Client."""

import random
import sys
import requests

BASE_URL = "https://api.alquran.cloud/v1"
TOTAL_AYAHS = 6236
TIMEOUT_SECONDS = 10


def fetch_random_verse(edition: str = "en.sahih") -> dict:
    """Fetch a random Quran verse in Uthmani Arabic and the chosen translation."""
    ayah_number = random.randint(1, TOTAL_AYAHS)
    endpoint = f"{BASE_URL}/ayah/{ayah_number}/editions/quran-uthmani,{edition}"

    try:
        response = requests.get(
            endpoint,
            headers={"Accept-Encoding": "gzip"},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException as exc:
        print(f"[Error] Network failure while contacting AlQuran Cloud API: {exc}", file=sys.stderr)
        sys.exit(1)

    if payload.get("code") != 200 or "data" not in payload or len(payload["data"]) < 2:
        print("[Error] Unexpected payload structure received from API.", file=sys.stderr)
        sys.exit(1)

    arabic_data = payload["data"][0]
    translation_data = payload["data"][1]
    surah = arabic_data["surah"]

    return {
        "global_number": arabic_data["number"],
        "reference": f"{surah['number']}:{arabic_data['numberInSurah']}",
        "surah_english": surah["englishName"],
        "surah_meaning": surah["englishNameTranslation"],
        "revelation_type": surah["revelationType"],
        "juz": arabic_data["juz"],
        "arabic_text": arabic_data["text"],
        "translation_text": translation_data["text"],
        "translator": translation_data["edition"]["englishName"],
    }


def display_verse(verse: dict) -> None:
    """Print the formatted verse and metadata to standard output."""
    divider = "=" * 72
    print(f"\n{divider}")
    print(
        f"  SURAH {verse['surah_english'].upper()} ({verse['surah_meaning']}) "
        f"— Ayah {verse['reference']} [{verse['revelation_type']} | Juz {verse['juz']}]"
    )
    print(divider)
    print(f"\n{verse['arabic_text']}\n")
    print(f"Translation ({verse['translator']}):")
    print(f"  \"{verse['translation_text']}\"")
    print(f"{divider}\n")


if __name__ == "__main__":
    verse_data = fetch_random_verse()
    display_verse(verse_data)
