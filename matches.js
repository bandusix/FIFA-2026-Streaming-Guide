/* ============================================================
   FIFA World Cup 2026 — FIXTURE DATA  (auto-corrected daily)
   ------------------------------------------------------------
   This file is the SINGLE SOURCE OF TRUTH for match data and is
   the ONLY file the daily verification routine should edit.
   See RUNBOOK.md for the update procedure and UPDATE_LOG.md for
   the change history.

   Time convention: every kickoff is stored as the US Eastern
   (EDT, UTC-4) wall-clock with the "-04:00" suffix, i.e. the
   true instant. index.html converts it to each visitor's zone.

   Match object shape:
     {n, g|r, d, c, h, a, s?}
       n = match number (1-104)
       g = group letter "A".."L"   OR   r = round key
           (r32, r16, qf, sf, tp, final)
       d = ISO datetime with -04:00 offset
       c = host city (maps to a stadium in index.html V{})
       h = home team   a = away team
           - group stage: ISO flag code (e.g. "br", "gb-eng")
           - knockout:    slot object via W()/R()/TH(), or omit for TBD
       s = [home, away] score  (only for finished matches)
   ============================================================ */

// ISO date (YYYY-MM-DD) of the last successful verification against official sources.
window.WC_LAST_VERIFIED = "2026-07-12";

// Knockout placeholder builders + US Eastern offset constant.
const W = g => ({ k: "winner", g });
const R = g => ({ k: "runner", g });
const TH = g => ({ k: "third", g });
const ET = "-04:00";

