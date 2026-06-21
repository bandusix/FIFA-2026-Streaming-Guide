const fs = require('fs');

// Extract matches from matches.js
let matchesJs = fs.readFileSync('matches.js', 'utf8');
matchesJs = matchesJs.replace(/const W = [\s\S]*?const ET = "-04:00";/g, '');
let M = [];
const sandbox = {
    window: {},
    W: g => ({ k: "winner", g }),
    R: g => ({ k: "runner", g }),
    TH: g => ({ k: "third", g }),
    ET: "-04:00"
};
try {
    const fn = new Function('window', 'W', 'R', 'TH', 'ET', matchesJs + '; return window.WC_MATCHES;');
    M = fn(sandbox.window, sandbox.W, sandbox.R, sandbox.TH, sandbox.ET);
} catch (e) {
    console.error("Error evaluating matches.js:", e);
    process.exit(1);
}

// Read index.html to extract LANGS and NAME_OVERRIDE
const html = fs.readFileSync('index.html', 'utf8');
const langMatch = html.match(/const LANGS = \[([\s\S]*?)\];/);
let langCodes = [];
if (langMatch) {
    const matches = langMatch[1].matchAll(/\["([^"]+)"/g);
    for (const m of matches) {
        langCodes.push(m[1]);
    }
}

// Extract NAME_OVERRIDE
let NAME_OVERRIDE = {};
const overrideMatch = html.match(/const NAME_OVERRIDE = (\{[\s\S]*?\});/);
if (overrideMatch) {
    try {
        const fn = new Function('return ' + overrideMatch[1]);
        NAME_OVERRIDE = fn();
    } catch(e) {
        console.error("Error parsing NAME_OVERRIDE:", e);
    }
}

let dnCache = {};
function countryName(code, lang) {
    if (NAME_OVERRIDE[code]) return NAME_OVERRIDE[code][lang] || NAME_OVERRIDE[code].en;
    try {
        if (!dnCache[lang]) dnCache[lang] = new Intl.DisplayNames([lang], { type: "region" });
        return dnCache[lang].of(code.toUpperCase()) || code.toUpperCase();
    } catch (e) { }
    return code.toUpperCase();
}

function getTeamName(t, lang) {
    if (typeof t === 'string') return countryName(t, lang);
    if (typeof t === 'object' && t.k) return t.k + '-' + t.g;
    return 'tbd';
}

function slugify(text) {
    return encodeURIComponent(text.replace(/\s+/g, '-'));
}

const baseUrl = "https://fifa-2026-streaming-guide.vercel.app/";
const urls = [];

urls.push(`<url><loc>${baseUrl}</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>`);

for (const lang of langCodes) {
    urls.push(`<url><loc>${baseUrl}?lang=${lang}</loc><changefreq>hourly</changefreq><priority>0.9</priority></url>`);
}

for (const m of M) {
    // English default slug for the global match route without lang
    const homeEn = getTeamName(m.h, 'en');
    const awayEn = getTeamName(m.a, 'en');
    const matchSlugEn = `${m.n}-${slugify(homeEn)}-vs-${slugify(awayEn)}`;
    
    urls.push(`<url><loc>${baseUrl}?match=${matchSlugEn}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>`);
    
    for (const lang of langCodes) {
        const homeLoc = getTeamName(m.h, lang);
        const awayLoc = getTeamName(m.a, lang);
        // Include ISO codes + Localized Names + 'vs' translated or just '-vs-'
        const matchSlugLoc = `${m.n}-${slugify(homeLoc)}-vs-${slugify(awayLoc)}`;
        
        urls.push(`<url><loc>${baseUrl}?lang=${lang}&amp;match=${matchSlugLoc}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>`);
    }
}

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>`;

fs.writeFileSync('sitemap.xml', xml, 'utf8');
console.log(`Sitemap generated successfully! Total URLs: ${urls.length}`);
