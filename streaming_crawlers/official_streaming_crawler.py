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

import subprocess
import random

def load_official_sources():
    # Use Node.js to evaluate sources.js and dump window.WC_SOURCES as JSON
    script = '''
    const fs = require("fs");
    const content = fs.readFileSync("../sources.js", "utf8");
    const window = {};
    eval(content);
    console.log(JSON.stringify(window.WC_SOURCES));
    '''
    try:
        result = subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print("Failed to load official sources via Node:", e)
        return {}

def load_proxies():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    webshare_file = "/Users/alex/Downloads/Webshare 5000 proxies (8).geo.json"
    free_file = os.path.join(base_dir, "..", "free_proxies.geo.json")
    
    all_proxies = []
    
    # Load Webshare proxies
    try:
        with open(webshare_file, "r", encoding="utf-8") as f:
            all_proxies.extend(json.load(f))
    except Exception as e:
        print("Failed to load Webshare proxies:", e)
        
    # Load Free proxies
    try:
        with open(free_file, "r", encoding="utf-8") as f:
            all_proxies.extend(json.load(f))
    except Exception as e:
        print("Failed to load free proxies:", e)

    # Group proxies by country code
    proxies_by_country = {}
    for p in all_proxies:
        cc = p.get("country_code")
        if cc:
            if cc not in proxies_by_country:
                proxies_by_country[cc] = []
            proxies_by_country[cc].append(p)
    return proxies_by_country

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

    official_sources_by_country = load_official_sources()
    proxies_by_country = load_proxies()
    
    # Flatten sources into a list of (country_code, url)
    test_urls = []
    for cc, sources in official_sources_by_country.items():
        for s in sources:
            test_urls.append((cc, s["url"]))
            
    # test_urls = test_urls[:5] # uncomment for quick local testing
    print(f"Testing all {len(test_urls)} official sources from sources.js...")

    results = {m["n"]: [] for m in recent_matches}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for cc, url in test_urls:
            print(f"\nScanning OFFICIAL: {url} (Target Country: {cc})")
            
            # Select a proxy for this country if available
            context_args = {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            
            country_proxies = proxies_by_country.get(cc, [])
            if country_proxies:
                proxy = random.choice(country_proxies)
                protocol = proxy.get("protocol", "http")
                
                proxy_config = {
                    "server": f"{protocol}://{proxy['proxy_ip']}:{proxy['proxy_port']}"
                }
                if proxy.get("proxy_username") and proxy.get("proxy_password"):
                    proxy_config["username"] = proxy['proxy_username']
                    proxy_config["password"] = proxy['proxy_password']
                    
                context_args["proxy"] = proxy_config
                print(f"   -> Using {protocol} proxy from {cc} ({proxy['proxy_ip']})")
            else:
                print(f"   -> No proxy found for {cc}, attempting without proxy...")
                
            context = await browser.new_context(**context_args)
            
            # --- [CRITICAL TRAFFIC SAVER] Block images, media, fonts, and stylesheets ---
            await context.route("**/*", lambda route: route.abort() 
                if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
                else route.continue_())
            
            page = await context.new_page()
            
            links = await fetch_links_from_site(page, url)
            await context.close()
            
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

    print("Committing to git...")
    subprocess.run(['git', 'config', '--local', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', '--local', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
    subprocess.run(['git', 'add', '../official_streams.json'], check=True)
    subprocess.run(['git', 'commit', '-m', 'chore: auto update official broadcaster links'], check=True)
    subprocess.run(['git', 'push'], check=True)

if __name__ == "__main__":
    asyncio.run(main())
