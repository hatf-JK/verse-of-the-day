#!/usr/bin/env python3
"""Verse of the Day - Multi-edition English & Urdu AlQuran Cloud client."""

import datetime
import random
import sys
import requests

BASE_URL = "https://api.alquran.cloud/v1"
AUDIO_CDN_TEMPLATE = "https://cdn.islamic.network/quran/audio/128/ar.alafasy/{number}.mp3"
TOTAL_AYAHS = 6236
TIMEOUT_SECONDS = 10

EDITIONS = {
    "en": ["en.sahih"],
    "en-asad": ["en.asad"],
    "ur": ["ur.jalandhry"],
    "ur-junagarhi": ["ur.junagarhi"],
    "both": ["en.sahih", "ur.jalandhry"],
}


def get_daily_ayah_number() -> int:
    """Generate a deterministic ayah number (1..6236) seeded by today's UTC date."""
    today_iso = datetime.date.today().isoformat()
    rng = random.Random(today_iso)
    return rng.randint(1, TOTAL_AYAHS)


def fetch_verse(reference: str | int, lang_key: str = "both") -> dict:
    """
    Fetch a Quran verse by global number (1..6236) or 'surah:ayah' reference
    along with Uthmani Arabic and requested English/Urdu translation editions.
    """
    selected_editions = EDITIONS.get(lang_key, EDITIONS["both"])
    editions_param = ",".join(["quran-uthmani"] + selected_editions)
    endpoint = f"{BASE_URL}/ayah/{reference}/editions/{editions_param}"

    try:
        response = requests.get(
            endpoint,
            headers={"Accept-Encoding": "gzip"},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.HTTPError:
        print(f"[Error] Reference '{reference}' was not found on AlQuran Cloud API.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as exc:
        print(f"[Error] Network failure while contacting AlQuran Cloud API: {exc}", file=sys.stderr)
        sys.exit(1)

    data_list = payload.get("data", [])
    if payload.get("code") != 200 or not data_list:
        print("[Error] Invalid response payload from API.", file=sys.stderr)
        sys.exit(1)

    arabic_entry = data_list[0]
    surah = arabic_entry["surah"]
    global_number = arabic_entry["number"]

    translations = []
    for item in data_list[1:]:
        edition_meta = item["edition"]
        translations.append(
            {
                "edition_id": edition_meta["identifier"],
                "language": edition_meta["language"].upper(),
                "translator": edition_meta["name"] if edition_meta["language"] == "ur" else edition_meta["englishName"],
                "text": item["text"],
            }
        )

    return {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "global_number": global_number,
        "reference": f"{surah['number']}:{arabic_entry['numberInSurah']}",
        "surah_number": surah["number"],
        "surah_arabic": surah["name"],
        "surah_english": surah["englishName"],
        "surah_meaning": surah["englishNameTranslation"],
        "revelation_type": surah["revelationType"],
        "juz": arabic_entry["juz"],
        "page": arabic_entry["page"],
        "arabic_text": arabic_entry["text"],
        "audio_url": AUDIO_CDN_TEMPLATE.format(number=global_number),
        "translations": translations,
    }


def display_verse(verse: dict, mode_label: str = "RANDOM VERSE") -> None:
    """Render the verse, translations, and audio recitation URL in the terminal."""
    divider = "=" * 76
    sub_divider = "-" * 76
    print(f"\n{divider}")
    print(f"  [{mode_label}] SURAH {verse['surah_english'].upper()} ({verse['surah_meaning']}) — {verse['surah_arabic']}")
    print(
        f"  Reference: {verse['reference']} (Global Ayah #{verse['global_number']}) | "
        f"{verse['revelation_type']} | Juz {verse['juz']} | Page {verse['page']}"
    )
    print(divider)
    print(f"\n  {verse['arabic_text']}\n")
    print(sub_divider)

    for trans in verse["translations"]:
        print(f"  [{trans['language']}] {trans['translator']} ({trans['edition_id']}):")
        print(f"  {trans['text']}\n")

    print(sub_divider)
    print(f"  Audio Recitation (Mishary Alafasy): {verse['audio_url']}")
    print(f"{divider}\n")


if __name__ == "__main__":
    random_ayah = random.randint(1, TOTAL_AYAHS)
    verse_info = fetch_verse(random_ayah, lang_key="both")
    display_verse(verse_info, mode_label="RANDOM VERSE")
