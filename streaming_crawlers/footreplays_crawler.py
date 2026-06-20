import re
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timedelta, timezone

COUNTRY_CODES = {
    "ar": ["argentina"], "at": ["austria"], "au": ["australia"], "ba": ["bosnia", "herzegovina"], 
    "be": ["belgium"], "br": ["brazil"], "ca": ["canada"], "cd": ["congo"], 
    "ch": ["switzerland"], "ci": ["ivory-coast", "cote", "ivory"], "co": ["colombia"], "cv": ["cape", "cabo", "verde"], 
    "cw": ["curacao"], "cz": ["czech", "republic"], "de": ["germany"], "dz": ["algeria"], 
    "ec": ["ecuador"], "eg": ["egypt"], "es": ["spain"], "fr": ["france"], 
    "gb-eng": ["england"], "gb-sct": ["scotland"], "gh": ["ghana"], "hr": ["croatia"], 
    "ht": ["haiti"], "iq": ["iraq"], "ir": ["iran"], "jo": ["jordan"], 
    "jp": ["japan"], "kr": ["south-korea", "korea"], "ma": ["morocco"], "mx": ["mexico"], 
    "nl": ["netherlands", "dutch"], "no": ["norway"], "nz": ["zealand", "new-zealand"], "pa": ["panama"], 
    "pt": ["portugal"], "py": ["paraguay"], "qa": ["qatar"], "sa": ["saudi", "arabia"], 
    "se": ["sweden"], "sn": ["senegal"], "tn": ["tunisia"], "tr": ["turkey", "turkiye"], 
    "us": ["united-states", "usa", "america"], "uy": ["uruguay"], "uz": ["uzbekistan"], "za": ["south-africa", "rsa"]
}

def load_schedule():
    with open("../matches.js", "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'window\.WC_MATCHES\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not match:
        return []
    
    matches_str = match.group(1)
    parsed_matches = []
    for line in matches_str.split('\n'):
        if '{n:' in line:
            n_match = re.search(r'n:(\d+)', line)
            d_match = re.search(r'd:"([^"]+)"', line)
            h_match = re.search(r'h:"([^"]+)"', line)
            a_match = re.search(r'a:"([^"]+)"', line)
            
            if n_match and h_match and a_match:
                parsed_matches.append({
                    "n": int(n_match.group(1)),
                    "h": h_match.group(1),
                    "a": a_match.group(1)
                })
    return parsed_matches

def extract_slugs_from_url(url):
    # url looks like: https://www.footreplays.com/international/world-cup-2026/mexico-vs-south-korea-19-06-2026/
    match = re.search(r'/world-cup-2026/([a-z0-9\-]+)-vs-([a-z0-9\-]+?)(?:-\d{2}-\d{2}-\d{4})?/?$', url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def match_teams_to_id(team1_slug, team2_slug, schedule):
    # Reverse lookup slug to fifa code
    def find_code(slug):
        for code, keywords in COUNTRY_CODES.items():
            for kw in keywords:
                if kw in slug or slug in kw:
                    return code
        return None
        
    t1_code = find_code(team1_slug)
    t2_code = find_code(team2_slug)
    
    if not t1_code or not t2_code:
        return None
        
    # Find match in schedule
    for m in schedule:
        if (m['h'] == t1_code and m['a'] == t2_code) or (m['h'] == t2_code and m['a'] == t1_code):
            return str(m['n'])
    return None

def fetch_page_urls(page_num):
    url = f"https://www.footreplays.com/international/world-cup-2026/page/{page_num}/" if page_num > 1 else "https://www.footreplays.com/international/world-cup-2026/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, timeout=10)
        if response.status == 200:
            html = response.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href="(https://www\.footreplays\.com/international/world-cup-2026/[^"]+)"', html)
            # Filter out pagination or category links
            return list(set([l for l in links if '-vs-' in l]))
    except Exception:
        pass
    return []

def main():
    print("Loading schedule for footreplays.com crawler...")
    schedule = load_schedule()
    
    output_path = "../streams.json"
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            streams_db = json.load(f)
    except FileNotFoundError:
        print("streams.json not found, initializing empty database.")
        streams_db = {}
        
    print("\nCrawling footreplays.com pages for actual links...")
    all_found_links = set()
    for page in range(1, 10):
        print(f"Scraping page {page}...")
        links = fetch_page_urls(page)
        if not links:
            break
        all_found_links.update(links)
        
    added_count = 0
    for link in all_found_links:
        t1, t2 = extract_slugs_from_url(link)
        if not t1 or not t2:
            continue
            
        match_id = match_teams_to_id(t1, t2, schedule)
        if match_id:
            if match_id not in streams_db:
                streams_db[match_id] = []
            
            # Avoid duplicate URLs
            if any(r.get("url") == link for r in streams_db[match_id]):
                continue
                
            streams_db[match_id].append({
                "source": "https://www.footreplays.com",
                "url": link,
                "text": "Full Match Replay"
            })
            added_count += 1
            print(f"   -> Match {match_id} mapped to real URL: {link}")

    print(f"\nAdded {added_count} new footreplays.com streams.")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(streams_db, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated streams data in {output_path}")
        
        print("Committing footreplays streams to git...")
        subprocess.run(['git', 'config', '--local', 'user.name', 'github-actions[bot]'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
        
        status = subprocess.run(['git', 'status', '--porcelain', '../streams.json'], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(['git', 'add', '../streams.json'], check=True)
            subprocess.run(['git', 'commit', '-m', 'chore: auto update footreplays.com URLs'], check=True)
            subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
            subprocess.run(['git', 'push'], check=True)
            print("Successfully pushed footreplays streams.")
        else:
            print("No changes in streams.json, skipping commit.")
            
    except Exception as e:
        print(f"\nFailed to update {output_path} or git: {e}")

if __name__ == "__main__":
    main()
