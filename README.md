# FIFA World Cup 2026 — Multilingual Live Schedule

A single-page, dependency-free web app that shows the full **FIFA World Cup 2026**
fixture list (104 matches), localized to each visitor's **language**, **time zone**,
and **country** (which drives both the UI language and the official broadcast sources).

> **Status:** working prototype, verified in-browser. Schedule data is partially
> verified against official sources (see [`UPDATE_LOG.md`](UPDATE_LOG.md)); broadcast
> sources are official rights-holders that still need final per-country verification.
> See **Open tasks** in [`HANDOFF.md`](HANDOFF.md) before continuing development.

---

## ✨ Features

| Feature | Notes |
|---|---|
| **104 matches** | Group stage (A–L) + full knockout bracket (R32 → Final). |
| **12 UI languages** | English, Português, Español, 简体中文, 繁體中文, Français, Italiano, Русский, Deutsch, हिन्दी, Bahasa Indonesia, Türkçe. |
| **Auto-localized team names** | All 48 nations translated automatically via `Intl.DisplayNames` (no manual translation table). |
| **Local-time conversion** | Kickoffs stored as US-Eastern and converted to the visitor's own time zone via `Intl.DateTimeFormat`. |
| **Country-based delivery** | Visitor country (IP geo) selects the default UI language **and** the broadcast sources. Manual override available and persisted. |
| **Per-country broadcast sources** | 2 official rights-holders per country (62 countries). Hybrid aggregator (deep links extracted automatically via Playwright + Python) alongside official broadcasters. |
| **Endonym country picker** | Each country shown in its own script (日本, السعودية, Россия…), independent of UI language. |
| **Live / Full-time status** | Auto-refreshes every minute; authoritative status and live scores via the official FIFA API; "Today/Tomorrow" date grouping; team search; Upcoming/All filter. |
| **Responsive dark UI** | Works on mobile and desktop. |
| **Daily auto-verification** | A scheduled agent re-checks the schedule against official FIFA data each day (see [`RUNBOOK.md`](RUNBOOK.md)). |

---

## 🏃 Run it

No build step, no dependencies. Either:

```bash
# Option A — static server (recommended; matches .claude/launch.json)
python3 -m http.server 8765
# then open http://localhost:8765

# Option B — just open the file
open index.html        # works too: data files load via <script src>, not fetch
```

Network is used at runtime for: flag images (`flagcdn.com`) and IP geolocation
(`ipquery.io` + fallbacks). Everything else is local.

---

## 📁 File structure

```
FIFA2026/
├── index.html          # The entire app: markup + CSS + JS (UI, i18n, timezone, geo, render)
├── matches.js          # FIXTURE DATA — window.WC_MATCHES + window.WC_LAST_VERIFIED  ← daily routine edits this
├── sources.js          # BROADCAST SOURCES — window.WC_SOURCES (per country)
├── README.md           # This file
├── HANDOFF.md          # Technical deep-dive + conventions + open tasks (READ THIS to continue dev)
├── RUNBOOK.md          # Daily schedule-verification procedure (for the automated agent)
├── UPDATE_LOG.md       # Append-only change history (newest on top)
├── CONVERSATION_LOG.md # How the project evolved — original requirements & decisions
└── .claude/
    └── launch.json     # Local preview server config (python http.server :8765)
```

**Separation of concerns:** all data lives in `matches.js` (schedule) and `sources.js`
(broadcasters). `index.html` holds only logic + presentation. Never inline data into
`index.html`.

---

## 🧩 Data models

### `matches.js` — `window.WC_MATCHES` (array of 104)

```js
// Group-stage match
{ n:37, g:"G", d:"2026-06-15T21:00:00-04:00", c:"Inglewood", h:"ir", a:"nz" }
// Finished match adds a score
{ n:1,  g:"A", d:"2026-06-11T16:00:00-04:00", c:"Mexico City", h:"mx", a:"za", s:[2,0] }
// Knockout match — teams are placeholder slots until the bracket resolves
{ n:73, r:"r32", d:"2026-06-28T15:00:00-04:00", c:"Inglewood", h:R("A"), a:R("B") }
```

| Field | Meaning |
|---|---|
| `n` | Match number 1–104 (unique). |
| `g` | Group letter `"A".."L"` (group stage) **or** `r` = round key (`r32,r16,qf,sf,tp,final`). |
| `d` | Kickoff as **US-Eastern (EDT, UTC-4) wall-clock** with `-04:00` suffix = the true instant. |
| `c` | Host city (maps to a stadium in `V{}` inside `index.html`). |
| `h` / `a` | Home/away team. Group stage = ISO alpha-2 flag code (`"br"`, `"gb-eng"`). Knockout = slot object via `W("A")` / `R("B")` / `TH("A/B/C/D/F")`, or omit for TBD. |
| `s` | `[home, away]` score, only for finished matches. |

