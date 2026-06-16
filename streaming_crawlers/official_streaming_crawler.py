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

def load_schedule():
    with open("../matches.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'window\.WC_MATCHES\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not match: return []
    matches_str = match.group(1)
    
    parsed_matches = []
    for line in matches_str.split('\n'):
        if '{n:' in line:
            n_match = re.search(r'n:(\d+)', line)
            d_match = re.search(r'd:"([^"]+)"', line)
            h_match = re.search(r'h:"([^"]+)"', line)
            a_match = re.search(r'a:"([^"]+)"', line)
            
            if n_match and d_match and h_match and a_match:
                dt_str = d_match.group(1) + "-04:00"
                dt = datetime.fromisoformat(dt_str)
                parsed_matches.append({
                    "n": int(n_match.group(1)),
                    "d": dt,
                    "h": h_match.group(1),
                    "a": a_match.group(1)
                })
    return parsed_matches

def load_official_sources():
    with open("../sources.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract window.WC_SOURCES dictionary
    match = re.search(r'window\.WC_SOURCES\s*=\s*(\{.*?\});', content, re.DOTALL)
    if not match: return []
    
    sources_str = match.group(1)
    # Extract all urls from the block using regex
    urls = set(re.findall(r'url:"([^"]+)"', sources_str))
    
    # We might want to just test a subset for local testing to avoid 100+ browsers
    # or just return all unique URLs
    return list(urls)

def get_recent_matches(matches):
    now = datetime.now(timezone.utc)
    recent = []
    for m in matches:
        diff = m["d"] - now
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
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Scroll to load lazy content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        
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
        print("Forcing 'now' to 2026-06-15 12:00:00 UTC for testing...")
        forced_now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
        for m in all_matches:
            diff = m["d"] - forced_now
            if diff >= timedelta(hours=-24):
                recent_matches.append(m)

    official_urls = load_official_sources()
    print(f"Testing all {len(official_urls)} official sources from sources.js...")
    test_urls = official_urls

    results = {m["n"]: [] for m in recent_matches}
    
    # 代理配置占位，等待用户提供真实代理
    proxy_config = None
    # proxy_config = {
    #     "server": "http://IP:PORT",
    #     "username": "YOUR_USERNAME",
    #     "password": "YOUR_PASSWORD"
    # }
    
    async with async_playwright() as p:
        # 如果有代理则带上代理启动 Chromium
        launch_args = {"headless": True}
        if proxy_config:
            launch_args["proxy"] = proxy_config
            print(f"Launching browser with proxy: {proxy_config['server']}")
            
        browser = await p.chromium.launch(**launch_args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        
        for url in test_urls:
            print(f"\nScanning OFFICIAL: {url} ...")
            page = await context.new_page()
            links = await fetch_links_from_site(page, url)
            await page.close()
            
            for m in recent_matches:
                for link in links:
                    href = link["href"]
                    text = link["text"]
                    combined = f"{href} {text}"
                    
                    if matches_team(combined, m["h"]) and matches_team(combined, m["a"]):
                        if not any(r["url"] == href for r in results[m["n"]]):
                            results[m["n"]].append({
                                "source": url,
                                "url": href,
                                "text": text.replace('\n', ' ').strip()
                            })
                            print(f"   -> Match {m['n']} found official player page: {href}")

        await browser.close()
        
    print("\n\n=== OFFICIAL AGGREGATED LINKS ===")
    for m in recent_matches:
        h_name = COUNTRY_CODES.get(m['h'], [m['h']])[0].title()
        a_name = COUNTRY_CODES.get(m['a'], [m['a']])[0].title()
        if results[m["n"]]:
            print(f"\nMatch {m['n']} | {h_name} vs {a_name}")
            for r in results[m["n"]]:
                print(f"  [Official Source: {r['source']}] {r['url']}")
            
    # Optionally append to streams.json or create official_streams.json
    output_path = "../official_streams.json"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully wrote official streams data to {output_path}")
    except Exception as e:
        print(f"\nFailed to write to {output_path}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
