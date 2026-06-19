import re
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timedelta, timezone

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

def verify_url_get(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        html = response.read(1000).decode('utf-8', errors='ignore')
        
        # Note: livsports is a SPA, so we might need to check if the response is valid 
        # But since we get the ID directly from the API, the URL will be valid as long as the ID is correct.
        if "404" in html or "Not Found" in html or "not exist" in html.lower():
            return False
            
        return True
    except Exception:
        return False

def main():
    print("Loading schedule for livsports.dpdns.org crawler...")
    all_matches = load_schedule()
    recent_matches = get_recent_matches(all_matches)
    
    if not recent_matches:
        print("No matches within the window found. Forcing 'now' for testing...")
        forced_now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
        for m in all_matches:
            diff = m["d"] - forced_now
            if diff >= timedelta(hours=-24):
                recent_matches.append(m)

    # Fetch from the upstream API directly
    print("\nFetching data from upstream API (https://streamed.pk/api/matches/football)...")
    api_matches = []
    try:
        req = urllib.request.Request("https://streamed.pk/api/matches/football", headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req).read().decode('utf-8')
        api_matches = json.loads(data)
    except Exception as e:
        print("Error fetching upstream API:", e)

    # Load existing streams database
    output_path = "../streams.json"
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            streams_db = json.load(f)
    except FileNotFoundError:
        print("streams.json not found, initializing empty database.")
        streams_db = {}
    
    added_count = 0
    for m in recent_matches:
        match_id_str = str(m["n"])
        if match_id_str not in streams_db:
            streams_db[match_id_str] = []

        for api_m in api_matches:
            title = api_m.get('title', '')
            if matches_team(title, m["h"]) and matches_team(title, m["a"]):
                # Found the match in API, extract the ID
                stream_id = api_m.get('id')
                if stream_id:
                    url = f"https://livsports.dpdns.org/match?id={stream_id}&cat=football"
                    
                    if verify_url_get(url):
                        if not any(r.get("url") == url for r in streams_db[match_id_str]):
                            streams_db[match_id_str].append({
                                "source": "https://livsports.dpdns.org",
                                "url": url,
                                "text": "Livsports Web Player"
                            })
                            added_count += 1
                            print(f"   -> Match {m['n']} verified livsports stream: {url}")
                    else:
                        print(f"   -> Match {m['n']} invalid URL: {url}")

    print(f"\nAdded {added_count} new livsports.dpdns.org streams.")
    
    # Save back to database
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(streams_db, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated streams data in {output_path}")
        
        print("Committing livsports streams to git...")
        subprocess.run(['git', 'config', '--local', 'user.name', 'github-actions[bot]'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
        
        # Check if there are any changes to commit
        status = subprocess.run(['git', 'status', '--porcelain', '../streams.json'], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(['git', 'add', '../streams.json'], check=True)
            subprocess.run(['git', 'commit', '-m', 'chore: auto update livsports.dpdns.org URLs'], check=True)
            subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
            subprocess.run(['git', 'push'], check=True)
            print("Successfully pushed livsports streams.")
        else:
            print("No changes in streams.json, skipping commit.")
            
    except Exception as e:
        print(f"\nFailed to update {output_path} or git: {e}")

if __name__ == "__main__":
    main()