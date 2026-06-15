# Developer Handoff — FIFA World Cup 2026 Schedule

This document is written for the next developer or AI agent (Gemini / Trae / Codex /
Claude) picking up the project. It explains the architecture, every important function,
the conventions you must not break, the lessons already learned, and the prioritized
open tasks. Read this fully before editing.

---

## 1. Tech stack & philosophy

- **Vanilla HTML + CSS + JavaScript in one file** (`index.html`). No framework, no build,
  no package manager, no dependencies. Keep it that way unless there's a strong reason.
- **Data is separated from logic**: `matches.js` (schedule) and `sources.js` (broadcasters)
  are loaded via `<script src>` and expose globals (`window.WC_MATCHES`,
  `window.WC_LAST_VERIFIED`, `window.WC_SOURCES`). This keeps automated edits low-risk and
  works under `file://` (no fetch/CORS needed for data).
- **Browser built-ins do the heavy lifting**: `Intl.DisplayNames` (localized country/team
  names + endonyms), `Intl.DateTimeFormat` (time-zone conversion + localized dates).
- **Runtime network calls** (all optional, all degrade gracefully): flag images from
  `flagcdn.com`; IP geolocation from `ipquery.io` + fallbacks.

---

## 2. Architecture & data flow

```
Page load
  │
  ├─ matches.js  → window.WC_MATCHES (104), window.WC_LAST_VERIFIED
  ├─ sources.js  → window.WC_SOURCES (per-country broadcasters)
  │
  └─ init()
       ├─ build language <select> (LANGS, native names)
       ├─ country = localStorage 'wc26country'  ||  provisionalCountry()   (timezone/locale)
       ├─ lang    = resolveLang()   (manual 'wc26lang' > country default > browser)
       ├─ wire listeners (filter / search / country / language)
       ├─ applyStrings() + render()                      ← first paint (provisional country)
       ├─ detectCountryIP() [async]  →  refine country   ← second paint if IP differs
       └─ setInterval(render, 60000)                     ← refresh LIVE/FT status
```

Two render triggers after load: an immediate paint with the provisional (timezone-based)
country, then a re-paint once the async IP lookup resolves (only if the user hasn't
manually chosen a country).

---

## 3. File-by-file

### `index.html`
- **`<head>`**: meta + a single `<style>` block. CSS uses custom properties (`:root`
  variables) for the dark theme. Layout is CSS grid; `.match` cards are
  `grid-template-columns: 84px 1fr auto` with a full-width `.watch` row spanning all
  columns. Responsive breakpoint at `560px`.
- **`<body>`**: `header.hero` (title `#appTitle`, time-zone/country note `#tznote`) →
  `.controls` (sticky: `#fUpcoming`/`#fAll` filter, `#search`, `#countrySel`, `#langSel`)
  → `main.wrap` (`#list`, `#empty`, `#footer`).
- **`<script>`**: see the function reference below.

### `matches.js` / `sources.js`
Data only (schemas in `README.md`). `matches.js` also defines the knockout slot builders
`W(g)`, `R(g)`, `TH(g)` and the `ET = "-04:00"` constant used to compose timestamps.

---

## 4. Function reference (`index.html` script)

**Config / data tables**
- `LANGS` — `[code, nativeName]` for the 12 UI languages. Native names are autonyms and are
  never re-localized.
- `T` — i18n dictionary: `T[key][lang]` → string (falls back to `.en`). Add a key here for
  every new UI string; add a column to every key when adding a language.
- `NAME_OVERRIDE` — team-name overrides for codes `Intl` can't resolve as regions:
  `gb-eng`, `gb-sct`, and `cd` (nicer "DR Congo" label). Keyed by UI language.
- `V` — host city → stadium name.
- `COUNTRY_LANG` — country → default UI language (en fallback). Drives auto language.
- `COUNTRY_LOCALE` — country → its *own* primary locale, used for **endonyms** in the
  country picker. Independent of `COUNTRY_LANG`.
- `TZ_COUNTRY` — partial timezone → country map for the provisional guess.

