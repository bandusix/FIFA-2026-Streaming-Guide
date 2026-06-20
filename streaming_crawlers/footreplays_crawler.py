import re
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timedelta, timezone

COUNTRY_CODES = {
    "ar": ["argentina"], "at": ["austria"], "au": ["australia"], "ba": ["bosnia", "herzegovina"], 
    "be": ["belgium"], "br": ["brazil"], "ca": ["canada"], "cd": ["congo"], 
    "ch": ["switzerland"], "ci": ["ivory-coast", "cote", "ivory"], "co": ["colombia"], "cv": ["cape", "cabo"], 
    "cw": ["curacao"], "cz": ["czech"], "de": ["germany"], "dz": ["algeria"], 
    "ec": ["ecuador"], "eg": ["egypt"], "es": ["spain"], "fr": ["france"], 
    "gb-eng": ["england"], "gb-sct": ["scotland"], "gh": ["ghana"], "hr": ["croatia"], 
    "ht": ["haiti"], "iq": ["iraq"], "ir": ["iran"], "jo": ["jordan"], 
    "jp": ["japan"], "kr": ["south-korea", "korea"], "ma": ["morocco"], "mx": ["mexico"], 
    "nl": ["netherlands", "dutch"], "no": ["norway"], "nz": ["zealand"], "pa": ["panama"], 
    "pt": ["portugal"], "py": ["paraguay"], "qa": ["qatar"], "sa": ["saudi"], 
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

def get_slug(team_code):
    keywords = COUNTRY_CODES.get(team_code, [team_code])
    # The first keyword in our dict is the standard slug name for footreplays
    # except when it contains spaces, we replace with hyphens.
    # Our dict already uses hyphens for south-korea, united-states, etc.
    return keywords[0]

def verify_url_get(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        # Footreplays returns 200 for valid, 404 for invalid.
        # But we also read the title just to be completely sure.
        html = response.read(2000).decode('utf-8', errors='ignore')
        
        if response.status == 200 and "Full Match Replay" in html:
            return True
            
        return False
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        return False
    except Exception:
        return False

def main():
    print("Loading schedule for footreplays.com crawler...")
    all_matches = load_schedule()
    
    # We will check ALL matches in the schedule (from Match 1 on June 11 to the final).
    # If the match replay is not yet published on footreplays.com, it simply returns 404
    # and we skip it. This ensures we don't rely on the system clock or timezones,
    # and automatically supports all matches from June 11th onwards!
    target_matches = all_matches
                
    # Load existing streams database
    output_path = "../streams.json"
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            streams_db = json.load(f)
    except FileNotFoundError:
        print("streams.json not found, initializing empty database.")
        streams_db = {}
    
    print(f"\nGenerating and verifying footreplays.com links for all {len(target_matches)} matches...")
    added_count = 0
    for m in target_matches:
        home_slug = get_slug(m['h'])
        away_slug = get_slug(m['a'])
        date_str = m['d'].strftime("%d-%m-%Y")
        url = f"https://www.footreplays.com/international/world-cup-2026/{home_slug}-vs-{away_slug}-{date_str}/"
        
        match_id_str = str(m["n"])
        if match_id_str not in streams_db:
            streams_db[match_id_str] = []
            
        # Avoid checking if it already exists
        if any(r.get("url") == url for r in streams_db[match_id_str]):
            continue
            
        if verify_url_get(url):
            streams_db[match_id_str].append({
                "source": "https://www.footreplays.com",
                "url": url,
                "text": "Full Match Replay"
            })
            added_count += 1
            print(f"   -> Match {m['n']} verified footreplays stream: {url}")
        else:
            pass # print(f"   -> Match {m['n']} invalid URL: {url}")

    print(f"\nAdded {added_count} new footreplays.com streams.")
    
    # Save back to database
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
