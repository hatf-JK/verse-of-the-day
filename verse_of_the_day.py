#!/usr/bin/env python3
"""
Verse of the Day — CLI & Interactive Client for the AlQuran Cloud API.
Supports random verses, deterministic daily verses, Surah:Ayah lookup,
English/Urdu translations, keyword search, and local JSON/Markdown bookmarking.
"""

import argparse
import datetime
import random
import sys
import urllib.parse
import requests

from storage import load_saved_verses, save_verse_locally

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
    """Return a deterministic ayah number (1..6236) seeded by today's date."""
    today_iso = datetime.date.today().isoformat()
    rng = random.Random(today_iso)
    return rng.randint(1, TOTAL_AYAHS)


def fetch_verse(reference: str | int, lang_key: str = "both") -> dict:
    """Fetch a Quran verse by global number or 'surah:ayah' with translations."""
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
        print(f"[Error] Verse reference '{reference}' was not found (use 1-6236 or Surah:Ayah like 2:255).", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as exc:
        print(f"[Error] Network failure while contacting AlQuran Cloud API: {exc}", file=sys.stderr)
        sys.exit(1)

    data_list = payload.get("data", [])
    if payload.get("code") != 200 or not data_list:
        print("[Error] Unexpected API response structure.", file=sys.stderr)
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


def search_keyword(keyword: str, limit: int = 5) -> None:
    """Search across all Surahs in English translation (en.sahih) for a keyword."""
    safe_keyword = urllib.parse.quote(keyword.strip())
    endpoint = f"{BASE_URL}/search/{safe_keyword}/all/en.sahih"

    try:
        response = requests.get(
            endpoint,
            headers={"Accept-Encoding": "gzip"},
            timeout=TIMEOUT_SECONDS,
        )
        if response.status_code == 404:
            print(f"\nNo verses found matching keyword: '{keyword}'.\n")
            return
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException as exc:
        print(f"[Error] Search request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    data = payload.get("data", {})
    count = data.get("count", 0)
    matches = data.get("matches", [])[:limit]

    print(f"\nFound {count} total matches for '{keyword}' (showing top {len(matches)}):")
    print("=" * 76)
    for match in matches:
        surah = match["surah"]
        ref = f"{surah['number']}:{match['numberInSurah']}"
        print(f"• [{ref}] Surah {surah['englishName']}: \"{match['text']}\"")
    print("=" * 76 + "\n")


def display_verse(verse: dict, mode_label: str = "RANDOM VERSE") -> None:
    """Render the verse, translations, and audio URL to stdout."""
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


def display_saved_history() -> None:
    """Display all locally bookmarked verses from saved_verses.json."""
    records = load_saved_verses()
    if not records:
        print("\nNo saved verses found yet. Run with --save to bookmark verses.\n")
        return

    print(f"\nSaved Verses History ({len(records)} bookmarked):")
    print("=" * 76)
    for idx, item in enumerate(records, start=1):
        print(
            f"{idx}. [{item['reference']}] Surah {item['surah_english']} "
            f"({item['surah_meaning']}) — Saved on {item['fetched_at']}"
        )
    print("=" * 76 + "\n")


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Fetch a random or daily Quran verse with English and Urdu translations via AlQuran Cloud API."
    )
    parser.add_argument(
        "-l",
        "--lang",
        choices=list(EDITIONS.keys()),
        default="both",
        help="Translation edition: 'en' (Sahih Intl), 'en-asad' (Asad), 'ur' (Jalandhry), 'ur-junagarhi' (Junagarhi), or 'both' (default).",
    )
    parser.add_argument(
        "-d",
        "--daily",
        action="store_true",
        help="Fetch deterministic Verse of the Day seeded by today's date instead of a random verse.",
    )
    parser.add_argument(
        "-r",
        "--ref",
        type=str,
        help="Fetch a specific verse by global number (1-6236) or Surah:Ayah (e.g., 2:255 or 55:13).",
    )
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save the fetched verse to saved_verses.json and saved_verses.md.",
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Search the Quran in English for a specific keyword (e.g., 'mercy', 'patience').",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="List all previously bookmarked verses from local storage.",
    )
    return parser


def main() -> None:
    """Entry point for CLI execution."""
    parser = build_parser()
    args = parser.parse_args()

    if args.history:
        display_saved_history()
        return

    if args.search:
        search_keyword(args.search)
        return

    if args.ref:
        target_ref = args.ref.strip()
        mode_label = f"SELECTED VERSE ({target_ref})"
    elif args.daily:
        target_ref = get_daily_ayah_number()
        mode_label = f"VERSE OF THE DAY ({datetime.date.today().isoformat()})"
    else:
        target_ref = random.randint(1, TOTAL_AYAHS)
        mode_label = "RANDOM VERSE"

    verse = fetch_verse(target_ref, lang_key=args.lang)
    display_verse(verse, mode_label=mode_label)

    if args.save:
        is_new, json_path, md_path = save_verse_locally(verse)
        if is_new:
            print(f"[Saved] Verse {verse['reference']} appended to {json_path} and {md_path}.\n")
        else:
            print(f"[Info] Verse {verse['reference']} is already bookmarked in {json_path}.\n")


if __name__ == "__main__":
    main()
