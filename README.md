# Verse of the Day

A command-line Python application that fetches live Quranic verses, Arabic script (Uthmani), English translations, Urdu translations, and audio recitation links using the open-source [AlQuran Cloud REST API](https://alquran.cloud/api).

## Features

- **Random Verse Fetching:** Pulls any random verse from all 6,236 Ayahs in the Quran in a single multi-edition HTTP request.
- **Deterministic Verse of the Day (`--daily`):** Generates a consistent daily verse seeded by the current date.
- **English & Urdu Translations (`--lang`):** Supports Saheeh International (`en`), Muhammad Asad (`en-asad`), Fateh Muhammad Jalandhry (`ur`), Muhammad Junagarhi (`ur-junagarhi`), or side-by-side bilingual output (`both`).
- **Direct Reference Lookup (`--ref`):** Fetch any specific verse by `Surah:Ayah` (e.g., `2:255` or `55:13`) or global Ayah number (`1`–`6236`).
- **Keyword Search (`--search`):** Searches across the Quranic text for matching English keywords.
- **Local Bookmarking (`--save` & `--history`):** Saves favorite verses to `saved_verses.json` and exports a formatted Markdown journal (`saved_verses.md`).

## Prerequisites & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hatf-JK/verse-of-the-day.git
   cd verse-of-the-day
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

#### 1. Fetch a random verse with both English and Urdu translations (default)
```bash
python3 verse_of_the_day.py
```
###### 
#### 2. Fetch today's deterministic Verse of the Day and save it locally
```bash
python3 verse_of_the_day.py --daily --save
```
###### 
#### 3. Fetch only the Urdu translation (Fateh Muhammad Jalandhry)
```bash
python3 verse_of_the_day.py --lang ur
```
###### 
#### 4. Fetch a specific verse (Ayat al-Kursi, 2:255)
```bash
python3 verse_of_the_day.py --ref 2:255
```
###### 
#### 5. Search verses by keyword
```bash
python3 verse_of_the_day.py --search patience
```
###### 
#### 6. View locally saved bookmarks
```bash
python3 verse_of_the_day.py --history
```

### Sample Output

```plaintext
$ python3 verse_of_the_day.py --ref 94:5 --lang both

============================================================================
  [SELECTED VERSE (94:5)] SURAH ASH-SHARH (The Consolation) — سُورَةُ الشَّرۡحِ
  Reference: 94:5 (Global Ayah #6095) | Meccan | Juz 30 | Page 596
============================================================================

  فَإِنَّ مَعَ ٱلْعُسْرِ يُسْرًا

----------------------------------------------------------------------------
  [EN] Saheeh International (en.sahih):
  For indeed, with hardship [will be] ease.

  [UR] جالندہری (ur.jalandhry):
  پس بے شک مشکل کے ساتھ آسانی ہے

----------------------------------------------------------------------------
  Audio Recitation (Mishary Alafasy): [https://cdn.islamic.network/quran/audio/128/ar.alafasy/6095.mp3](https://cdn.islamic.network/quran/audio/128/ar.alafasy/6095.mp3)
============================================================================
```

## API Reference

- **Provider:** [AlQuran Cloud API v1](https://api.alquran.cloud/v1)
- **Authentication:** None required (Open-source public REST API)
