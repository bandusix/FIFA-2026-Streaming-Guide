import re
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timedelta, timezone

# FIFA3 mapping from original live_streaming_crawler
FIFA3_ISO = {
    "MEX":"mx","RSA":"za","KOR":"kr","CZE":"cz","CAN":"ca","BIH":"ba","QAT":"qa",
    "SUI":"ch","BRA":"br","MAR":"ma","HAI":"ht","SCO":"gb-sct","USA":"us","PAR":"py",
    "AUS":"au","TUR":"tr","GER":"de","CUW":"cw","CIV":"ci","ECU":"ec","NED":"nl",
    "JPN":"jp","SWE":"se","TUN":"tn","IRN":"ir","NZL":"nz","BEL":"be","EGY":"eg",
    "ESP":"es","CPV":"cv","KSA":"sa","URU":"uy","FRA":"fr","SEN":"sn","IRQ":"iq",
    "NOR":"no","ARG":"ar","ALG":"dz","AUT":"at","JOR":"jo","POR":"pt","COD":"cd",
    "UZB":"uz","COL":"co","ENG":"gb-eng","CRO":"hr","GHA":"gh","PAN":"pa"
}
ISO_TO_FIFA3 = {v: k.lower() for k, v in FIFA3_ISO.items()}

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

def verify_url_get(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        html = response.read(1000).decode('utf-8', errors='ignore')
        
        if "404" in html or "Not Found" in html or "not exist" in html.lower():
            return False
            
        return True
    except Exception:
        return False

def main():
    print("Loading schedule for ppv.to crawler...")
    all_matches = load_schedule()
    recent_matches = get_recent_matches(all_matches)
    
    if not recent_matches:
        print("No matches within the window found. Forcing 'now' for testing...")
        forced_now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
        for m in all_matches:
            diff = m["d"] - forced_now
            if diff >= timedelta(hours=-24):
                recent_matches.append(m)
                
    # Load existing streams database
    output_path = "../streams.json"
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            streams_db = json.load(f)
    except FileNotFoundError:
        print("streams.json not found, initializing empty database.")
        streams_db = {}
    
    print("\nGenerating and verifying ppv.to links ...")
    added_count = 0
    for m in recent_matches:
        home3 = ISO_TO_FIFA3.get(m['h'], m['h'])
        away3 = ISO_TO_FIFA3.get(m['a'], m['a'])
        date_str = m['d'].strftime("%Y-%m-%d")
        url = f"https://old.ppv.to/live/wc/{date_str}/{home3}-{away3}"
        
        match_id_str = str(m["n"])
        if match_id_str not in streams_db:
            streams_db[match_id_str] = []
            
        if verify_url_get(url):
            # Check if already exists to avoid duplicates
            if not any(r.get("url") == url for r in streams_db[match_id_str]):
                streams_db[match_id_str].append({
                    "source": "https://ppv.to",
                    "url": url,
                    "text": "PPV.to Live Stream"
                })
                added_count += 1
                print(f"   -> Match {m['n']} verified ppv.to stream: {url}")
        else:
            pass # Keep output clean

    print(f"\nAdded {added_count} new ppv.to streams.")
    
    # Save back to database
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(streams_db, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated streams data in {output_path}")
        
        print("Committing ppv.to streams to git...")
        subprocess.run(['git', 'config', '--local', 'user.name', 'github-actions[bot]'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
        
        # Check if there are any changes to commit
        status = subprocess.run(['git', 'status', '--porcelain', '../streams.json'], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(['git', 'add', '../streams.json'], check=True)
            subprocess.run(['git', 'commit', '-m', 'chore: auto update ppv.to streaming URLs'], check=True)
            # Fetch and rebase to avoid conflicts
            subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
            subprocess.run(['git', 'push'], check=True)
            print("Successfully pushed ppv.to streams.")
        else:
            print("No changes in streams.json, skipping commit.")
            
    except Exception as e:
        print(f"\nFailed to update {output_path} or git: {e}")

if __name__ == "__main__":
    main()
