import json
import urllib.request
import datetime
from datetime import timezone
import subprocess
import sys
import os

API_URL = "https://api.fifa.com/api/v3/calendar/matches?idSeason=285023&count=500"

alpha3_to_alpha2 = {
    'ALG': 'dz', 'ARG': 'ar', 'AUS': 'au', 'AUT': 'at', 'BEL': 'be', 'BIH': 'ba',
    'BRA': 'br', 'CAN': 'ca', 'CIV': 'ci', 'COD': 'cd', 'COL': 'co', 'CPV': 'cv',
    'CRO': 'hr', 'CUW': 'cw', 'CZE': 'cz', 'ECU': 'ec', 'EGY': 'eg', 'ENG': 'gb-eng',
    'ESP': 'es', 'FRA': 'fr', 'GER': 'de', 'GHA': 'gh', 'HAI': 'ht', 'IRN': 'ir',
    'IRQ': 'iq', 'JOR': 'jo', 'JPN': 'jp', 'KOR': 'kr', 'KSA': 'sa', 'MAR': 'ma',
    'MEX': 'mx', 'NED': 'nl', 'NOR': 'no', 'NZL': 'nz', 'PAN': 'pa', 'PAR': 'py',
    'POR': 'pt', 'QAT': 'qa', 'RSA': 'za', 'SCO': 'gb-sct', 'SEN': 'sn', 'SUI': 'ch',
    'SWE': 'se', 'TUN': 'tn', 'TUR': 'tr', 'URU': 'uy', 'USA': 'us', 'UZB': 'uz'
}

city_map = {
    'New Jersey': 'East Rutherford',
    'San Francisco Bay Area': 'Santa Clara',
    'Guadalajara': 'Zapopan',
    'Dallas': 'Arlington',
    'Los Angeles': 'Inglewood',
    'Monterrey': 'Guadalupe',
    'Miami': 'Miami Gardens',
    'Boston': 'Foxborough'
}

def parse_placeholder(ph):
    if not ph: return None
    if ph.startswith('1') and len(ph) == 2:
        return f'W("{ph[1]}")'
    if ph.startswith('2') and len(ph) == 2:
        return f'R("{ph[1]}")'
    if ph.startswith('3'):
        groups = "/".join(list(ph[1:]))
        return f'TH("{groups}")'
    return None

