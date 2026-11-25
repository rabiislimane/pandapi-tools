#!/usr/bin/env python3
"""Builds the Pandapi Tools static pages: python3 build.py
Each tool lives in <slug>/ (convert.js + app.js); this script writes <slug>/index.html and index.html
from the definitions below so the header, footer, SEO tags and FAQ markup stay identical everywhere.
Set SITE_URL once the site has its public address (canonical links, sitemap)."""
import html
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")  # e.g. https://rabiislimane.github.io/pandapi-tools
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
    {
        "slug": "html-table-to-excel",
        "name": "HTML Table to Excel",
        "title": "HTML Table to Excel & CSV Converter (any web page, free, private)",
        "h1": "HTML table to Excel and CSV converter",
        "description": "Copy a table from any web page and get a clean Excel .xlsx or CSV. Finds every table, handles merged cells, turns 1,234.5 into real numbers and drops [1] footnotes. Free, nothing uploaded.",
        "lede": "Select a table on any web page, copy it and paste it here, or paste the page's HTML. You get every table on the page, merged cells filled in, footnote marks like <code>[1]</code> removed and numbers like <code>1,234.5</code> turned into real numbers, as a <b>real .xlsx</b> (one sheet per table) or CSV.",
        "badges": ["Every table on the page", "Merged cells handled", "Real numbers in Excel", "One sheet per table", "Nothing uploaded"],
        "icon": "tool-html-table-to-excel.png",
        "scripts": ["../vendor/fflate.js", "../json-to-excel/convert.js", "convert.js", "app.js"],
        "upsell_icon": "web-page-to-markdown.png",
        "upsell": "Need tables from hundreds of pages, or the same page every day? <b>Web Page to Markdown</b> fetches any list of URLs or a whole sitemap, renders JavaScript pages and returns each page with its tables as clean Markdown tables, through an API or on a schedule.",
        "upsell_url": APIFY + "web-page-to-markdown",
        "upsell_cta": "See the Web Page to Markdown API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="html-in">Web page or HTML</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="html-in" spellcheck="false" placeholder="Select a table on a web page, copy it (Ctrl+C) and paste it here. Or paste a page's HTML source (Ctrl+U)."></textarea>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose an HTML file"><strong>Drop a saved web page (.html)</strong> or click to choose.</div>
    <input type="file" id="file-in" accept=".html,.htm,.xhtml,.xls,text/html" hidden>
    <div class="opts" role="group" aria-label="Options">
      <label><input type="checkbox" id="opt-rich" checked> Paste keeps the table</label>
      <label><input type="checkbox" id="opt-footnotes" checked> Remove footnote marks like [1]</label>
      <label><input type="checkbox" id="opt-numbers" checked> 1,234.5 and (12) become numbers</label>
      <label><input type="checkbox" id="opt-symbols"> Also strip $ € £ and %</label>
      <label><input type="checkbox" id="opt-links"> Add link columns</label>
      <label>Header <select id="opt-header"><option value="auto">detect</option><option value="yes">first row</option><option value="no">none</option></select></label>
      <label>Merged cells <select id="opt-merged"><option value="repeat">repeat the value</option><option value="blank">first cell only</option></select></label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2>Tables</h2></div>
    <p class="status" id="summary" aria-live="polite"></p>
    <div id="tables-wrap" hidden>
      <div class="row"><button type="button" class="secondary" id="btn-all">Select all / none</button></div>
      <ul class="table-list" id="table-list" aria-label="Tables found; tick the ones to download, click a name to preview"></ul>
      <p class="meta" id="preview-note"></p>
      <div class="table-wrap"><table class="preview" id="preview" aria-label="Preview of the chosen table"></table></div>
    </div>
    <div class="row"><button type="button" id="btn-xlsx" disabled>Download Excel (.xlsx)</button><button type="button" class="secondary" id="btn-csv" disabled>Download CSV</button><button type="button" class="secondary" id="btn-copy" disabled>Copy for Excel / Sheets</button>
      <label class="meta">CSV <select id="opt-delim" aria-label="CSV separator"><option value=",">comma</option><option value=";">semicolon</option><option value="tab">tab</option></select></label></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </div>
</div>
<script type="text/plain" id="sample-html"><h2>Largest cities</h2>
<table class="wikitable sortable">
<caption>Largest metropolitan areas, 2025<sup class="reference"><a href="#cite_note-1">[1]</a></sup></caption>
<thead>
<tr><th rowspan="2">Rank</th><th rowspan="2">City</th><th rowspan="2">Country</th><th colspan="2">Population</th></tr>
<tr><th>Metro</th><th>Change since 2015</th></tr>
</thead>
<tbody>
<tr><td>1</td><td><a href="https://en.wikipedia.org/wiki/Tokyo">Tokyo</a></td><td>Japan</td><td>37,036,200</td><td>(1.2%)</td></tr>
<tr><td>2</td><td><a href="https://en.wikipedia.org/wiki/Delhi">Delhi</a><sup class="reference"><a href="#cite_note-2">[2]</a></sup></td><td>India</td><td>34,665,600</td><td>31.4%</td></tr>
<tr><td>3</td><td><a href="https://en.wikipedia.org/wiki/Shanghai">Shanghai</a></td><td rowspan="2">China</td><td>30,482,100</td><td>18.0%</td></tr>
<tr><td>4</td><td><a href="https://en.wikipedia.org/wiki/Chongqing">Chongqing</a></td><td>17,773,000</td><td>8.9%</td></tr>
<tr><td>5</td><td><a href="https://en.wikipedia.org/wiki/Dhaka">Dhaka</a></td><td>Bangladesh</td><td>24,652,900</td><td>36.1%</td></tr>
</tbody>
</table>
<h2>Exchange rates</h2>
<table>
<tr><th>Currency</th><th>Code</th><th>Per US dollar</th></tr>
<tr><td>Euro</td><td>EUR</td><td>0.9213</td></tr>
<tr><td>Japanese yen</td><td>JPY</td><td>1,512.40</td></tr>
<tr><td>Swiss franc</td><td>CHF</td><td>0.8841</td></tr>
</table></script>
""",
        "howto": [
            "Select the table on the web page (drag from its first cell to its last), copy it with Ctrl+C and paste it here. To get every table, paste the page source instead (Ctrl+U, then Ctrl+A, Ctrl+C) or drop a saved .html file.",
            "Pick the tables you want in the list and click a name to preview it. Merged cells, header rows and footnote marks are handled for you.",
            "Download Excel (one sheet per table), CSV (a .zip when you pick several), or copy the table and paste it straight into Excel or Google Sheets.",
        ],
        "faq": [
            ("Is my data uploaded?", "No. The HTML is read and the Excel file is made in your browser, so tables from intranet pages, admin panels or private reports never leave your computer."),
            ("Can I paste a URL?", "Not here: a page running in your browser can't fetch other websites. Copy the table from the page, paste the page source, or drop a saved .html file. To pull tables from many URLs automatically, use the Web Page to Markdown API linked on this page."),
            ("What happens to merged cells?", "A cell that spans several rows or columns is repeated in each of them, so every row is complete for sorting and filtering. Choose “first cell only” to leave the others empty, like the original layout."),
            ("Why do some numbers stay as text?", "Values like 007 or long ID numbers stay text so Excel doesn't drop the zeros or round them. Numbers with thousands separators (1,234.5), accounting minus signs ((12)) and the − sign become real numbers. Tick “strip $ € £ and %” to turn $12.50 or 45% into numbers too."),
            ("Does it work with Wikipedia tables?", "Yes. Footnote marks like [1] and hidden sort keys are removed, stacked header rows become names like “Population / Metro”, and each table gets its caption or section heading as its name."),
        ],
        "related": ["json-to-excel", "html-to-markdown"],
    },
    {
        "slug": "link-extractor",
        "name": "Link Extractor",
        "title": "Link Extractor: Get All Links from a Web Page, Text or Sitemap (free)",
        "h1": "Link extractor: every link from a page, text or sitemap",
        "description": "Extract every link from a web page's HTML, part of a page, plain text or a sitemap.xml. Anchor text, internal or external, nofollow, duplicates counted. Export Excel, CSV or a URL list. Free, nothing uploaded.",
        "lede": "Paste a page's HTML, copy part of a page, paste any text, or drop a <code>sitemap.xml</code> or saved pages. You get <b>every link</b> with its anchor text, internal or external, nofollow and how often it appears, as Excel, CSV or a plain URL list.",
        "badges": ["HTML, text and sitemaps", "Anchor text and nofollow", "Internal vs external", "Many files at once", "Nothing uploaded"],
        "icon": "tool-link-extractor.png",
        "scripts": ["../vendor/fflate.js", "../json-to-excel/convert.js", "../html-table-to-excel/convert.js", "convert.js", "app.js"],
        "upsell_icon": "broken-link-checker.png",
        "upsell": "Want to know which of these links are dead? <b>Broken Link Checker</b> crawls your whole site, checks every link and image, and lists each 404, server error and redirect with the page it is on and its anchor text. Run it once or every week.",
        "upsell_url": APIFY + "broken-link-checker",
        "upsell_cta": "See the Broken Link Checker",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="links-in">Page, text or sitemap</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="links-in" spellcheck="false" placeholder="Paste a page's HTML source (Ctrl+U), copy part of a web page, paste text with URLs, or paste a sitemap.xml."></textarea>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose files"><strong>Drop saved pages (.html), a sitemap (.xml) or text files</strong> or click to choose. Several at once is fine.</div>
    <input type="file" id="file-in" accept=".html,.htm,.xhtml,.xml,.txt,.md,.csv,.json,text/html,text/xml,text/plain" multiple hidden>
    <p class="meta" id="file-note" aria-live="polite"></p>
    <div class="opts" role="group" aria-label="Options">
      <label class="wide">Page URL <input type="url" id="opt-base" placeholder="https://example.com/page" autocomplete="off"></label>
      <p class="meta" id="base-hint" hidden>Add the page URL to turn relative links like /about into full URLs and sort them into internal and external.</p>
      <label><input type="checkbox" id="opt-rich" checked> Paste keeps the links</label>
      <label><input type="checkbox" id="opt-dedupe" checked> Merge duplicates and count them</label>
      <label><input type="checkbox" id="opt-hash" checked> Ignore #fragments</label>
      <label><input type="checkbox" id="opt-tracking"> Remove utm_ and other tracking tags</label>
      <label><input type="checkbox" id="opt-images"> Include images</label>
      <label><input type="checkbox" id="opt-resources"> Include scripts, styles and iframes</label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2>Links</h2></div>
    <p class="status" id="summary" aria-live="polite"></p>
    <div id="results-wrap" hidden>
      <div class="opts" role="group" aria-label="Filter">
        <label>Show <select id="f-type"></select></label>
        <label>Sort <select id="f-sort"><option value="page">page order</option><option value="url">URL</option><option value="domain">domain</option><option value="count">most used</option><option value="lastmod" id="sort-lastmod" hidden>last modified</option></select></label>
        <label class="wide">Search <input type="search" id="f-q" placeholder="part of a URL or anchor text"></label>
      </div>
      <p class="meta" id="preview-note"></p>
      <div class="table-wrap"><table class="preview" id="preview" aria-label="Links found"></table></div>
      <p class="meta"><b>Top domains:</b></p>
      <ul class="domain-list" id="domains"></ul>
      <p class="meta" id="domains-more"></p>
    </div>
    <div class="row"><button type="button" id="btn-xlsx" disabled>Download Excel (.xlsx)</button><button type="button" class="secondary" id="btn-csv" disabled>Download CSV</button><button type="button" class="secondary" id="btn-copy-urls" disabled>Copy URLs</button><button type="button" class="secondary" id="btn-copy" disabled>Copy table</button>
      <label class="meta">CSV <select id="opt-delim" aria-label="CSV separator"><option value=",">comma</option><option value=";">semicolon</option><option value="tab">tab</option></select></label></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </div>
</div>
<script type="text/plain" id="sample-html"><!doctype html>
<html><head><title>Pour-over coffee guide</title>
<link rel="canonical" href="https://coffee.example/guides/pour-over">
<link rel="stylesheet" href="/assets/site.css"></head>
<body>
<nav><a href="/">Home</a> <a href="/guides/">Guides</a> <a href="/shop/?utm_source=nav">Shop</a> <a href="#main">Skip to content</a></nav>
<main id="main"><h1>How to brew pour-over coffee</h1>
<p>Start with our <a href="/guides/grind#pour-over">grind size guide</a>, then weigh 20 g of coffee. The <a href="https://www.sca.coffee/research/coffee-standards" title="SCA brewing standards">SCA golden ratio</a> is a good start.</p>
<p>We like the <a href="https://shop.example.org/v60?utm_source=coffee&amp;utm_medium=affiliate" rel="sponsored nofollow" target="_blank">Hario V60</a> and a <a href="https://shop.example.org/kettle" rel="sponsored nofollow">gooseneck kettle</a>.</p>
<p><a href="/guides/grind">Read the grind guide</a> or watch <a href="https://video.example.com/watch?v=abc123" rel="nofollow ugc">a reader's video</a>.</p>
<a href="/guides/french-press"><img src="/img/french-press.jpg" alt="French press guide"></a>
<iframe src="https://video.example.com/embed/abc123" title="Brewing video"></iframe>
</main>
<footer><a href="mailto:hello@coffee.example">hello@coffee.example</a> · <a href="tel:+15550100">Call us</a> · <a href="/privacy">Privacy</a> · <a href="/">Home</a></footer>
</body></html></script>
""",
        "howto": [
            "Paste a page's HTML (open the page, press Ctrl+U, then Ctrl+A and Ctrl+C), or select part of a page and copy it: the links come with it. Plain text with URLs and sitemap.xml files work too, and you can drop several saved pages at once.",
            "Add the page URL if the page doesn't name itself, so /about becomes a full URL and links are sorted into internal and external. Filter by type, search, or sort by URL, domain or how often a link is used.",
            "Download Excel (a Links sheet and a Domains sheet), CSV, or copy the URLs one per line. To find which links are broken, run the Broken Link Checker on your site.",
        ],
        "faq": [
            ("Is my data uploaded?", "No. The page is read in your browser, so links from intranet pages, admin panels or pages behind a login never leave your computer."),
            ("Can I paste a URL?", "Not here: a page running in your browser can't fetch other websites. Open the page, press Ctrl+U to see its source and paste that, or save the page (Ctrl+S) and drop the .html file. The Broken Link Checker linked on this page fetches whole sites for you."),
            ("What counts as internal?", "A link to the same host as the page, with or without www. The page's own address comes from the Page URL box, or from the page's canonical link or base tag when it has one."),
            ("What does nofollow mean here?", "The column says yes when the link's rel attribute has nofollow, sponsored or ugc, which tell search engines not to pass ranking credit. The Rel column shows the exact value."),
            ("Does it read sitemap index files?", "Yes. A sitemap index lists its child sitemaps (Kind: Sitemap) and a normal sitemap lists its pages with last modified date, change frequency, priority and image count. Drop several sitemap files to merge them."),
        ],
        "related": ["html-table-to-excel", "html-to-markdown"],
    },
    {
        "slug": "email-extractor",
        "name": "Email Extractor",
        "title": "Email Extractor: Pull Email Addresses from Text, PDF, Word & Excel (free)",
        "h1": "Email extractor: every address from text, PDFs, Word and Excel",
        "description": "Extract email addresses from pasted text, web pages, PDF, Word, Excel, CSV, .eml and vCard files. Names kept, duplicates merged, role and free-mail addresses flagged, [at] [dot] decoded. Free, nothing uploaded.",
        "lede": "Paste anything with email addresses in it, or drop <b>PDF, Word, Excel, CSV, .eml, .vcf or .html</b> files, several at once. You get one clean list with the <b>name next to each address</b>, where it was found, and whether it is a person, a role inbox like info@, a free mailbox or a no-reply. Addresses written as <code>jane [at] acme [dot] com</code> are decoded too.",
        "badges": ["PDF, Word, Excel, CSV, .eml", "Names kept", "[at] [dot] decoded", "Role and free-mail flags", "Nothing uploaded"],
        "icon": "tool-email-extractor.png",
        "scripts": ["../vendor/pdf.min.js", "../vendor/fflate.js", "../pdf-to-markdown/convert.js", "../csv-to-json/convert.js", "../json-to-excel/convert.js", "../html-table-to-excel/convert.js", "convert.js", "app.js"],
        "upsell_icon": "website-contact-finder.png",
        "upsell": "Need the emails of a list of companies, not of a file? <b>Website Contact Finder</b> visits each website you give it, reads its contact, about and team pages, and returns emails, phone numbers and social profiles for every site. Paste 10 or 10,000 domains; sites with no contacts are free.",
        "upsell_url": APIFY + "website-contact-finder",
        "upsell_cta": "See the Website Contact Finder",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="emails-in">Text, page or files</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="emails-in" spellcheck="false" placeholder="Paste text, an email thread, a contact list, a web page (or its HTML source), CSV or cells copied from a spreadsheet."></textarea>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose files"><strong>Drop PDF, Word (.docx), Excel (.xlsx), CSV, .eml, .vcf, .html or text files</strong> or click to choose. Several at once is fine.</div>
    <input type="file" id="file-in" accept=".pdf,.docx,.xlsx,.xlsm,.csv,.tsv,.txt,.md,.json,.eml,.mbox,.vcf,.ics,.html,.htm,.xml,.log,application/pdf,text/plain,text/csv,text/html" multiple hidden>
    <p class="meta" id="file-note" aria-live="polite"></p>
    <div class="opts" role="group" aria-label="Options">
      <label><input type="checkbox" id="opt-dedupe" checked> Merge duplicates and count them</label>
      <label><input type="checkbox" id="opt-deob" checked> Decode [at] and [dot]</label>
      <label><input type="checkbox" id="opt-lower" checked> Lowercase addresses</label>
      <label><input type="checkbox" id="opt-rich" checked> Paste keeps hidden mailto addresses</label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2>Email addresses</h2></div>
    <p class="status" id="summary" aria-live="polite"></p>
    <div id="results-wrap" hidden>
      <div class="opts" role="group" aria-label="Filter">
        <label><input type="checkbox" id="f-personal" checked> Personal</label>
        <label><input type="checkbox" id="f-role" checked> Role (info@, sales@)</label>
        <label><input type="checkbox" id="f-free" checked> Free mailbox (Gmail...)</label>
        <label><input type="checkbox" id="f-noreply"> No-reply</label>
        <label>Sort <select id="f-sort"><option value="found">order found</option><option value="email">email</option><option value="domain">domain</option><option value="count">most seen</option></select></label>
        <label class="wide">Search <input type="search" id="f-q" placeholder="part of an address or name"></label>
      </div>
      <p class="meta" id="preview-note"></p>
      <div class="table-wrap"><table class="preview" id="preview" aria-label="Email addresses found"></table></div>
      <p class="meta"><b>Top domains:</b></p>
      <ul class="domain-list" id="domains"></ul>
      <p class="meta" id="domains-more"></p>
    </div>
    <div class="row"><button type="button" id="btn-xlsx" disabled>Download Excel (.xlsx)</button><button type="button" class="secondary" id="btn-csv" disabled>Download CSV</button><button type="button" class="secondary" id="btn-copy-list" disabled>Copy addresses</button><button type="button" class="secondary" id="btn-copy" disabled>Copy table</button></div>
    <div class="row"><label class="meta">Copy as <select id="opt-sep" aria-label="Address separator"><option value="lines">one per line</option><option value="comma">comma separated</option><option value="semicolon">semicolon (Outlook)</option></select></label>
      <label class="meta">CSV <select id="opt-delim" aria-label="CSV separator"><option value=",">comma</option><option value=";">semicolon</option><option value="tab">tab</option></select></label></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </div>
</div>
<script type="text/plain" id="sample-text">From: "Ortega, Maria" <maria.ortega@brightlane.io>
To: Sam Lee <sam.lee@northwind-foods.com>; sales@northwind-foods.com
Cc: priya.nair@gmail.com
Subject: Re: Supplier list for Q3

Hi Sam,

Here are the contacts you asked for:
- Packaging: Tom Becker, tom.becker@kartonwerk.de, +49 30 1234567
- Logistics: logistics (at) shipfast-eu (dot) com
- Our new buyer is Lena Park (lena.park@brightlane.io).
- For invoices write to billing@brightlane.io, not to the no-reply address noreply@notify.brightlane.io.

Thanks!
Maria Ortega | Head of Purchasing
maria.ortega@brightlane.io | brightlane.io
<img src="logo@2x.png"> Template address: name@example.com</script>
""",
        "howto": [
            "Paste text from anywhere: an email thread, a web page, a spreadsheet, a CRM export or a document. Or drop files, several at once: PDF, Word (.docx), Excel (.xlsx), CSV, saved emails (.eml), contact cards (.vcf) and web pages (.html).",
            "Check the list. Each address appears once, with the name written next to it, how often it was seen and where (file, page, sheet and row). Untick role addresses, free mailboxes or no-replies to drop them, or search for one company's domain.",
            "Download Excel (an Emails sheet and a Domains sheet) or CSV, or copy the addresses one per line, comma separated, or semicolon separated to paste straight into Outlook's To box.",
        ],
        "faq": [
            ("Is my data uploaded?", "No. Everything runs in your browser, so contracts, inboxes, CRM exports and customer lists never leave your computer. You can turn off your internet after the page loads and it still works."),
            ("Which files can it read?", "PDF (with a text layer, not scans), Word .docx, Excel .xlsx, CSV and TSV, saved emails (.eml and .mbox), vCard contact files (.vcf), calendar files (.ics), web pages (.html) and any plain text file. Old .doc and .xls files must be saved as .docx or .xlsx first."),
            ("How does it find the name?", "It takes the name written right before the address, as in Maria Ortega <maria@...> or \"Ortega, Maria\" <...>, or right after it in brackets, and the visible text of mailto links. If no name is next to an address, the Name column stays empty rather than guessing."),
            ("What do the types mean?", "Role is a shared inbox like info@, sales@ or support@. Free mailbox is a personal account at Gmail, Outlook, Yahoo and about 100 other providers. No-reply addresses can't receive mail. Everything else is marked personal."),
            ("Does it check that the addresses work?", "No. It finds and cleans addresses that are written correctly; it does not send mail or contact any server. Image names like logo@2x.png, template addresses such as name@example.com and tracking ids are left out."),
            ("Can I paste a website address?", "Not here: a page running in your browser can't visit other websites. Open the page, select all and copy, or save it and drop the .html file. To get the emails of many websites at once, use the Website Contact Finder linked on this page."),
        ],
        "related": ["link-extractor", "csv-to-json"],
    },
    {
        "slug": "word-to-markdown",
        "name": "Word to Markdown",
        "title": "Word to Markdown Converter: DOCX to MD with Images, Tables and Footnotes (free)",
        "h1": "Word to Markdown converter",
        "description": "Convert Word .docx files to clean Markdown in your browser: headings, lists, tables, footnotes, links and images (saved to a .zip). Many files at once, or paste from Word or Google Docs. Free, nothing uploaded.",
        "lede": "Drop <b>.docx files</b>, several at once, or <b>paste straight from Word or Google Docs</b>. You get clean GitHub-flavored Markdown with headings, nested lists, tables, footnotes, links and code, and the document's <b>images saved as files</b> in a .zip next to the Markdown. Add front matter from the document's title, author and dates for a static site or Obsidian.",
        "badges": ["Many .docx at once", "Paste from Word or Google Docs", "Images to a .zip", "Footnotes and tables", "Nothing uploaded"],
        "icon": "tool-word-to-markdown.png",
        "scripts": ["../vendor/mammoth.min.js", "../vendor/fflate.js", "../vendor/turndown.js", "../vendor/turndown-plugin-gfm.js", "convert.js", "app.js"],
        "upsell_icon": "pdf-to-text-markdown.png",
        "upsell": "Got PDFs too, or thousands of documents to convert from a script? <b>PDF to Text, Markdown &amp; Excel</b> turns PDFs into Markdown through an API, with OCR for scans, real tables and chunks ready for RAG. $3 per 1,000 PDFs.",
        "upsell_url": APIFY + "pdf-to-text-markdown",
        "upsell_cta": "See the PDF API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="word-in">Word document</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose Word files"><strong>Drop .docx files here</strong> or click to choose. Several at once is fine.</div>
    <input type="file" id="file-in" accept=".docx,.docm,.dotx,application/vnd.openxmlformats-officedocument.wordprocessingml.document" multiple hidden>
    <p class="meta">Or paste from Word, Google Docs or a web page:</p>
    <textarea id="word-in" spellcheck="false" placeholder="Copy text in Word or Google Docs (Ctrl+A, Ctrl+C) and paste it here (Ctrl+V). Headings, lists, bold, links and tables come along."></textarea>
    <p class="meta" id="paste-note" aria-live="polite"></p>
    <div class="opts" role="group" aria-label="Options">
      <label>Images <select id="opt-images"><option value="files">save as files (.zip)</option><option value="inline">embed in the Markdown</option><option value="drop">leave out</option></select></label>
      <label><input type="checkbox" id="opt-front"> Front matter (title, author, dates)</label>
      <label><input type="checkbox" id="opt-underline"> Keep underline as &lt;u&gt;</label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2><label for="md-out">Markdown</label></h2>
      <select id="file-pick" aria-label="Show the Markdown of" hidden></select></div>
    <p class="status" id="summary" aria-live="polite"></p>
    <textarea id="md-out" spellcheck="false" readonly placeholder="Your Markdown appears here."></textarea>
    <p class="meta" id="file-note2" aria-live="polite"></p>
    <div class="row"><button type="button" id="btn-md" disabled>Download .md</button><button type="button" id="btn-zip" hidden disabled>Download .zip (Markdown + images)</button><button type="button" class="secondary" id="btn-copy" disabled>Copy Markdown</button></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
  </div>
</div>
""",
        "howto": [
            "Drop one or more .docx files, or open your document in Word or Google Docs, select everything (Ctrl+A), copy and paste it into the box. Pasting keeps headings, lists, bold, italics, links and tables.",
            "Pick how to handle images: save them as files (the .zip has your Markdown and an images/ folder, linked by relative paths), embed them in the Markdown, or leave them out. Tick front matter to start each file with its title, author and dates.",
            "Download the .md file, the .zip with images, or copy the Markdown. With several files, use the menu above the Markdown to look at each one, and Download all to get every file in one .zip.",
        ],
        "faq": [
            ("Is my document uploaded?", "No. The .docx file is read and converted in your browser, so contracts, drafts and internal documents never leave your computer. The page works offline once it has loaded."),
            ("What is kept?", "Headings (Title and Heading 1-6), bold, italics, strike-through, links, bullet and numbered lists with nesting, tables, footnotes and endnotes (as [^1] notes), block quotes, code styles and images with their alt text. Underline has no Markdown form, so it is dropped unless you keep it as <u>."),
            ("What happens to tables with merged cells?", "Markdown tables can't merge cells, so a table with merged cells, or with lists inside its cells, is written as a small HTML table inside the Markdown. GitHub, Obsidian and most static site generators show it as a table. Simple tables become normal Markdown tables."),
            ("Can it read .doc files or password-protected documents?", "No. Old .doc files (Word 97-2003) and encrypted documents use a different format. Open them in Word or LibreOffice, save as .docx, and drop that file here."),
            ("Why are images missing when I paste from Word?", "When you copy from Word, the clipboard points to temporary image files that a browser isn't allowed to read. Drop the .docx file instead and every image comes out. Pasting from Google Docs keeps images as links."),
            ("Does it work for Google Docs?", "Yes, two ways: paste straight from the document (the page fixes Google Docs' bold-everything clipboard), or use File > Download > Microsoft Word (.docx) and drop that file to get the images too."),
        ],
        "related": ["html-to-markdown", "pdf-to-markdown"],
    },
    {
        "slug": "csv-to-json",
        "name": "CSV & Excel to JSON",
        "title": "CSV to JSON and Excel to JSON Converter (free, private, batch)",
        "h1": "CSV and Excel to JSON converter",
        "description": "Convert CSV, TSV or Excel (.xlsx) to JSON in your browser. Real numbers and dates, leading zeros kept, nested JSON, JSON Lines, every sheet at once, many files to a .zip. Free, nothing uploaded.",
        "lede": "Paste CSV or cells copied from Excel or Google Sheets, or drop <code>.csv</code> and <code>.xlsx</code> files. You get clean JSON with <b>real numbers, true/false and ISO dates</b>, while zip codes and IDs like <code>00721</code> stay text. Drop several files to get a .zip of JSON files.",
        "badges": ["CSV, TSV and .xlsx", "Dates as 2026-03-05, not 46086", "Nested JSON and JSON Lines", "Many files to .zip", "Nothing uploaded"],
        "icon": "tool-csv-to-json.png",
        "scripts": ["../vendor/fflate.js", "convert.js", "app.js"],
        "upsell_icon": "pdf-to-text-markdown.png",
        "upsell": "Is your table stuck in a PDF? <b>PDF to Excel, Markdown &amp; Text</b> pulls tables out of PDFs in bulk, scans and borderless bank statements included, and returns each table's header and rows as JSON plus an Excel workbook, through an API. About $3 per 1,000 PDFs.",
        "upsell_url": APIFY + "pdf-to-text-markdown",
        "upsell_cta": "See the PDF tables API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="csv-in">CSV, TSV or Excel cells</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="csv-in" spellcheck="false" placeholder="Paste CSV here, or copy cells in Excel or Google Sheets and paste them."></textarea>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose CSV or Excel files"><strong>Drop .csv, .tsv or .xlsx files</strong> or click to choose. One file opens here; several files become a .zip of JSON files.</div>
    <input type="file" id="file-in" accept=".csv,.tsv,.txt,.tab,.xlsx,.xlsm,.xls,text/csv,text/tab-separated-values,text/plain,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" multiple hidden>
    <p class="meta" id="file-note" aria-live="polite"></p>
    <div class="opts" role="group" aria-label="Options">
      <label id="sheet-wrap" class="wide" hidden>Sheet <select id="opt-sheet"></select></label>
      <label>Separator <select id="opt-delim"><option value="auto">auto-detect</option><option value=",">comma</option><option value=";">semicolon</option><option value="tab">tab</option><option value="|">pipe</option></select></label>
      <label><input type="checkbox" id="opt-header" checked> First row is the header</label>
      <label>Values <select id="opt-types"><option value="smart">numbers, true/false, null</option><option value="text">everything as text</option></select></label>
      <label>Empty cells <select id="opt-empty"><option value="string">""</option><option value="null">null</option><option value="omit">leave out</option></select></label>
      <label>Nested keys <select id="opt-nested"><option value="off">off</option><option value=".">from a.b and a[0]</option><option value="/">from a/b</option></select></label>
      <label><input type="checkbox" id="opt-decimal"> Decimal comma (1.234,5)</label>
      <label><input type="checkbox" id="opt-transpose"> Swap rows and columns</label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2><label for="json-out">JSON</label></h2><span class="status" id="summary" aria-live="polite"></span></div>
    <div class="opts" role="group" aria-label="Output">
      <label>Shape <select id="opt-shape"><option value="array">array of objects</option><option value="jsonl">JSON Lines (one per line)</option><option value="keyed">object keyed by a column</option><option value="arrays">array of arrays</option><option value="columns">one array per column</option></select></label>
      <label id="key-wrap" hidden>Key <select id="opt-key"></select></label>
      <label>Indent <select id="opt-indent"><option value="2">2 spaces</option><option value="4">4 spaces</option><option value="tab">tab</option><option value="0">none (minified)</option></select></label>
    </div>
    <textarea id="json-out" spellcheck="false" readonly placeholder="JSON appears here as you type."></textarea>
    <div class="row"><button type="button" id="btn-copy" disabled>Copy</button><button type="button" class="secondary" id="btn-download" disabled>Download .json</button></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
    <div id="cols" hidden><p class="meta"><b>Columns and the type found:</b></p><ul class="col-list" id="col-list"></ul></div>
  </div>
</div>
<div class="card" style="margin-top:16px">
  <div class="pane-head"><h2>Many files at once</h2></div>
  <p class="meta">Drop two or more files in the box above. Each becomes its own .json file with the options above (all sheets for workbooks), and you get one .zip.</p>
  <p class="status" id="batch-status" role="status" aria-live="polite"></p>
  <ul class="files" id="batch-list"></ul>
</div>
<script type="text/plain" id="sample-csv">
order_id,date,customer.name,customer.email,items,total,paid,zip
00721,2026-03-05,Ann Lee,ann@example.com,2,49.90,true,02134
00722,2026-03-06,"Chen, Bo",,1,1234.50,false,10001
00723,2026-03-07,"Zoë ""Z"" Martin",zoe@example.com,3,-7,TRUE,94105
</script>
""",
        "howto": [
            "Paste CSV, or copy cells in Excel or Google Sheets and paste them (they arrive tab-separated, which is detected). You can also drop a .csv, .tsv or .xlsx file; for a workbook, pick one sheet or all sheets.",
            "Check the options: the separator is found for you, numbers and true/false become real JSON values, and anything with a leading zero or more than 15 digits stays text so zip codes and IDs survive. Turn on <b>Nested keys</b> to make <code>customer.name</code> a nested object.",
            "Pick the shape: an array of objects (most APIs), JSON Lines (one record per line, for BigQuery, MongoDB or AI fine-tuning files), an object keyed by a column, or arrays. Copy the JSON or download it.",
            "To convert a folder of files, drop them all at once and download one .zip.",
        ],
        "faq": [
            ("Are my files uploaded?", "No. The CSV and Excel files are read in your browser, so customer lists, exports and reports never leave your computer, and the page works offline once loaded."),
            ("Why do my Excel dates come out as dates?", "Excel stores a date as a day number (46086 is 5 March 2026) and only its cell format says it is a date. This tool reads the cell formats, so dates come out as 2026-03-05, date-times as 2026-03-06T14:30:00 and times as 09:15:00. Numbers come out as Excel shows them, so 0.1+0.2 is 0.3, not 0.30000000000000004."),
            ("Which values become numbers?", "Plain numbers like 42, -3.5 or 1e3. Values with a leading zero (00721), more than 15 digits, a plus sign or spaces stay text, because turning them into numbers would change them. Choose \"everything as text\" to keep every value as a string."),
            ("My CSV shows strange characters like Ã©. What now?", "Files are read as UTF-8 when they are valid UTF-8, and as Windows-1252 (what older Excel saves) when they are not, so accents like é and ü come out right without picking an encoding."),
            ("Can it read .xls or .ods files?", "Not yet. Save old .xls (Excel 97-2003) and .ods files as .xlsx or .csv first. Password-protected workbooks can't be read either."),
        ],
        "related": ["json-to-excel", "html-table-to-excel"],
    },
    {
        "slug": "markdown-to-pdf",
        "name": "Markdown to PDF",
        "title": "Markdown to PDF Converter (free, no watermark, private)",
        "h1": "Markdown to PDF converter",
        "description": "Convert Markdown to a clean PDF in your browser: real selectable text, code colors, tables, images, clickable table of contents and page numbers. Many .md files at once. Free, no watermark, nothing uploaded.",
        "lede": "Paste Markdown (a README, notes, or an answer from ChatGPT or Claude) or drop <code>.md</code> files. You get a PDF with <b>real, searchable text</b>, colored code, tables that repeat their header on each page, your images, and an optional <b>clickable table of contents</b>. No limits and no watermark.",
        "badges": ["Real text, not a screenshot", "Clickable table of contents", "Code colors and tables", "Many .md files at once", "No watermark, nothing uploaded"],
        "icon": "tool-markdown-to-pdf.png",
        "styles": ["md.css"],
        "scripts": ["../vendor/marked.js", "../vendor/highlight.min.js", "../vendor/pdfmake.min.js", "../vendor/pdfmake-mono.js", "../vendor/pdfmake-fonts.js", "../vendor/fflate.js", "convert.js", "app.js"],
        "upsell_icon": "html-to-pdf.png",
        "upsell": "Making PDFs from your app or a workflow? <b>HTML to PDF</b> turns HTML, Markdown-made pages or any URL into PDFs through an API, in bulk, with headers, footers and page sizes, ready for n8n, Make or your own code. Pay per PDF, no monthly plan.",
        "upsell_url": APIFY + "html-to-pdf",
        "upsell_cta": "See the HTML to PDF API",
        "tool": """
<div class="tool">
  <div class="pane card">
    <div class="pane-head"><h2><label for="md-in">Markdown</label></h2>
      <div class="row"><button type="button" class="secondary" id="btn-sample">Try a sample</button><button type="button" class="secondary" id="btn-clear">Clear</button></div></div>
    <textarea id="md-in" spellcheck="false" placeholder="Paste or type Markdown here. You can paste a screenshot too."></textarea>
    <div class="drop" id="drop" tabindex="0" role="button" aria-label="Choose Markdown files"><strong>Drop .md files</strong> (and their images) or click to choose. One file opens here; several become a .zip of PDFs or one combined PDF.</div>
    <input type="file" id="file-in" accept=".md,.markdown,.mdown,.mkd,.txt,text/markdown,text/plain,image/*" multiple hidden>
    <div class="opts" role="group" aria-label="Page options">
      <label>Page <select id="opt-size"><option value="A4">A4</option><option value="LETTER">US Letter</option><option value="LEGAL">US Legal</option><option value="A5">A5</option></select></label>
      <label><select id="opt-orient" aria-label="Orientation"><option value="portrait">portrait</option><option value="landscape">landscape</option></select></label>
      <label>Margins <select id="opt-margins"><option value="narrow">narrow</option><option value="normal" selected>normal</option><option value="wide">wide</option></select></label>
      <label>Text size <select id="opt-font"><option value="10">10 pt</option><option value="11" selected>11 pt</option><option value="12">12 pt</option></select></label>
      <label><input type="checkbox" id="opt-toc"> Table of contents</label>
      <label><input type="checkbox" id="opt-nums" checked> Page numbers</label>
      <label><input type="checkbox" id="opt-header"> Title at the top of each page</label>
      <label><input type="checkbox" id="opt-break"> Each # heading on a new page</label>
    </div>
  </div>
  <div class="pane card">
    <div class="pane-head"><h2>Preview</h2></div>
    <div class="paper md-body" id="preview" aria-live="off"></div>
    <div class="row"><button type="button" id="btn-pdf" disabled>Download PDF</button><button type="button" class="secondary" id="btn-print" disabled>Print / Save as PDF</button></div>
    <p class="status" id="status" role="status" aria-live="polite"></p>
    <ul class="notes" id="notes" aria-live="polite"></ul>
  </div>
</div>
<div class="tool" style="margin-top:16px">
  <div class="card">
    <div class="pane-head"><h2>Images</h2></div>
    <div class="drop" id="img-drop" tabindex="0" role="button" aria-label="Add images"><strong>Add images</strong> used in your Markdown. They are matched by file name, so <code>![chart](img/chart.png)</code> uses chart.png.</div>
    <input type="file" id="img-in" accept="image/*" multiple hidden>
    <p class="meta" id="img-note" aria-live="polite"></p>
  </div>
  <div class="card">
    <div class="pane-head"><h2>Many files at once</h2></div>
    <p class="meta">Drop two or more .md files in the Markdown box. Each becomes a PDF with the options above, sorted by name.</p>
    <label class="meta"><input type="checkbox" id="opt-combine"> Combine them into one PDF</label>
    <p class="status" id="batch-status" role="status" aria-live="polite"></p>
    <ul class="files" id="batch-list"></ul>
  </div>
</div>
<script type="text/plain" id="sample-md">
---
title: Pour-over coffee guide
author: Pandapi Tools
---
# Pour-over coffee guide

Pour-over gives a **clean, bright cup**. This guide takes about *four minutes*. Jump to [the ratios](#ratios) or read the [SCA brewing standards](https://sca.coffee/research/coffee-standards).

## What you need

- [x] A dripper and a paper filter
- [x] A kettle, ideally gooseneck
- [ ] Fresh beans, ground medium-fine

## Ratios

| Cups | Coffee | Water | Time |
|:-----|-------:|------:|:----:|
| 1 | 20 g | 320 g | 3:00 |
| 2 | 36 g | 580 g | 3:30 |
| 4 | 64 g | 1,040 g | 4:15 |

> [!TIP]
> Rinse the filter with hot water first, so the coffee doesn't taste of paper.

## Steps

1. Heat the water to `94 °C`.
2. Bloom: pour 50 g and wait 45 seconds.
3. Pour the rest in slow circles.

```python
for step, seconds in [("bloom", 45), ("pour", 90), ("drain", 45)]:
    print(f"{step:>6}: {seconds} s")  # timer script
```

---

<!-- pagebreak -->

## Notes

Grind just before you brew. A finer grind slows the flow; a coarser one speeds it up.
</script>
""",
        "howto": [
            "Paste Markdown in the left box, or drop a .md file. The preview shows how it will look. If your Markdown uses images, add the image files in the Images box (or paste a screenshot into the text).",
            "Pick the page size, margins and text size. Turn on <b>Table of contents</b> for a contents page whose entries link to each heading, and <b>Each # heading on a new page</b> for chapters. Put <code>&lt;!-- pagebreak --&gt;</code> on its own line wherever you want a new page.",
            "Click <b>Download PDF</b>. The PDF has real text you can select and search, page numbers, working links and a title from your first heading or front matter.",
            "Writing in Chinese, Japanese, Korean, Arabic, Hebrew or with emoji? Use <b>Print / Save as PDF</b>: it uses your browser's own PDF engine, which has fonts for every language.",
            "For many files, drop them all at once and get a .zip of PDFs, or tick <b>Combine them into one PDF</b>.",
        ],
        "faq": [
            ("Is my Markdown uploaded?", "No. The PDF is made in your browser with open-source libraries (marked, highlight.js and pdfmake), so notes, specs and drafts never leave your computer. The page works offline once it has loaded."),
            ("Is there a limit or a watermark?", "No. Convert as many documents as you like, as often as you like. There is no account, no daily limit and no watermark."),
            ("Is the text in the PDF real text?", "Yes. The PDF has vector text with embedded fonts, not a picture of the page, so it stays sharp when you zoom, the file is small, and you can select, copy and search the text. Links and the table of contents are clickable."),
            ("Which Markdown does it support?", "GitHub Flavored Markdown: headings, bold, italic, strikethrough, links, lists, task lists, tables with alignment, code blocks with colors for common languages, block quotes, GitHub alerts like [!NOTE], images, horizontal rules and YAML front matter (title, author, date). Math and Mermaid diagrams are shown as their source text."),
            ("Why are some characters missing from my PDF?", "Download PDF embeds fonts for Latin, Greek and Cyrillic text. For Chinese, Japanese, Korean, Arabic, Hebrew, Indian scripts or emoji, click Print / Save as PDF and choose \"Save as PDF\" as the printer: your browser has fonts for those."),
        ],
        "related": ["html-to-markdown", "pdf-to-markdown"],
    },
]

BY_SLUG = {t["slug"]: t for t in TOOLS}

# SEO guide pages (see SEO-PAGES.md): one folder per page at the site root.
import seo_pages  # noqa: E402
from seo_content_tools import PAGES as _API_PAGES  # noqa: E402
from seo_content_compare import PAGES as _COMPARE_PAGES  # noqa: E402
SEO_PAGES = _API_PAGES + _COMPARE_PAGES
import outcome_pages  # noqa: E402  (outcome pages for non-technical buyers, strategy v3)
HOME_GUIDES = ["export-app-store-reviews", "extract-tables-from-pdf-to-excel", "website-to-markdown-api", "government-tenders-api", "firecrawl-alternative", "tableconvert-alternative"]
assert len({p["slug"] for p in SEO_PAGES}) == len(SEO_PAGES), "duplicate SEO page slug"
assert not {p["slug"] for p in SEO_PAGES} & set(BY_SLUG), "SEO page slug clashes with a tool"
assert not set(outcome_pages.BY_SLUG) & ({p["slug"] for p in SEO_PAGES} | set(BY_SLUG)), "outcome page slug clashes"


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
  <nav class="site-nav" aria-label="Tools">{''.join(f'<a href="{depth}{t["slug"]}/"{" aria-current=\"page\"" if path == t["slug"] + "/" else ""}>{E(t["name"])}</a>' for t in TOOLS)}<a href="{depth}guides/"{' aria-current="page"' if path == "guides/" else ""}>API guides</a></nav>
</div></header>
"""


def foot(depth):
    return f"""<footer class="site-footer"><div class="wrap">
  <span>🐼 Pandapi Tools: free tools that run in your browser. Nothing you use here is uploaded or stored.</span>
  <span><a href="{depth}guides/">Guides</a> · <a href="https://apify.com/blueberry_rainstorm">Pandapi data APIs</a> · <a href="{depth}privacy.html">Privacy</a></span>
</div></footer>
</body>
</html>
"""


def upsell_href(t):
    """Paid-API link with the tracking tags every Tools-site upsell carries."""
    url = t["upsell_url"]
    if "utm_source=" in url:
        return url
    return url + ("&" if "?" in url else "?") + f"utm_source=pandapi-tools&utm_medium=tool&utm_campaign={t['slug']}"


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
    extra += "".join(f'\n<link rel="stylesheet" href="{c}">' for c in t.get("styles", []))
    out = [head(t["title"], t["description"], path, t["icon"], extra)]
    out.append(f"""<main><div class="wrap">
<div class="hero"><img src="../assets/icons/{t['icon']}" alt="" width="64" height="64"><h1>{E(t['h1'])}</h1></div>
<p class="lede">{t['lede']}</p>
<ul class="badges">{''.join(f'<li>{E(b)}</li>' for b in t['badges'])}</ul>
{t['tool']}
<div class="card upsell"><img src="../assets/icons/{t['upsell_icon']}" alt="" width="56" height="56"><p>{t['upsell']}</p><a class="btn" href="{E(upsell_href(t))}">{E(t['upsell_cta'])}</a></div>
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
    desc = "Free, private tools for developers and data people: HTML to Markdown, PDF to Markdown, JSON to Excel, HTML tables to Excel, a link extractor, an email extractor, Word to Markdown, CSV and Excel to JSON, Markdown to PDF. Everything runs in your browser; nothing is uploaded."
    return (head("Pandapi Tools: free converters that run in your browser", desc, "", "tool-html-to-markdown.png")
            + f"""<main><div class="wrap">
<h1>Free tools that run in your browser</h1>
<div class="card cta" style="margin-top:0"><p><b>New: alerts you can set up in 3 minutes, no code.</b> {' · '.join(f'<a href="{p["slug"]}/">{E(p["short"])}</a>' for p in outcome_pages.PAGES)}</p></div>
<p class="lede">Small, careful converters for everyday data jobs. No sign-up, no limits, no upload: your files never leave your computer. When you need the same job done in bulk or through an API, each tool links to the matching Pandapi API.</p>
<div class="grid">{''.join(tile(t, '') for t in TOOLS)}</div>
<h2 style="margin-top:32px">Guides: do the same job in bulk</h2>
<p class="lede">How to export app reviews, pull tables out of hundreds of PDFs, turn a docs site into Markdown for RAG, track government tenders and more, plus honest comparisons with Firecrawl, Hunter, ScreenshotOne and others. <a href="guides/">All guides</a>.</p>
<div class="grid">{''.join(seo_pages.guide_tile(p, '') for p in SEO_PAGES if p['slug'] in HOME_GUIDES)}</div>
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
    for p in SEO_PAGES:
        write(f"{p['slug']}/index.html", seo_pages.page_html(p, head, foot, BY_SLUG, SEO_PAGES, SITE_URL))
    for p in outcome_pages.PAGES:
        write(f"{p['slug']}/index.html", outcome_pages.page_html(p, head, foot, SITE_URL))
    write("guides/index.html", seo_pages.hub_html(head, foot, SEO_PAGES, SITE_URL, outcome_pages))
    write("index.html", home())
    write("privacy.html", privacy())
    write(".nojekyll", "")
    if SITE_URL:
        urls = [""] + [t["slug"] + "/" for t in TOOLS] + ["guides/"]
        lastmod = {p["slug"] + "/": seo_pages.UPDATED for p in SEO_PAGES}
        urls += list(lastmod)
        for p in outcome_pages.PAGES:
            lastmod[p["slug"] + "/"] = outcome_pages.UPDATED
            urls.append(p["slug"] + "/")
        write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              + "".join(f"<url><loc>{SITE_URL}/{u}</loc>" + (f"<lastmod>{lastmod[u]}</lastmod>" if u in lastmod else "") + "</url>" for u in urls) + "</urlset>\n")
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("built", len(TOOLS), "tools,", len(SEO_PAGES), "guide pages and", len(outcome_pages.PAGES), "outcome pages")
