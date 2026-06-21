const fs = require('fs');

// 1. Read matches.js
let matchesJs = fs.readFileSync('matches.js', 'utf8');
// Remove the const W, R, TH, ET declarations from matchesJs to avoid redeclaration in eval
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

// 2. Read index.html to extract LANGS
const html = fs.readFileSync('index.html', 'utf8');
const langMatch = html.match(/const LANGS = \[([\s\S]*?)\];/);
let langCodes = [];
if (langMatch) {
    const matches = langMatch[1].matchAll(/\["([^"]+)"/g);
    for (const m of matches) {
        langCodes.push(m[1]);
    }
} else {
    console.error("Could not extract LANGS from index.html");
    process.exit(1);
}

function getTeamSlug(t) {
    if (typeof t === 'string') return t.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
    if (typeof t === 'object' && t.k) return t.k + '-' + t.g;
    return 'tbd';
}

const baseUrl = "https://fifa-2026-streaming-guide.vercel.app/";
const urls = [];

urls.push(`<url><loc>${baseUrl}</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>`);

for (const lang of langCodes) {
    urls.push(`<url><loc>${baseUrl}?lang=${lang}</loc><changefreq>hourly</changefreq><priority>0.9</priority></url>`);
}

for (const m of M) {
    const homeSlug = getTeamSlug(m.h);
    const awaySlug = getTeamSlug(m.a);
    // e.g. 1-mx-vs-za
    const matchSlug = `${m.n}-${homeSlug}-vs-${awaySlug}`;
    
    urls.push(`<url><loc>${baseUrl}?match=${matchSlug}</loc><changefreq>daily</changefreq><priority>0.8</priority></url>`);
    for (const lang of langCodes) {
        urls.push(`<url><loc>${baseUrl}?lang=${lang}&amp;match=${matchSlug}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>`);
    }
}

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join('\n')}
</urlset>`;

fs.writeFileSync('sitemap.xml', xml, 'utf8');
console.log(`Sitemap generated successfully! Total URLs: ${urls.length}`);
