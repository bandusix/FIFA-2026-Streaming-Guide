# Skill: FIFA 2026 Third-Party Streams Crawler

## Overview
This skill extracts raw video player deep links (Embed URLs) from various third-party streaming aggregator sites and APIs. It matches these links against the official FIFA match schedule and outputs a structured JSON mapping for frontend consumption.

## 1. Target Data Sources (URL Types)

### 1.1 Web Scraping Targets (HTML Parsing via Playwright)
These are aggregator sites where the crawler parses HTML anchor `<a>` tags.
- `https://footybite.ac/fifa-world-cup`
- `https://www.vipboxtv.sk/live-now-stream`
- `https://olympicweb.me/live/2026-worldcup-stream`
- `https://buffstreams.plus/soccer-live-streams`
- `https://boxinginfo.info/#soccer`
- `https://mmafighter.info/`
- `https://ppv.to/#34`

### 1.2 Direct API Targets (JSON Parsing)
These are endpoints where the crawler fetches structured JSON data, bypassing HTML scraping.
- **Match List API**: `https://streamed.pk/api/matches/football`
- **Live Status API**: `https://streamed.pk/api/matches/live`
- **Stream Extraction API**: `https://streamed.pk/api/stream/{source}/{id}`

## 2. Match Resolution & Filtering

### 2.1 Time Window Filtering
The crawler only looks for matches that fall within the window of `[Now - 24 Hours, Future]`. Past matches (older than 24 hours) are skipped to save resources.

### 2.2 Fuzzy Team Matching
Matches are mapped using an internal `COUNTRY_CODES` dictionary. The crawler checks if the `href` or `innerText` of a scraped link (or the `title` field from an API) contains the names of **both** the Home and Away teams.
- *Example*: ISO codes `["ar", "br"]` map to keywords `["argentina"]` and `["brazil"]`.
- *Match logic*: If a link's text is "Watch Argentina vs Brazil HD", it successfully maps to the corresponding match ID (`m.n`).

## 3. Data Structure (Output JSON Schema)

The crawler outputs a `streams.json` file. The structure is a dictionary where the **keys are the official FIFA Match IDs (`m.n`)**, and the **values are arrays of stream objects**.

### Example Output:
```json
{
  "_live": [13, 14],
  "15": [
    {
      "source": "https://footybite.ac/fifa-world-cup",
      "url": "https://footybite.ac/event/spain-vs-cape-verde-islands",
      "text": "Spain vs Cape Verde Islands - HD English"
    },
    {
      "source": "https://streamed.pk",
      "url": "https://embed.st/embed/admin/ppv-spain-vs-cape-verde/1",
      "text": "Streamed.pk Embed (HD: True, Lang: English) #1"
    },
    {
      "source": "https://streamed.pk",
      "url": "https://embed.st/embed/admin/ppv-spain-vs-cape-verde/2",
      "text": "Streamed.pk Embed (HD: False, Lang: Spanish) #2"
    }
  ]
}
```

### Field Definitions:
- `_live` (Array of Integers): A special key containing Match IDs that are currently explicitly flagged as "LIVE" by third-party APIs.
- `{Match_ID}` (String/Integer): The official match number (e.g., 1 to 104).
  - `source` (String): The original aggregator URL or API root (e.g., `https://streamed.pk`). This is used by the frontend to replace specific fallback entries.
  - `url` (String): The **Deep Link / Embed URL**. This is the actual page containing the video iframe.
  - `text` (String): Descriptive text about the stream, including language, HD status, or link number.