window.WC_MATCHES = [
 {n:1,g:"A",d:"2026-06-11T15:00:00"+ET,c:"Mexico City",h:"mx",a:"za",s:[2,0]},
 {n:2,g:"A",d:"2026-06-11T22:00:00"+ET,c:"Zapopan",h:"kr",a:"cz",s:[2,1]},
 {n:3,g:"B",d:"2026-06-12T15:00:00"+ET,c:"Toronto",h:"ca",a:"ba",s:[1,1]},
 {n:4,g:"D",d:"2026-06-12T21:00:00"+ET,c:"Inglewood",h:"us",a:"py",s:[4,1]},
 {n:5,g:"C",d:"2026-06-13T21:00:00"+ET,c:"Foxborough",h:"ht",a:"gb-sct",s:[0,1]},
 {n:6,g:"D",d:"2026-06-14T00:00:00"+ET,c:"Vancouver",h:"au",a:"tr",s:[2,0]},
 {n:7,g:"C",d:"2026-06-13T18:00:00"+ET,c:"East Rutherford",h:"br",a:"ma",s:[1,1]},
 {n:8,g:"B",d:"2026-06-13T15:00:00"+ET,c:"Santa Clara",h:"qa",a:"ch",s:[1,1]},
 {n:9,g:"E",d:"2026-06-14T19:00:00"+ET,c:"Philadelphia",h:"ci",a:"ec",s:[1,0]},
 {n:10,g:"E",d:"2026-06-14T13:00:00"+ET,c:"Houston",h:"de",a:"cw",s:[7,1]},
 {n:11,g:"F",d:"2026-06-14T16:00:00"+ET,c:"Arlington",h:"nl",a:"jp",s:[2,2]},
 {n:12,g:"F",d:"2026-06-14T22:00:00"+ET,c:"Guadalupe",h:"se",a:"tn",s:[5,1]},
 {n:13,g:"H",d:"2026-06-15T18:00:00"+ET,c:"Miami Gardens",h:"sa",a:"uy",s:[1,1]},
 {n:14,g:"H",d:"2026-06-15T12:00:00"+ET,c:"Atlanta",h:"es",a:"cv",s:[0,0]},
 {n:15,g:"G",d:"2026-06-15T21:00:00"+ET,c:"Inglewood",h:"ir",a:"nz",s:[2,2]},
 {n:16,g:"G",d:"2026-06-15T15:00:00"+ET,c:"Seattle",h:"be",a:"eg",s:[1,1]},
 {n:17,g:"I",d:"2026-06-16T15:00:00"+ET,c:"East Rutherford",h:"fr",a:"sn",s:[3,1]},
 {n:18,g:"I",d:"2026-06-16T18:00:00"+ET,c:"Foxborough",h:"iq",a:"no",s:[1,4]},
 {n:19,g:"J",d:"2026-06-16T21:00:00"+ET,c:"Kansas City",h:"ar",a:"dz",s:[3,0]},
 {n:20,g:"J",d:"2026-06-17T00:00:00"+ET,c:"Santa Clara",h:"at",a:"jo",s:[3,1]},
 {n:21,g:"L",d:"2026-06-17T19:00:00"+ET,c:"Toronto",h:"gh",a:"pa",s:[1,0]},
 {n:22,g:"L",d:"2026-06-17T16:00:00"+ET,c:"Arlington",h:"gb-eng",a:"hr",s:[4,2]},
 {n:23,g:"K",d:"2026-06-17T13:00:00"+ET,c:"Houston",h:"pt",a:"cd",s:[1,1]},
 {n:24,g:"K",d:"2026-06-17T22:00:00"+ET,c:"Mexico City",h:"uz",a:"co",s:[1,3]},
 {n:25,g:"A",d:"2026-06-18T12:00:00"+ET,c:"Atlanta",h:"cz",a:"za",s:[1,1]},
 {n:26,g:"B",d:"2026-06-18T15:00:00"+ET,c:"Inglewood",h:"ch",a:"ba",s:[4,1]},
 {n:27,g:"B",d:"2026-06-18T18:00:00"+ET,c:"Vancouver",h:"ca",a:"qa",s:[6,0]},
 {n:28,g:"A",d:"2026-06-18T21:00:00"+ET,c:"Zapopan",h:"mx",a:"kr",s:[1,0]},
 {n:29,g:"C",d:"2026-06-19T20:30:00"+ET,c:"Philadelphia",h:"br",a:"ht",s:[3,0]},
 {n:30,g:"C",d:"2026-06-19T18:00:00"+ET,c:"Foxborough",h:"gb-sct",a:"ma",s:[0,1]},
 {n:31,g:"D",d:"2026-06-19T23:00:00"+ET,c:"Santa Clara",h:"tr",a:"py",s:[0,1]},
 {n:32,g:"D",d:"2026-06-19T15:00:00"+ET,c:"Seattle",h:"us",a:"au",s:[2,0]},
 {n:33,g:"E",d:"2026-06-20T16:00:00"+ET,c:"Toronto",h:"de",a:"ci",s:[2,1]},
 {n:34,g:"E",d:"2026-06-20T20:00:00"+ET,c:"Kansas City",h:"ec",a:"cw",s:[0,0]},
 {n:35,g:"F",d:"2026-06-20T13:00:00"+ET,c:"Houston",h:"nl",a:"se",s:[5,1]},
 {n:36,g:"F",d:"2026-06-21T00:00:00"+ET,c:"Guadalupe",h:"tn",a:"jp",s:[0,4]},
 {n:37,g:"H",d:"2026-06-21T18:00:00"+ET,c:"Miami Gardens",h:"uy",a:"cv",s:[2,2]},
 {n:38,g:"H",d:"2026-06-21T12:00:00"+ET,c:"Atlanta",h:"es",a:"sa",s:[4,0]},
 {n:39,g:"G",d:"2026-06-21T15:00:00"+ET,c:"Inglewood",h:"be",a:"ir",s:[0,0]},
 {n:40,g:"G",d:"2026-06-21T21:00:00"+ET,c:"Vancouver",h:"nz",a:"eg",s:[1,3]},
 {n:41,g:"I",d:"2026-06-22T20:00:00"+ET,c:"East Rutherford",h:"no",a:"sn",s:[3,2]},
 {n:42,g:"I",d:"2026-06-22T17:00:00"+ET,c:"Philadelphia",h:"fr",a:"iq",s:[3,0]},
 {n:43,g:"J",d:"2026-06-22T13:00:00"+ET,c:"Arlington",h:"ar",a:"at",s:[2,0]},
 {n:44,g:"J",d:"2026-06-22T23:00:00"+ET,c:"Santa Clara",h:"jo",a:"dz",s:[1,2]},
 {n:45,g:"L",d:"2026-06-23T16:00:00"+ET,c:"Foxborough",h:"gb-eng",a:"gh",s:[0,0]},
 {n:46,g:"L",d:"2026-06-23T19:00:00"+ET,c:"Toronto",h:"pa",a:"hr",s:[0,1]},
 {n:47,g:"K",d:"2026-06-23T13:00:00"+ET,c:"Houston",h:"pt",a:"uz",s:[5,0]},
 {n:48,g:"K",d:"2026-06-23T22:00:00"+ET,c:"Zapopan",h:"co",a:"cd",s:[1,0]},
 {n:49,g:"C",d:"2026-06-24T18:00:00"+ET,c:"Miami Gardens",h:"gb-sct",a:"br",s:[0,3]},
 {n:50,g:"C",d:"2026-06-24T18:00:00"+ET,c:"Atlanta",h:"ma",a:"ht",s:[4,2]},
 {n:51,g:"B",d:"2026-06-24T15:00:00"+ET,c:"Vancouver",h:"ch",a:"ca",s:[2,1]},
 {n:52,g:"B",d:"2026-06-24T15:00:00"+ET,c:"Seattle",h:"ba",a:"qa",s:[3,1]},
 {n:53,g:"A",d:"2026-06-24T21:00:00"+ET,c:"Mexico City",h:"cz",a:"mx",s:[0,3]},
 {n:54,g:"A",d:"2026-06-24T21:00:00"+ET,c:"Guadalupe",h:"za",a:"kr",s:[1,0]},
 {n:55,g:"E",d:"2026-06-25T16:00:00"+ET,c:"Philadelphia",h:"cw",a:"ci",s:[0,2]},
 {n:56,g:"E",d:"2026-06-25T16:00:00"+ET,c:"East Rutherford",h:"ec",a:"de",s:[2,1]},
 {n:57,g:"F",d:"2026-06-25T19:00:00"+ET,c:"Arlington",h:"jp",a:"se",s:[1,1]},
 {n:58,g:"F",d:"2026-06-25T19:00:00"+ET,c:"Kansas City",h:"tn",a:"nl",s:[1,3]},
 {n:59,g:"D",d:"2026-06-25T22:00:00"+ET,c:"Inglewood",h:"tr",a:"us",s:[3,2]},
 {n:60,g:"D",d:"2026-06-25T22:00:00"+ET,c:"Santa Clara",h:"py",a:"au",s:[0,0]},
 {n:61,g:"I",d:"2026-06-26T15:00:00"+ET,c:"Foxborough",h:"no",a:"fr",s:[1,4]},
 {n:62,g:"I",d:"2026-06-26T15:00:00"+ET,c:"Toronto",h:"sn",a:"iq",s:[5,0]},
 {n:63,g:"G",d:"2026-06-26T23:00:00"+ET,c:"Seattle",h:"eg",a:"ir",s:[1,1]},
 {n:64,g:"G",d:"2026-06-26T23:00:00"+ET,c:"Vancouver",h:"nz",a:"be",s:[1,5]},
 {n:65,g:"H",d:"2026-06-26T20:00:00"+ET,c:"Houston",h:"cv",a:"sa",s:[0,0]},
 {n:66,g:"H",d:"2026-06-26T20:00:00"+ET,c:"Zapopan",h:"uy",a:"es",s:[0,1]},
 {n:67,g:"L",d:"2026-06-27T17:00:00"+ET,c:"East Rutherford",h:"pa",a:"gb-eng",s:[0,2]},
 {n:68,g:"L",d:"2026-06-27T17:00:00"+ET,c:"Philadelphia",h:"hr",a:"gh",s:[2,1]},
 {n:69,g:"J",d:"2026-06-27T22:00:00"+ET,c:"Kansas City",h:"dz",a:"at",s:[3,3]},
 {n:70,g:"J",d:"2026-06-27T22:00:00"+ET,c:"Arlington",h:"jo",a:"ar",s:[1,3]},
 {n:71,g:"K",d:"2026-06-27T19:30:00"+ET,c:"Miami Gardens",h:"co",a:"pt",s:[0,0]},
 {n:72,g:"K",d:"2026-06-27T19:30:00"+ET,c:"Atlanta",h:"cd",a:"uz",s:[3,1]},
 {n:73,r:"r32",d:"2026-06-28T15:00:00"+ET,c:"Inglewood",h:"za",a:"ca",s:[0,1]},
 {n:74,r:"r32",d:"2026-06-29T16:30:00"+ET,c:"Foxborough",h:"de",a:"py",s:[1,1]},
 {n:75,r:"r32",d:"2026-06-29T21:00:00"+ET,c:"Guadalupe",h:"nl",a:"ma",s:[1,1]},
 {n:76,r:"r32",d:"2026-06-29T13:00:00"+ET,c:"Houston",h:"br",a:"jp",s:[2,1]},
 {n:77,r:"r32",d:"2026-06-30T17:00:00"+ET,c:"East Rutherford",h:"fr",a:"se",s:[3,0]},
 {n:78,r:"r32",d:"2026-06-30T13:00:00"+ET,c:"Arlington",h:"ci",a:"no",s:[1,2]},
 {n:79,r:"r32",d:"2026-06-30T22:00:00"+ET,c:"Mexico City",h:"mx",a:"ec",s:[2,0]},
 {n:80,r:"r32",d:"2026-07-01T12:00:00"+ET,c:"Atlanta",h:"gb-eng",a:"cd",s:[2,1]},
 {n:81,r:"r32",d:"2026-07-01T20:00:00"+ET,c:"Santa Clara",h:"us",a:"ba",s:[2,0]},
 {n:82,r:"r32",d:"2026-07-01T16:00:00"+ET,c:"Seattle",h:"be",a:"sn",s:[3,2]},
 {n:83,r:"r32",d:"2026-07-02T19:00:00"+ET,c:"Toronto",h:"pt",a:"hr",s:[2,1]},
 {n:84,r:"r32",d:"2026-07-02T15:00:00"+ET,c:"Inglewood",h:"es",a:"at",s:[3,0]},
 {n:85,r:"r32",d:"2026-07-02T23:00:00"+ET,c:"Vancouver",h:"ch",a:"dz",s:[2,0]},
 {n:86,r:"r32",d:"2026-07-03T18:00:00"+ET,c:"Miami Gardens",h:"ar",a:"cv",s:[3,2]},
 {n:87,r:"r32",d:"2026-07-03T21:30:00"+ET,c:"Kansas City",h:"co",a:"gh",s:[1,0]},
 {n:88,r:"r32",d:"2026-07-03T14:00:00"+ET,c:"Arlington",h:"au",a:"eg",s:[1,1]},
 {n:89,r:"r16",d:"2026-07-04T17:00:00"+ET,c:"Philadelphia",h:"py",a:"fr",s:[0,1]},
 {n:90,r:"r16",d:"2026-07-04T13:00:00"+ET,c:"Houston",h:"ca",a:"ma",s:[0,3]},
 {n:91,r:"r16",d:"2026-07-05T16:00:00"+ET,c:"East Rutherford",h:"br",a:"no",s:[1,2]},
 {n:92,r:"r16",d:"2026-07-05T21:00:00"+ET,c:"Mexico City",h:"mx",a:"gb-eng",s:[2,3]},
 {n:93,r:"r16",d:"2026-07-06T15:00:00"+ET,c:"Arlington",h:"pt",a:"es",s:[0,1]},
 {n:94,r:"r16",d:"2026-07-06T20:00:00"+ET,c:"Seattle",h:"us",a:"be",s:[1,4]},
 {n:95,r:"r16",d:"2026-07-07T12:00:00"+ET,c:"Atlanta",h:"ar",a:"eg",s:[3,2]},
 {n:96,r:"r16",d:"2026-07-07T16:00:00"+ET,c:"Vancouver",h:"ch",a:"co",s:[0,0]},
 {n:97,r:"qf",d:"2026-07-09T16:00:00"+ET,c:"Foxborough",h:"fr",a:"ma",s:[2,0]},
 {n:98,r:"qf",d:"2026-07-10T15:00:00"+ET,c:"Inglewood",h:"es",a:"be",s:[2,1]},
 {n:99,r:"qf",d:"2026-07-11T17:00:00"+ET,c:"Miami Gardens",h:"no",a:"gb-eng"},
 {n:100,r:"qf",d:"2026-07-11T21:00:00"+ET,c:"Kansas City",h:"ar",a:"ch"},
 {n:101,r:"sf",d:"2026-07-14T15:00:00"+ET,c:"Arlington",h:"fr",a:"es"},
 {n:102,r:"sf",d:"2026-07-15T15:00:00"+ET,c:"Atlanta"},
 {n:103,r:"tp",d:"2026-07-18T17:00:00"+ET,c:"Miami Gardens"},
 {n:104,r:"final",d:"2026-07-19T15:00:00"+ET,c:"East Rutherford"}
];
