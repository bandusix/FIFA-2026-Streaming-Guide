import re
import json
import asyncio
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright

# Mapping ISO codes to team names for fuzzy matching
COUNTRY_CODES = {
    "ar": ["argentina"], "at": ["austria"], "au": ["australia"], "ba": ["bosnia", "herzegovina"], 
    "be": ["belgium"], "br": ["brazil"], "ca": ["canada"], "cd": ["congo"], 
    "ch": ["switzerland"], "ci": ["ivory", "cote"], "co": ["colombia"], "cv": ["cape", "cabo"], 
    "cw": ["curacao"], "cz": ["czech"], "de": ["germany"], "dz": ["algeria"], 
    "ec": ["ecuador"], "eg": ["egypt"], "es": ["spain"], "fr": ["france"], 
    "gb-eng": ["england"], "gb-sct": ["scotland"], "gh": ["ghana"], "hr": ["croatia"], 
    "ht": ["haiti"], "iq": ["iraq"], "ir": ["iran"], "jo": ["jordan"], 
    "jp": ["japan"], "kr": ["korea", "south korea"], "ma": ["morocco"], "mx": ["mexico"], 
    "nl": ["netherlands", "dutch"], "no": ["norway"], "nz": ["zealand"], "pa": ["panama"], 
    "pt": ["portugal"], "py": ["paraguay"], "qa": ["qatar"], "sa": ["saudi"], 
    "se": ["sweden"], "sn": ["senegal"], "tn": ["tunisia"], "tr": ["turkey", "turkiye"], 
    "us": ["usa", "united states", "america"], "uy": ["uruguay"], "uz": ["uzbekistan"], "za": ["south africa", "rsa"]
}

TARGET_SITES = [
    "https://footybite.ac/fifa-world-cup",
    "https://www.vipboxtv.sk/live-now-stream",
    "https://olympicweb.me/live/2026-worldcup-stream",
    "https://buffstreams.plus/soccer-live-streams",
    "https://boxinginfo.info/#soccer",
    "https://mmafighter.info/",
    "https://ppv.to/#34"
]

def load_schedule():
    with open("../matches.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract the window.WC_MATCHES array
    match = re.search(r'window\.WC_MATCHES\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not match:
        return []
    
    matches_str = match.group(1)
    
    # Simple regex to parse each match object
    # e.g., {n:13,g:"H",d:"2026-06-15T18:00:00"+ET,c:"Miami Gardens",h:"sa",a:"uy"}
    parsed_matches = []
    for line in matches_str.split('\n'):
        if '{n:' in line:
            n_match = re.search(r'n:(\d+)', line)
            d_match = re.search(r'd:"([^"]+)"', line)
            h_match = re.search(r'h:"([^"]+)"', line)
            a_match = re.search(r'a:"([^"]+)"', line)
            
            if n_match and d_match and h_match and a_match:
                # Add ET (-04:00) to the date string
                dt_str = d_match.group(1) + "-04:00"
                dt = datetime.fromisoformat(dt_str)
                parsed_matches.append({
                    "n": int(n_match.group(1)),
                    "d": dt,
                    "h": h_match.group(1),
                    "a": a_match.group(1)
                })
    return parsed_matches

def get_recent_matches(matches):
    # Determine "now" based on the system's timezone (using UTC for standard comparison)
    # The requirement is: Fetch matches from the past 24 hours up to all future matches
    now = datetime.now(timezone.utc)
    
    recent = []
    for m in matches:
        diff = m["d"] - now
        # diff >= -24h means it hasn't been over 24 hours since the match started.
        # This includes all future matches as well.
        if diff >= timedelta(hours=-24):
            recent.append(m)
    return recent

def matches_team(text, team_code):
    keywords = COUNTRY_CODES.get(team_code, [])
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            return True
    return False

async def fetch_links_from_site(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        # Scroll to load lazy content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        
        # Extract all links
        links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({href: e.href, text: e.innerText}))")
        return [l for l in links if l.get("href") and l.get("href").startswith("http")]
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

async def main():
    print("Loading schedule...")
    all_matches = load_schedule()
    recent_matches = get_recent_matches(all_matches)
    
    if not recent_matches:
        print("No matches within the [-24h, future] window found based on current system time.")
        print("Forcing 'now' to 2026-06-15 12:00:00 UTC for testing...")
        forced_now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
        for m in all_matches:
            diff = m["d"] - forced_now
            if diff >= timedelta(hours=-24):
                recent_matches.append(m)

    print(f"Found {len(recent_matches)} matches in the target window.")
    for m in recent_matches:
        h_name = COUNTRY_CODES.get(m['h'], [m['h']])[0].title()
        a_name = COUNTRY_CODES.get(m['a'], [m['a']])[0].title()
        print(f" - Match {m['n']}: {h_name} vs {a_name} ({m['d']})")

    results = {m["n"]: [] for m in recent_matches}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        
        for url in TARGET_SITES:
            print(f"\nScanning {url} ...")
            page = await context.new_page()
            links = await fetch_links_from_site(page, url)
            await page.close()
            
            # Cross-reference with matches
            for m in recent_matches:
                for link in links:
                    href = link["href"]
                    text = link["text"]
                    combined = f"{href} {text}"
                    
                    # If both home and away keywords are in the link text or URL
                    if matches_team(combined, m["h"]) and matches_team(combined, m["a"]):
                        # The URL extracted (e.g. https://footybite.ac/event/spain-vs-cape-verde-islands) 
                        # IS the actual player page where the video embed lives on these sites.
                        # We just need to deduplicate it.
                        if not any(r["url"] == href for r in results[m["n"]]):
                            results[m["n"]].append({
                                "source": url,
                                "url": href,
                                "text": text.replace('\n', ' ').strip()
                            })
                            print(f"   -> Match {m['n']} found player page: {href}")

        await browser.close()
        
    # Output final summary
    print("\n\n=== FINAL AGGREGATED LINKS ===")
    for m in recent_matches:
        h_name = COUNTRY_CODES.get(m['h'], [m['h']])[0].title()
        a_name = COUNTRY_CODES.get(m['a'], [m['a']])[0].title()
        print(f"\nMatch {m['n']} | {h_name} vs {a_name}")
        if not results[m["n"]]:
            print("  No streams found.")
        for r in results[m["n"]]:
            print(f"  [Source: {r['source']}] {r['url']}")
            
    # Write to streams.json in the parent directory
    output_path = "../streams.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            # We map match number to list of source dicts
            # We'll reformat slightly to match sources.js format if helpful, or just export raw
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully wrote streams data to {output_path}")
    except Exception as e:
        print(f"\nFailed to write to {output_path}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
