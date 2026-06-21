import re
import json

def generate_sitemap():
    # 1. Parse LANGS from index.html
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    lang_match = re.search(r"const LANGS = \[(.*?)\];", html, re.DOTALL)
    if not lang_match:
        print("Could not find LANGS in index.html")
        return
        
    lang_codes = re.findall(r"\[\"([^\"]+)\",", lang_match.group(1))
    
    # 2. Extract match IDs from matches.js (we know there are 104 matches, let's parse them safely)
    with open("matches.js", "r", encoding="utf-8") as f:
        matches_js = f.read()
        
    # Matches are in an array: const M = [ {n: 1, ...}, ... ]
    match_numbers = re.findall(r"\{n:\s*(\d+)", matches_js)
    
    print(f"Found {len(lang_codes)} languages and {len(match_numbers)} matches.")
    
    # 3. Generate XML
    urls = []
    base_url = "https://fifa-2026-streaming-guide.vercel.app/"
    
    # Add root URL
    urls.append(f"<url><loc>{base_url}</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>")
    
    # Add language root URLs
    for lang in lang_codes:
        urls.append(f"<url><loc>{base_url}?lang={lang}</loc><changefreq>hourly</changefreq><priority>0.9</priority></url>")
        
    # Add Match x Language URLs (SITEMAP EXPLOSION)
    for match_id in match_numbers:
        # Default english route
        urls.append(f"<url><loc>{base_url}?match={match_id}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>")
        
        # Localized routes
        for lang in lang_codes:
            # ?lang=xx&match=YY
            url = f"{base_url}?lang={lang}&amp;match={match_id}"
            urls.append(f"<url><loc>{url}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>")
            
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>"""

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    print(f"Sitemap generated successfully! Total URLs: {len(urls)}")

if __name__ == "__main__":
    generate_sitemap()
