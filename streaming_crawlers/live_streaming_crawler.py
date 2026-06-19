import re
import json
import asyncio
import urllib.request
import subprocess
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
    "https://mmafighter.info/"
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

def fetch_streamed_pk_api(recent_matches, results):
    print("\nScanning API: https://streamed.pk/api/matches/football ...")
    try:
        req = urllib.request.Request("https://streamed.pk/api/matches/football", headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req).read().decode('utf-8')
        api_matches = json.loads(data)
    except Exception as e:
        print("Error fetching streamed.pk matches:", e)
        api_matches = []

    # Also fetch currently live matches to optimize status
    live_match_ids = set()
    try:
        req_live = urllib.request.Request("https://streamed.pk/api/matches/live", headers={'User-Agent': 'Mozilla/5.0'})
        live_data = urllib.request.urlopen(req_live).read().decode('utf-8')
        live_matches = json.loads(live_data)
        for lm in live_matches:
            title = lm.get('title', '')
            # Match to our recent_matches
            for m in recent_matches:
                if matches_team(title, m["h"]) and matches_team(title, m["a"]):
                    live_match_ids.add(m["n"])
    except Exception as e:
        print("Error fetching streamed.pk live matches:", e)

    # Store live match ids in a special key in results
    if "_live" not in results:
        results["_live"] = []
    results["_live"] = list(set(results["_live"] + list(live_match_ids)))

    for m in recent_matches:
        for api_m in api_matches:
            title = api_m.get('title', '')
            if matches_team(title, m["h"]) and matches_team(title, m["a"]):
                # Found a match, now fetch its streams
                sources = api_m.get('sources', [])
                for s in sources:
                    s_name = s.get('source')
                    s_id = s.get('id')
                    try:
                        s_req = urllib.request.Request(f"https://streamed.pk/api/stream/{s_name}/{s_id}", headers={'User-Agent': 'Mozilla/5.0'})
                        s_data = urllib.request.urlopen(s_req).read().decode('utf-8')
                        streams = json.loads(s_data)
                        for idx, st in enumerate(streams):
                            if 'embedUrl' in st:
                                embed_url = st['embedUrl']
                                if not any(r["url"] == embed_url for r in results[m["n"]]):
                                    results[m["n"]].append({
                                        "source": "https://streamed.pk",
                                        "url": embed_url,
                                        "text": f"Streamed.pk Embed (HD: {st.get('hd', False)}, Lang: {st.get('language', 'Unknown')}) #{idx+1}"
                                    })
                                    print(f"   -> Match {m['n']} found player page (streamed.pk): {embed_url}")
                    except Exception as e:
                        print(f"Error fetching streamed.pk stream {s_name}/{s_id}:", e)

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

    # Load existing streams to preserve independently managed sources (like ppv.to)
    try:
        with open("../streams.json", "r", encoding="utf-8") as f:
            existing_streams = json.load(f)
    except Exception:
        existing_streams = {}

    results = {m["n"]: [] for m in recent_matches}
    for m in recent_matches:
        match_id_str = str(m["n"])
        if match_id_str in existing_streams:
            for r in existing_streams[match_id_str]:
                # Preserve ppv.to links
                if r.get("source") == "https://ppv.to":
                    results[m["n"]].append(r)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        
        # --- [CRITICAL TRAFFIC SAVER] Block heavy assets (images, videos, fonts, CSS) ---
        await context.route("**/*", lambda route: route.abort() 
            if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
            else route.continue_())

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

    # Call the streamed.pk API crawler
    fetch_streamed_pk_api(recent_matches, results)

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
        
        print("Committing to git...")
        subprocess.run(['git', 'config', '--local', 'user.name', 'github-actions[bot]'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
        
        status = subprocess.run(['git', 'status', '--porcelain', '../streams.json'], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(['git', 'add', '../streams.json'], check=True)
            subprocess.run(['git', 'commit', '-m', 'chore: auto update streaming URLs'], check=True)
            subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
            subprocess.run(['git', 'push'], check=True)
            print("Successfully pushed live streams.")
        else:
            print("No changes in streams.json, skipping commit.")
    except Exception as e:
        print(f"\nFailed to write to {output_path} or commit to git: {e}")

if __name__ == "__main__":
    asyncio.run(main())