`window.WC_LAST_VERIFIED` = `"YYYY-MM-DD"` of the last verification (shown in the footer).

### `sources.js` — `window.WC_SOURCES` (keyed by country)

```js
window.WC_SOURCES = {
  "US": [ {name:"FOX Sports", url:"https://...", lang:"en"},
          {name:"Telemundo",  url:"https://...", lang:"es"} ],
  // ...
};
```

| Field | Meaning |
|---|---|
| `name` | Broadcaster display name. |
| `url` | Link to the broadcaster's **official** live player / streaming page. |
| `lang` | *(optional)* commentary language tag, shown as a small chip. |
| `matchNo` | *(optional)* restrict a source to one match; omit = applies to all matches. |

> ⚖️ **Broadcast sources.** We list official rights-holders per country. In addition, we provide a global fallback array of aggregator streams alongside the official ones.

---

## 🌍 How localization works

- **UI strings** → manual dictionary `T` in `index.html` (12 languages).
- **Team / country names in match cards** → `Intl.DisplayNames` in the active UI language
  (with manual overrides for `gb-eng`, `gb-sct`, `cd`).
- **Country picker labels** → **endonyms** via `Intl.DisplayNames` in each country's own
  locale (`COUNTRY_LOCALE` map) — independent of UI language.
- **Language picker labels** → native autonyms, hardcoded in `LANGS`.
- **Country → default language** → `COUNTRY_LANG` map (manual language choice overrides).
- **IP geolocation** → `ipquery.io` (primary) → `api.ip.sb` → `geojs.io` → `country.is` →
  `ipapi.co` fallback chain; timezone/locale as provisional guess until IP resolves.

See [`HANDOFF.md`](HANDOFF.md) for the full function-level walkthrough.

---

## 🔧 Common edits

- **Fix a kickoff time** → edit the match's `d` in `matches.js` (keep the `-04:00` form;
  conversion rules in `RUNBOOK.md`).
- **Add/replace a broadcaster** → edit `sources.js`.
- **Add a UI language** → add the locale to `LANGS` + a column to every key in `T`.
- **Add a country** → add it to `COUNTRY_LANG` (+ `COUNTRY_LOCALE` for its endonym) and,
  optionally, `sources.js`.
- **Fill knockout teams** → replace `W()/R()/TH()` slots with ISO codes once known.

---

## ⚠️ Known limitations

1. **Knockout bracket** — teams are placeholders until groups finalize.
2. **IP geolocation** — free public APIs (rate limits / occasional blocks); the fallback
   chain mitigates this, and a manual country picker is always available.

## 📝 Changelog & Iteration History

### Phase 6: Global SEO Domination & GMCA Standard (2026-06-21 to 2026-06-22)
- **Long-tail SEO Sitemap Explosion**: Overcame Single Page Application (SPA) indexing limitations by building a Node.js dynamic sitemap generator. It injects localized country names via `Intl.DisplayNames` and creates nearly 4,000 unique semantic URLs (e.g., `?match=1-墨西哥-vs-南非`) covering 104 matches across 37 languages.
- **Deep Technical SEO**: Deployed robust `hreflang` alternate tags, injected `SportsEvent` JSON-LD structured data for Google Rich Snippets, semantic `<h3>` HTML adjustments, and configured Google Search Console verification.
- **Social Fission & Meta Tags**: Upgraded Open Graph (OG) and Twitter Card mechanisms with dynamic high-CTR multi-language titles, descriptions, and custom thumbnail injections.
- **GMCA Scraper Architecture Migration**: Initiated the refactoring of all legacy scrapers into the strict **GMCA (Global Media Crawler Architect)** v23 standard. Created the isolated `FIFA-World-Cup-2026-scraper` framework for better logging, deduplication, and pipeline resilience.
- **Aggregator Cleanups (Livsports & Streamed.pk)**: Solved major data-pollution bugs where expired/stale IDs accumulated as 404 dead links, and irrelevant sports (Golf, NBA) were mistakenly attached to football matches. Implemented source-of-truth validation and automatic dead-link pruning.
- **Historical Data Hygiene (Pelota-Libretv)**: Fixed a logic flaw that appended 24/7 live TV channels to long-finished historical matches. Enforced a strict 12-hour expiration window and retroactively purged over 90 invalid historical TV source entries.