def fetch_data():
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def generate_matches_js(results, today_str):
    lines = []
    lines.append('/* ============================================================')
    lines.append('   FIFA World Cup 2026 — FIXTURE DATA  (auto-corrected daily)')
    lines.append('   ------------------------------------------------------------')
    lines.append('   This file is the SINGLE SOURCE OF TRUTH for match data and is')
    lines.append('   the ONLY file the daily verification routine should edit.')
    lines.append('   See RUNBOOK.md for the update procedure and UPDATE_LOG.md for')
    lines.append('   the change history.')
    lines.append('')
    lines.append('   Time convention: every kickoff is stored as the US Eastern')
    lines.append('   (EDT, UTC-4) wall-clock with the "-04:00" suffix, i.e. the')
    lines.append('   true instant. index.html converts it to each visitor\'s zone.')
    lines.append('')
    lines.append('   Match object shape:')
    lines.append('     {n, g|r, d, c, h, a, s?}')
    lines.append('       n = match number (1-104)')
    lines.append('       g = group letter "A".."L"   OR   r = round key')
    lines.append('           (r32, r16, qf, sf, tp, final)')
    lines.append('       d = ISO datetime with -04:00 offset')
    lines.append('       c = host city (maps to a stadium in index.html V{})')
    lines.append('       h = home team   a = away team')
    lines.append('           - group stage: ISO flag code (e.g. "br", "gb-eng")')
    lines.append('           - knockout:    slot object via W()/R()/TH(), or omit for TBD')
    lines.append('       s = [home, away] score  (only for finished matches)')
    lines.append('   ============================================================ */')
    lines.append('')
    lines.append(f'// ISO date (YYYY-MM-DD) of the last successful verification against official sources.')
    lines.append(f'window.WC_LAST_VERIFIED = "{today_str}";')
    lines.append('')
    lines.append('// Knockout placeholder builders + US Eastern offset constant.')
    lines.append('const W = g => ({ k: "winner", g });')
    lines.append('const R = g => ({ k: "runner", g });')
    lines.append('const TH = g => ({ k: "third", g });')
    lines.append('const ET = "-04:00";')
    lines.append('')
    lines.append('window.WC_MATCHES = [')

    for i, m in enumerate(results):
        n = m['MatchNumber']

        stage_desc = m['StageName'][0]['Description'] if m.get('StageName') else ""
        group_desc = m['GroupName'][0]['Description'] if m.get('GroupName') else ""

        is_group = "Group" in group_desc or "Group" in stage_desc

        g_or_r = ""
        if is_group:
            grp_letter = group_desc.replace("Group ", "")
            if not grp_letter and "Group" in stage_desc:
                grp_letter = stage_desc.replace("Group ", "")
            g_or_r = f'g:"{grp_letter}"'
        else:
            if "32" in stage_desc: r_val = "r32"
            elif "16" in stage_desc: r_val = "r16"
            elif "Quarter" in stage_desc or "quarter" in stage_desc: r_val = "qf"
            elif "Semi" in stage_desc or "semi" in stage_desc: r_val = "sf"
            elif "Third" in stage_desc or "third" in stage_desc: r_val = "tp"
            elif "Final" in stage_desc or "final" in stage_desc: r_val = "final"
            else: r_val = "unknown"
            g_or_r = f'r:"{r_val}"'

        dt = datetime.datetime.strptime(m['Date'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        dt_edt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
        d_str = dt_edt.strftime("%Y-%m-%dT%H:%M:%S")
        d_val = f'd:"{d_str}"+ET'

        city_raw = m['Stadium']['CityName'][0]['Description']
        c_val = city_map.get(city_raw, city_raw)

        h_val = None
        a_val = None
        s_val = None

        if m.get('Home') and m['Home'].get('IdCountry'):
            h_val = f'"{alpha3_to_alpha2[m["Home"]["IdCountry"]]}"'
        if m.get('Away') and m['Away'].get('IdCountry'):
            a_val = f'"{alpha3_to_alpha2[m["Away"]["IdCountry"]]}"'

        if not h_val and m.get('PlaceHolderA'):
            h_val = parse_placeholder(m['PlaceHolderA'])
        if not a_val and m.get('PlaceHolderB'):
            a_val = parse_placeholder(m['PlaceHolderB'])

        if m.get('HomeTeamScore') is not None and m.get('AwayTeamScore') is not None:
            s_val = f"[{m['HomeTeamScore']},{m['AwayTeamScore']}]"

        parts = [f"n:{n}", g_or_r, d_val, f'c:"{c_val}"']
        if h_val: parts.append(f"h:{h_val}")
        if a_val: parts.append(f"a:{a_val}")
        if s_val: parts.append(f"s:{s_val}")

        comma = "," if i < len(results) - 1 else ""
        lines.append(" {" + ",".join(parts) + "}" + comma)

    lines.append('];')
    return '\n'.join(lines) + '\n'

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Fetching latest FIFA data...")
    data = fetch_data()
    results = sorted(data.get('Results', []), key=lambda x: x['MatchNumber'])
    
    today_str = datetime.datetime.now(timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d")
    
    new_content = generate_matches_js(results, today_str)
    
    with open('matches.js', 'r') as f:
        old_content = f.read()
        
    if new_content == old_content:
        print("No changes in matches.js. Exiting.")
        sys.exit(0)
        
    with open('matches.js', 'w') as f:
        f.write(new_content)
        
    # Check what changed using git diff
    diff = subprocess.run(['git', 'diff', 'matches.js'], capture_output=True, text=True).stdout
    if not diff.strip():
        print("No actual changes after git diff. Exiting.")
        sys.exit(0)
        
    # Append to UPDATE_LOG.md
    print("Changes detected, updating log...")
    log_entry = f"\n### {today_str}\n- Auto-updated match schedule/scores from FIFA API.\n"
    with open('UPDATE_LOG.md', 'a') as f:
        f.write(log_entry)
        
    print("Committing to git...")
    subprocess.run(['git', 'add', 'matches.js', 'UPDATE_LOG.md'], check=True)
    subprocess.run(['git', 'commit', '-m', 'chore: auto update schedule data'], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("Successfully updated and pushed.")

if __name__ == "__main__":
    main()
