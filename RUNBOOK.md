# FIFA 2026 Schedule — Daily Verification Runbook

This project displays the FIFA World Cup 2026 schedule. Kickoff times and venues
**must be re-verified against official FIFA data every day** because published
secondary sources (ESPN etc.) have proven unreliable — especially for late-night
and US-West-Coast/Pacific-venue games (a recurring timezone-conversion bug that
surfaces as bogus `12:00 AM ET` kickoffs).

## Files

| File | Role |
|------|------|
| `matches.js` | **Single source of truth** for fixture data. The ONLY file this routine edits. |
| `sources.js` | Broadcast/streaming sources keyed by country (`window.WC_SOURCES`). Edited only when broadcast data changes — not part of the daily schedule pass. |
| `index.html` | UI + i18n + timezone + IP-geolocation/country logic. Loads `matches.js` + `sources.js`. Do **not** put data here. |
| `UPDATE_LOG.md` | Append-only change history. One entry per run. |
| `RUNBOOK.md` | This file. |

## Data conventions (in `matches.js`)

- Every kickoff is stored as the **US Eastern (EDT, UTC-4)** wall-clock with the
  `-04:00` suffix — i.e. the true instant. The page converts it to the visitor's
  local zone, so you only ever store the ET equivalent.
- To convert an official **local** kickoff to what goes in the file:
  - Pacific venues (LA/Inglewood, Seattle, Vancouver, San Francisco/Santa Clara):
    local PDT (UTC-7) **+ 3h** = ET value to store.
  - Mountain — none in 2026.
  - Central venues (Houston, Kansas City, Dallas/Arlington, Mexico City,
    Guadalajara/Zapopan, Monterrey/Guadalupe): local CDT (UTC-5) **+ 1h** = ET.
  - Eastern venues (Atlanta, Miami, NY/NJ, Boston/Foxborough, Philadelphia,
    Toronto): local already = ET, store as-is.
- `window.WC_LAST_VERIFIED` must be set to the run date (`YYYY-MM-DD`).

## Procedure (run daily)

1. **Fetch authoritative data.** PRIMARY source of truth = the **official FIFA JSON
   calendar API** (`https://api.fifa.com/api/v3/calendar/matches?...`), which returns
   exact UTC timestamps — no timezone math, no summarizer jumbling. (It was unreachable
   from one local fetch tool; attempt it from this environment, and if it needs
   competition/season IDs, discover them via `/api/v3/calendar/competitions`.)
   FALLBACK if the API is unreachable: **Wikipedia** per-group pages
   `2026_FIFA_World_Cup_Group_A` … `_Group_L` + the knockout-stage page — but fetch
   **ONE GROUP AT A TIME** and ask for each row's exact kickoff (with venue-local
   timezone + UTC offset) AND its match number. ⚠️ Lesson learned: free-text BULK
   fetches jumble the match→time mapping (a past run mis-ordered Group C and returned
   an impossible 5 h gap at an Eastern venue). Only apply a change when it is
   **corroborated by a second source** or fixes an obviously-broken value.
2. **Compare** every match in `matches.js` against the official source: kickoff
   datetime, host city, the two teams, group/round, and — once played —
   the final score (add `s:[home,away]` for finished matches).
3. **Correct** only what differs. Edit `matches.js` in place. Convert official
   local times to the stored ET value using the table above. Keep formatting/comments.
4. **Update knockout teams** as groups finalize: replace `W("A")` / `R("B")` /
   `TH(...)` placeholder slots with real ISO flag codes (e.g. `"br"`) once known,
   and fill Round-of-16+ matchups when the bracket resolves.
5. **Bump** `window.WC_LAST_VERIFIED` to today's date.
6. **Log** the run in `UPDATE_LOG.md`: date, sources checked, and a bullet per
   change (`Match N: old → new`). If nothing changed, still add a "no changes" line.
7. **Sanity check**: 104 matches total, every `n` unique 1–104, no syntax errors
   (the page must still load). If a preview server is available, reload and confirm
   the schedule renders with no console errors.

## Team code reference

ISO 3166-1 alpha-2 codes are used as both the team id and the flag
(`flagcdn.com/w80/<code>.png`). Non-region exceptions handled in `index.html`:
`gb-eng` (England), `gb-sct` (Scotland), `cd` (DR Congo override label).