### Phase 5: Decoupled Architecture, Social Growth & Web Performance (2026-06-18 to 2026-06-20)
- **Crawler Architecture Decoupling**: Extracted `ppv.to`, `livsports.dpdns.org`, and `footreplays.com` into standalone Python crawlers (`streaming_crawlers/*.py`) and independent GitHub Actions workflows. Avoided concurrency conflicts and improved scraping stability.
- **Footreplays (Match Replay) Revamp**: Rewrote the replay crawler from a "blind date-guessing" approach to an active pagination-scraping model. Reverse-matched team slugs to official match IDs, successfully recovering 19+ lost match replays caused by timezone discrepancies.
- **Full i18n Domain Rendering**: Enhanced the frontend `sourcesFor` logic to correctly render dynamic streams (like `Full Match Replay`) with their respective domains while applying internationalization dictionaries.
- **Social Sharing & Virality**: Implemented a lightweight, native Web Share modal triggered via clicking the streaming source or a dedicated header button. Included QR code generation and inline SVG buttons for zero-dependency native sharing to Facebook, X, WhatsApp, and Telegram.
- **Smart TV Support**: Upgraded the Share modal to automatically capture focus, ensuring 100% usability on Android TV and webOS with physical D-Pad remotes.
- **Performance / SEO**: Added Google Analytics (GA4) with asynchronous loading. Massively optimized First-Paint speed by rewriting the sequential `init()` fetch logic into `Promise.allSettled()`, adding `<link rel="preconnect">` for IP geolocation, `<link rel="preload">` for critical scripts, and switching to an hourly-hash cache-busting strategy.

### Phase 4: Authoritative Data & Frontend Fixes (2026-06-17)
- **Authoritative LIVE Status**: Replaced local time-based kickoff heuristics. The UI now polls the official `api.fifa.com` every 60 seconds to accurately reflect Live status, real-time match minutes (e.g., `37'`, `HT`), and real-time scores.
- **Frontend Deep-link Mapping Fix**: Resolved a critical bug where the frontend `sourcesFor` logic overwrote and dropped third-party sources when fallback domain matching failed. All multi-link embeds (e.g., `Streamed.pk #1, #2`) now correctly append to the UI.
- **Proxy Geo-blocking Avoidance**: Scaled up proxy rotation using Webshare and Geonode (3000+ free IPs) to bypass strict 403 Forbidden blocks for Middle East, SEA, and Latin American official broadcasters (like Brazil's Globoplay and CazéTV).
- **Aggregator API Integration**: Added support for extracting raw video player iframes directly from `streamed.pk` and `worldcup26.ir` APIs, parsing their JSON responses to bypass HTML scraping limitations.

### Phase 3: Backend Automation & Crawlers (2026-06-16)
- **Robust Python Automation**: Deprecated the unreliable AI-prompt-based cron jobs. Built native Python scripts (`auto_update_schedule.py`, `official_streaming_crawler.py`, `live_streaming_crawler.py`) for deterministic, 30-minute interval data fetching and Git pushing.
- **Playwright Headless Crawling**: Implemented a headless browser crawler to automatically navigate official broadcast domains and third-party fallback sites (e.g., VIPBox, Footybite) to extract actual Deep Links (direct video playback URLs) for live matches.

### Phase 2: Android TV Optimization & Global Localization (2026-06-15)
- **Android TV / Gamepad UI UI Fixes**: Completely replaced native `<select>` dropdowns with large, accessible, full-screen Modals optimized for 16:9 displays and D-Pad remote navigation on older Android WebViews.
- **Expanded Localization**: Added full RTL (Right-to-Left) layout support and Arabic translation. Expanded language definitions to include 20 Indian regional languages (Hindi, Bengali, Tamil, etc.) and various SEA languages (Thai, Vietnamese, Malay).
- **Device Compatibility**: Added polyfills and fallbacks for `Intl.DisplayNames` to ensure the country selector renders properly on outdated Android TV systems.

### Phase 1: Initial Release (2026-06-15)
- **Core Architecture**: Launched the static, client-side only architecture (Vanilla JS + HTML/CSS).
- **Dynamic Timezones**: Implemented `Intl.DateTimeFormat` to convert all matches from US-Eastern to the visitor's local timezone.
- **Geo-targeting**: Added IP-based country detection to auto-select the UI language and display the relevant local broadcasting rights (covering 62 countries, 2 official sources each).

Full context and next steps: **[`HANDOFF.md`](HANDOFF.md)**.