**Helpers**
- `tt(key)` — translate a UI string into the active `lang`.
- `countryName(code)` — localized country/**team** name in the active UI language
  (used for match cards + search). Honors `NAME_OVERRIDE`.
- `countryEndonym(code)` — country name in **its own** language (country picker + 📍 note).
- `flagURL(code)` — `https://flagcdn.com/w80/{code}.png`.
- `fmtTime(date)` / `dayKey(date)` / `dayLabel(date)` — localized time / date-bucket key /
  "Today/Tomorrow/weekday" header, all via `Intl` in the active `lang`.
- `roundName(m)` — "Group X" or localized round name.
- `langForCountry(c)` / `resolveLang()` — country→language and the manual-override-aware
  language resolution.
- `provisionalCountry()` — timezone (`TZ_COUNTRY`) then locale region as a pre-IP guess.
- `detectCountryIP()` — **async IP→country chain**: `ipquery.io/?format=json` →
  `api.ip.sb` → `geojs.io` → `country.is` → `ipapi.co`. Each has a 2.5 s `AbortController`
  timeout; first valid 2-letter code wins. Returns `null` if all fail.
- `sourcesFor(matchNo)` — broadcasters for the current `country`, filtered by `matchNo`.
- `detectLang()` — browser-language fallback (only used when no country/manual language).

**Render**
- `sideHTML(side, m, idx)` — one team row. `side` is an ISO code (flag + localized name,
  + score + loser dimming) or a knockout slot object (`{k:'winner'|'runner'|'third', g}` →
  localized label, no flag) or `undefined` (TBD).
- `render()` — filters (`upcoming` hides finished matches; team search by localized name or
  code), sorts by kickoff, groups by local day, builds cards (time/status, two sides, group
  /round chip + venue, and the `.watch` row from `sourcesFor`). Re-run on every state change
  and once a minute.
- `applyStrings()` — sets all static UI text for the active language, the `#tznote`
  (timezone + 📍 endonym country), the footer (FIFA link + `WC_LAST_VERIFIED` freshness),
  and calls `populateCountrySelect()`.
- `populateCountrySelect()` — fills `#countrySel` with **endonym** labels, sorted by English
  name for a stable order; injects the detected country if it's outside the curated list.
- `init()` — see the data-flow diagram in §2.

---

## 5. Conventions you must not break

1. **Kickoff storage = US-Eastern wall-clock + `-04:00`.** Every `d` is the true instant
   expressed in EDT. The page converts to the viewer's zone. To convert a venue-LOCAL time
   to what you store: Pacific (PDT, UTC-7) **+3h**; US Central (CDT, UTC-5) **+1h**; Mexico
   Central (UTC-6, no DST) **+2h**; Eastern (EDT) **as-is**. If a source gives UTC, just
   re-express it at `-04:00`. (Full table in `RUNBOOK.md`.)
2. **Team codes = ISO 3166-1 alpha-2**, lowercase in data (`"br"`), used for both identity
   and flag. Exceptions handled in `NAME_OVERRIDE`: `gb-eng`, `gb-sct`, `cd`.
3. **Country codes in `WC_SOURCES`, `COUNTRY_LANG`, `COUNTRY_LOCALE` = UPPERCASE alpha-2.**
4. **Data only in `matches.js` / `sources.js`.** Never inline schedule/broadcaster data into
   `index.html`.
5. **Broadcast sources.** Official rights-holders are provided per country. A global array of aggregator streams (`WC_SOURCES_FALLBACK`) is also aggregated and shown alongside local official sources.
6. **localStorage keys**: `wc26lang` (manual language), `wc26country` (manual country).
   Their presence means "user chose this" → it overrides auto-detection.

---

## 6. Lessons already learned (don't repeat these)

- **ESPN schedule data is unreliable for non-Eastern venues** — it mislabels/мis-converts
  late-night Pacific and Mexico kickoffs (showed up as bogus `00:00` times). Several were
  corrected; trust the FIFA API / Wikipedia per-group instead.
- **Free-text web fetches of Wikipedia jumble the match→time mapping.** A bulk multi-group
  summary once ordered Group C wrong and produced an impossible 5-hour gap at an Eastern
  venue. Always fetch **one group at a time** and ask for the **match number + exact
  kickoff (with offset)**; only apply a change if **two sources agree** or it fixes an
  obviously-broken value.
- **`ip.skk.moe` cannot be used as a runtime source** — no CORS headers, so a cross-origin
  `fetch` fails. It's fine as a manual verification tool in a browser tab only.
- **`ipquery.io` own-IP**: `GET /` returns plain text; use `GET /?format=json` for the
  caller's full JSON in one call (`location.country_code`).
- **`api.fifa.com` was unreachable from the local fetch tool** this session — the cloud
  daily routine should attempt it; it may have different network access.

---

## 7. Testing / verifying changes

A local preview server is configured in `.claude/launch.json` (python http.server :8765).
Manual checks used during development (adapt for your tooling):

```js
// In the page console / preview eval:
window.WC_MATCHES.length                    // expect 104
new Set(WC_MATCHES.map(m=>m.n)).size         // expect 104 (unique numbers)
// switch country and confirm language + sources follow:
const cs=document.getElementById('countrySel'); cs.value='BR'; cs.dispatchEvent(new Event('change'));
// clear overrides to test auto-detect:
localStorage.clear(); location.reload();
```

After any data edit: confirm the page still loads (no JS syntax error), 104 cards render
under "All matches", and times/labels look right in 2–3 languages.

---

## 8. The daily verification agent

A scheduled task (`fifa2026-daily-schedule-verify`, stored in
`~/.claude/scheduled-tasks/`) runs every day ~07:15 local and re-verifies `matches.js`
against official FIFA data, then appends to `UPDATE_LOG.md`. Its full procedure is in
[`RUNBOOK.md`](RUNBOOK.md). If you're not in the Claude environment, you can run the same
procedure manually — it's just: pull official data → diff → fix `matches.js` → bump
`WC_LAST_VERIFIED` → log.

---

## 9. Open tasks (prioritized)

1. **Schedule source of truth → FIFA JSON API.** Wire the official
   `api.fifa.com/api/v3/calendar/matches` (exact UTC timestamps) as the authoritative
   feed and regenerate `matches.js` from it. Resolves all remaining time discrepancies.
2. **Resolve open schedule discrepancies** listed at the top of `UPDATE_LOG.md`
   (e.g. matches 31, 32, and any single-source suspicions).
3. **Verify broadcast sources** in `sources.js` against FIFA's official "Where to Watch"
   per country; fix names/URLs and add missing countries (Sub-Saharan Africa via
   SuperSport/DStv, more SEA/LatAm).
4. **Fill knockout teams** as groups finalize: replace `W()/R()/TH()` with ISO codes and
   wire R16+ matchups.
5. **Live scores** — optionally pull live/final scores (the `s:[h,a]` field already renders).
6. **Optional polish**: per-match calendar (.ics) export; deep-links/anchors; PWA/offline;
   add more UI languages (e.g. Arabic — would also enable RTL and proper MENA UI).

---

## 10. Quick orientation for an AI agent

- Start at `README.md` (what it is) → this file (how it works) → `UPDATE_LOG.md` (what's
  been changed and what's still open) → `CONVERSATION_LOG.md` (why decisions were made).
- The single most valuable improvement is **task #1** (FIFA JSON API as source of truth).
- Respect the conventions in §5 and the lessons in §6 — they were learned the hard way.
