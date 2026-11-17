#!/usr/bin/env python3
"""Builds the Pandapi Tools static pages: python3 build.py
Each tool lives in <slug>/ (convert.js + app.js); this script writes <slug>/index.html and index.html
from the definitions below so the header, footer, SEO tags and FAQ markup stay identical everywhere.
Set SITE_URL once the site has its public address (canonical links, sitemap)."""
import html
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")  # e.g. https://riaa3102.github.io/pandapi-tools
APIFY = "https://apify.com/blueberry_rainstorm/"
E = html.escape

TOOLS = [
    {
        "slug": "html-to-markdown",
        "name": "HTML to Markdown",
        "title": "HTML to Markdown Converter (free, private, main content only)",
        "h1": "HTML to Markdown converter",
        "description": "Convert HTML to clean Markdown in your browser. Keep only the main content, paste straight from a web page, batch-convert files to a .zip. Free, no sign-up, nothing uploaded.",
        "lede": "Paste HTML or copy part of any web page and paste it here. You get clean GitHub-flavored Markdown with tables, code blocks and links. Turn on <b>main content only</b> to drop menus, footers and cookie banners.",
        "badges": ["Runs in your browser", "Main content only", "Paste from any page", "Batch to .zip", "Free, no sign-up"],
        "icon": "tool-html-to-markdown.png",
        "scripts": ["../vendor/turndown.js", "../vendor/turndown-plugin-gfm.js", "../vendor/readability.js", "../vendor/fflate.js", "convert.js", "app.js"],
        "upsell_icon": "web-page-to-markdown.png",
        "upsell": "Need whole websites as Markdown, for RAG or an AI agent? <b>Web Page to Markdown</b> crawls URLs or sitemaps, renders JavaScript pages and returns clean, chunked Markdown through an API. About $1 per 1,000 pages.",
        "upsell_url": APIFY + "web-page-to-markdown",
        "upsell_cta": "See the Web Page to Markdown API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="html-in">HTML</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="html-in" spellcheck="false" placeholder="Paste HTML here, or copy part of a web page and paste it (formatting is kept)."></textarea>
    <div class="opts" role="group" aria-label="Options">
      <label><input type="checkbox" id="opt-main" checked> Main content only</label>
      <label><input type="checkbox" id="opt-rich" checked> Paste keeps formatting</label>
      <label><input type="checkbox" id="opt-noimg"> Drop images</label>
      <label><input type="checkbox" id="opt-reflinks"> Reference-style links</label>
      <label><input type="checkbox" id="opt-fm"> YAML front matter</label>
      <label>Page URL <input type="text" id="opt-base" placeholder="https://example.com/page" size="22" aria-label="Page URL, used to fix relative links"></label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2><label for="md-out">Markdown</label></h2><span class="status" id="stats" aria-live="polite"></span></div>
    <textarea id="md-out" spellcheck="false" readonly placeholder="Markdown appears here as you type."></textarea>
    <div class="row"><button type="button" id="btn-copy">Copy</button><button type="button" class="secondary" id="btn-download">Download .md</button></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </div>
</div>
<div class="card" style="margin-top:16px">
  <div class="pane-head"><h2>Convert many files at once</h2></div>
  <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose HTML files to convert"><strong>Drop .html files here</strong> or click to choose. You get one .zip of .md files, made with the options above.</div>
  <input type="file" id="file-in" accept=".html,.htm,.xhtml,text/html" multiple hidden>
  <p class="status" id="batch-status" role="status" aria-live="polite"></p>
  <ul class="files" id="batch-list"></ul>
</div>
<script type="text/plain" id="sample-html"><!doctype html><html><head><title>How to brew pour-over coffee</title></head><body>
<header><nav><a href="/">Home</a> <a href="/shop">Shop</a> <a href="/blog">Blog</a></nav></header>
<div class="cookie-banner">We use cookies. <button>Accept</button></div>
<main><article><h1>How to brew pour-over coffee</h1>
<p>Pour-over gives you a <strong>clean, bright cup</strong>. You need a dripper, a filter and a kettle. This guide takes about <em>four minutes</em>, and you can read more in our <a href="/guides/grind">grind size guide</a>.</p>
<h2>What you need</h2><ul><li>20 g of coffee, medium-fine</li><li>320 g of water at 94 °C</li><li>A paper filter, rinsed</li></ul>
<h2>Ratios</h2><table><thead><tr><th>Cups</th><th>Coffee</th><th>Water</th></tr></thead><tbody><tr><td>1</td><td>20 g</td><td>320 g</td></tr><tr><td>2</td><td>36 g</td><td>580 g</td></tr></tbody></table>
<h2>Timer script</h2><pre><code class="language-python">for step, seconds in [("bloom", 45), ("pour", 90)]:
    print(step, seconds)</code></pre>
<blockquote>Tip: grind just before you brew.</blockquote></article></main>
<aside><h3>Related posts</h3><a href="/a">French press</a></aside>
<footer>© 2026 Example Coffee · <a href="/privacy">Privacy</a></footer></body></html></script>
""",
        "howto": [
            "Paste HTML into the left box, or copy part of a web page (Ctrl+C) and paste it there: the formatting comes over, not just the text.",
            "Leave <b>Main content only</b> on for whole pages. It keeps the article and drops navigation, sidebars, footers, cookie banners and ads.",
            "Add the page URL if the HTML has relative links, so links and images point to the right place.",
            "Copy the Markdown or download it as a .md file. For many files, drop them in the batch box and get a .zip.",
        ],
        "faq": [
            ("Is my HTML uploaded anywhere?", "No. The conversion runs in your browser with open-source libraries (Turndown and Mozilla Readability). Nothing you paste or drop leaves your device, and the page works offline once it has loaded."),
            ("What does \"main content only\" do?", "It uses Mozilla's Readability, the same engine as Firefox Reader View, to find the article in a full page and drop menus, footers, sidebars, cookie banners and ads. Snippets are converted as they are."),
            ("Which Markdown flavor do I get?", "GitHub-flavored Markdown: # headings, - lists, ``` fenced code blocks with the language kept, pipe tables, ~~strikethrough~~ and task lists. Tables with merged cells stay as HTML, because Markdown tables can't merge cells."),
            ("Is this good for ChatGPT, Claude or a RAG pipeline?", "Yes. Markdown keeps the structure that models use, at a fraction of the tokens of raw HTML. The tool shows a token estimate and can add YAML front matter with the title and source URL."),
            ("Can it convert a whole website?", "This page converts the HTML you give it. To crawl many URLs or a sitemap, render JavaScript and get chunks for RAG, use the Web Page to Markdown API linked below."),
        ],
        "related": ["pdf-to-markdown", "json-to-excel"],
    },
    {
        "slug": "pdf-to-markdown",
        "name": "PDF to Markdown",
        "title": "PDF to Markdown Converter (free, no upload, no limits)",
        "h1": "PDF to Markdown converter",
        "description": "Convert PDF to Markdown in your browser: headings, lists and paragraphs kept, running headers and page numbers removed. No upload, no file size or daily limit, batch to .zip. Free.",
        "lede": "Drop one PDF or a hundred. Each is read <b>in your browser</b>, so private files never leave your computer. You get Markdown with headings, lists and joined paragraphs, without the running headers, footers and page numbers.",
        "badges": ["Nothing uploaded", "No size or daily limit", "Batch to .zip", "Headers and page numbers removed", "Free, no sign-up"],
        "icon": "tool-pdf-to-markdown.png",
        "scripts": ["../vendor/pdf.min.js", "../vendor/fflate.js", "convert.js", "app.js"],
        "upsell_icon": "pdf-to-text-markdown.png",
        "upsell": "Scanned PDFs, tables you need in Excel, or thousands of files through an API? <b>PDF to Text, Markdown &amp; Excel</b> adds OCR, real spreadsheet tables (borderless ones too) and RAG chunks. $3 per 1,000 PDFs.",
        "upsell_url": APIFY + "pdf-to-text-markdown",
        "upsell_cta": "See the PDF API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2>PDF files</h2><button type="button" class="secondary" id="btn-sample">Try a sample</button></div>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose PDF files to convert"><strong>Drop PDF files here</strong> or click to choose.<br>One or many. They stay on your computer.</div>
    <input type="file" id="file-in" accept=".pdf,application/pdf" multiple hidden>
    <div class="opts" role="group" aria-label="Options">
      <label><input type="checkbox" id="opt-markers"> Mark page breaks</label>
      <label><input type="checkbox" id="opt-keep"> Keep running headers and footers</label>
    </div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
    <ul class="files" id="file-list"></ul>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2><label for="md-out">Markdown</label></h2><span class="status" id="stats" aria-live="polite"></span></div>
    <textarea id="md-out" spellcheck="false" readonly placeholder="The Markdown of the first PDF appears here."></textarea>
    <div class="row"><button type="button" id="btn-copy" disabled>Copy</button><button type="button" class="secondary" id="btn-download" disabled>Download .md</button></div>
  </div>
</div>
""",
        "howto": [
            "Drop your PDFs on the box, or click it to choose files. Several files are converted one after another.",
            "Check the Markdown of the first file on the right. Headings come from the font sizes, lists and contents entries are kept, and broken lines and hyphenated words are joined.",
            "Download one .md file, or a .zip with one .md per PDF.",
            "Turn on <b>Mark page breaks</b> if you need page numbers for citations (it adds <code>&lt;!-- page 3 --&gt;</code> comments).",
        ],
        "faq": [
            ("Are my PDFs uploaded?", "No. They are read in your browser with Mozilla's pdf.js. Nothing is sent to a server, which is why there is no size limit, no daily limit and no account."),
            ("Does it work on scanned PDFs?", "Not on its own. A scanned page is a picture with no text layer, and this page has no OCR. The tool tells you when a file looks scanned. The PDF API linked below reads scans with OCR in 12 languages."),
            ("What happens to tables?", "Each table row comes out on its own line with cells separated by |, which keeps the data readable. For real spreadsheets (numbers you can sum, tables joined across pages), use the PDF API, which exports Excel and CSV."),
            ("How are headings found?", "From font sizes: text clearly larger than the body text and used for short lines becomes #, ## or ### headings. Two-column pages, like research papers, are read column by column."),
            ("Is it good for ChatGPT, Claude or RAG?", "Yes. Markdown keeps headings and lists that models use for context, and dropping repeated headers and page numbers saves tokens. The tool shows a token estimate for each file."),
        ],
        "related": ["html-to-markdown", "json-to-excel"],
    },
    {
        "slug": "json-to-excel",
        "name": "JSON to Excel",
        "title": "JSON to Excel & CSV Converter (nested JSON, real .xlsx, free)",
        "h1": "JSON to Excel and CSV converter",
        "description": "Convert JSON to a real Excel .xlsx or CSV in your browser. Flattens nested JSON, splits lists into rows, keeps leading zeros. Works with JSON Lines and API exports. Free, no upload, no limits.",
        "lede": "Paste JSON or drop a file. Nested objects become columns like <code>user.address.city</code>, lists can become extra rows, and you download a <b>real .xlsx</b> with numbers as numbers and IDs like <code>007</code> kept as text.",
        "badges": ["Real .xlsx", "Nested JSON flattened", "Lists to rows", "JSON Lines too", "Nothing uploaded"],
        "icon": "tool-json-to-excel.png",
        "scripts": ["../vendor/fflate.js", "convert.js", "app.js"],
        "upsell_icon": "public-tenders-feed.png",
        "upsell": "Need data that arrives ready for Excel? Every Pandapi API exports straight to Excel, CSV or JSON. <b>Public Tenders Feed</b>, for example, gives you new government tenders from the US, EU, UK, Canada and the World Bank in one table. $2 per 1,000 notices.",
        "upsell_url": APIFY + "public-tenders-feed",
        "upsell_cta": "See the Public Tenders API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="json-in">JSON</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="json-in" spellcheck="false" placeholder='Paste JSON, an array of objects, JSON Lines, or an API response like {"items": [...]}.'></textarea>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose a JSON file"><strong>Drop a .json or .jsonl file</strong> or click to choose.</div>
    <input type="file" id="file-in" accept=".json,.jsonl,.ndjson,.txt,application/json" hidden>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2>Table</h2></div>
    <div class="opts" role="group" aria-label="Options">
      <label>Lists <select id="opt-arrays"><option value="join">join in one cell</option><option value="rows">one row per item</option><option value="columns">one column per item</option></select></label>
      <label id="explode-wrap" hidden>split <select id="opt-explode" aria-label="List to split into rows"></select></label>
      <label><input type="checkbox" id="opt-numeric" checked> Numbers in text become numbers (Excel)</label>
      <label>CSV <select id="opt-delim" aria-label="CSV separator"><option value=",">comma</option><option value=";">semicolon (European Excel)</option><option value="tab">tab</option></select></label>
      <label><input type="checkbox" id="opt-protect" checked> Block formula injection</label>
    </div>
    <p class="status" id="summary" aria-live="polite"></p>
    <div class="table-wrap"><table class="preview" id="preview" aria-label="Preview of the first rows"></table></div>
    <div class="row"><button type="button" id="btn-xlsx" disabled>Download Excel (.xlsx)</button><button type="button" class="secondary" id="btn-csv" disabled>Download CSV</button><button type="button" class="secondary" id="btn-copy" disabled>Copy CSV</button></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </div>
</div>
<script type="text/plain" id="sample-json">{
  "count": 3,
  "items": [
    {"id": "00731", "title": "Road resurfacing, Lot 2", "buyer": {"name": "City of Lyon", "country": "FR"}, "value": 1250000, "deadline": "2026-12-01", "cpv": ["45233220", "45233000"],
     "lots": [{"lot": 1, "title": "North section", "value": 700000}, {"lot": 2, "title": "South section", "value": 550000}]},
    {"id": "00732", "title": "School IT equipment", "buyer": {"name": "Leeds City Council", "country": "GB"}, "value": "380000", "deadline": "2026-11-28", "cpv": ["30213000"],
     "lots": [{"lot": 1, "title": "Laptops", "value": 300000}]},
    {"id": "00733", "title": "Bridge inspection services", "buyer": {"name": "Ontario Ministry of Transportation", "country": "CA"}, "value": null, "deadline": "2026-12-15", "cpv": [], "lots": []}
  ]
}</script>
""",
        "howto": [
            "Paste JSON or drop a file. The tool finds the list of records itself, even inside an API response like <code>{\"data\": {\"results\": [...]}}</code>.",
            "Choose what to do with lists: join them in one cell, give each item its own row (an order with 3 lines becomes 3 rows), or its own columns.",
            "Check the preview, then download Excel (.xlsx) or CSV. Pick semicolons if your Excel uses commas for decimals.",
        ],
        "faq": [
            ("Is my data uploaded?", "No. Parsing and the Excel file are both made in your browser, so customer exports and API keys inside the data never leave your computer. There is no size limit beyond your computer's memory."),
            ("Why .xlsx instead of CSV?", "Excel changes CSV data as it opens it: 007 becomes 7, long IDs turn into 1.23E+15 and accented letters can break. The .xlsx keeps text as text and numbers as numbers, with a bold, frozen header row and filters."),
            ("How is nested JSON flattened?", "Nested objects become dot columns (buyer.name, buyer.country). Lists of values are joined in one cell, and lists of objects can be joined as JSON, split into one row per item, or spread into numbered columns."),
            ("Which JSON shapes work?", "An array of objects, a single object, an object that wraps the records (items, data, results...), arrays of arrays with a header row, and JSON Lines / NDJSON with one object per line, like Apify dataset exports."),
            ("What is formula injection?", "A cell that starts with =, +, - or @ can run as a formula when a CSV is opened in Excel. With the option on, such text cells get a leading apostrophe so they show as text. Numbers are not touched."),
        ],
        "related": ["html-to-markdown", "pdf-to-markdown"],
    },
]

BY_SLUG = {t["slug"]: t for t in TOOLS}


def head(title, description, path, icon, extra=""):
    canon = f'<link rel="canonical" href="{SITE_URL}/{path}">' if SITE_URL else ""
    og_img = f'<meta property="og:image" content="{SITE_URL}/assets/icons/{icon}">' if SITE_URL else ""
    depth = "../" if path else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(description)}">
{canon}
<meta property="og:type" content="website">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(description)}">
{og_img}
<meta name="theme-color" content="#4d7c0f">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; worker-src 'self' blob:; connect-src 'self' blob: data:; object-src 'none'; base-uri 'self'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="{depth}favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="{depth}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{depth}assets/site.css">
{extra}
</head>
<body>
<header class="site-header"><div class="wrap">
  <a class="brand" href="{depth or './'}"><img src="{depth}assets/mark.png" alt="" width="32" height="32"><span>Pandapi <b>Tools</b></span></a>
  <nav class="site-nav" aria-label="Tools">{''.join(f'<a href="{depth}{t["slug"]}/"{" aria-current=\"page\"" if path == t["slug"] + "/" else ""}>{E(t["name"])}</a>' for t in TOOLS)}</nav>
</div></header>
"""


def foot(depth):
    return f"""<footer class="site-footer"><div class="wrap">
  <span>🐼 Pandapi Tools: free tools that run in your browser. Nothing you use here is uploaded or stored.</span>
  <span><a href="https://apify.com/blueberry_rainstorm">Pandapi data APIs</a> · <a href="{depth}privacy.html">Privacy</a></span>
</div></footer>
</body>
</html>
"""


def tool_page(t):
    path = t["slug"] + "/"
    ld = [
        {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": t["h1"], "applicationCategory": "UtilitiesApplication",
         "operatingSystem": "Any (web browser)", "description": t["description"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "publisher": {"@type": "Organization", "name": "Pandapi"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]},
    ]
    if SITE_URL:
        ld[0]["url"] = f"{SITE_URL}/{path}"
    extra = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    out = [head(t["title"], t["description"], path, t["icon"], extra)]
    out.append(f"""<main><div class="wrap">
<div class="hero"><img src="../assets/icons/{t['icon']}" alt="" width="64" height="64"><h1>{E(t['h1'])}</h1></div>
<p class="lede">{t['lede']}</p>
<ul class="badges">{''.join(f'<li>{E(b)}</li>' for b in t['badges'])}</ul>
{t['tool']}
<div class="card upsell"><img src="../assets/icons/{t['upsell_icon']}" alt="" width="56" height="56"><p>{t['upsell']}</p><a class="btn" href="{t['upsell_url']}">{E(t['upsell_cta'])}</a></div>
<section class="content">
<h2>How to use it</h2>
<ol>{''.join(f'<li>{s}</li>' for s in t['howto'])}</ol>
<h2>Questions</h2>
{''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in t['faq'])}
<h2>More free tools</h2>
<div class="grid">{''.join(tile(BY_SLUG[s], '../') for s in t['related'])}</div>
</section>
</div></main>
<script src="../assets/site.js"></script>
{''.join(f'<script src="{s}"></script>' for s in t['scripts'])}
""")
    out.append(foot("../"))
    return "".join(out)


def tile(t, depth):
    return (f'<a class="card tile" href="{depth}{t["slug"]}/"><img src="{depth}assets/icons/{t["icon"]}" alt="" width="56" height="56">'
            f'<div><h3>{E(t["name"])}</h3><p>{E(t["description"].split(". ")[0])}.</p></div></a>')


def home():
    desc = "Free, private tools for developers and data people: HTML to Markdown, PDF to Markdown, JSON to Excel. Everything runs in your browser; nothing is uploaded."
    return (head("Pandapi Tools: free converters that run in your browser", desc, "", "tool-html-to-markdown.png")
            + f"""<main><div class="wrap">
<h1>Free tools that run in your browser</h1>
<p class="lede">Small, careful converters for everyday data jobs. No sign-up, no limits, no upload: your files never leave your computer. When you need the same job done in bulk or through an API, each tool links to the matching Pandapi API.</p>
<div class="grid">{''.join(tile(t, '') for t in TOOLS)}</div>
</div></main>
""" + foot(""))


def privacy():
    return (head("Privacy · Pandapi Tools", "Pandapi Tools run in your browser. We don't upload, store or track what you convert.", "privacy.html", "tool-html-to-markdown.png")
            + """<main><div class="wrap"><section class="content" style="margin-top:0">
<h1>Privacy</h1>
<p>Every Pandapi Tool runs entirely in your web browser. The text and files you paste or drop are processed on your device and are never uploaded, stored or shared. The pages load no ads, no analytics and no third-party scripts, and they set no cookies.</p>
<p>The site is hosted as static files. Like any web host, the host may keep standard server logs (such as IP address and the page requested) for security; we don't use them to track you.</p>
<p>Questions: open an issue on the Pandapi profile at <a href="https://apify.com/blueberry_rainstorm">apify.com/blueberry_rainstorm</a>.</p>
</section></div></main>
""" + foot(""))


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    for t in TOOLS:
        write(f"{t['slug']}/index.html", tool_page(t))
    write("index.html", home())
    write("privacy.html", privacy())
    write(".nojekyll", "")
    if SITE_URL:
        urls = [""] + [t["slug"] + "/" for t in TOOLS]
        write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              + "".join(f"<url><loc>{SITE_URL}/{u}</loc></url>" for u in urls) + "</urlset>\n")
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("built", len(TOOLS), "tools")
