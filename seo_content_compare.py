"""Comparison and "alternative" pages (kind "compare"). Competitor facts come from their own
pricing pages or docs and the Apify Store API, checked 2026-11-21; the sources are listed on each
page. Be fair: every page says where the competitor is the better choice. See SEO-PAGES.md."""
from seo_pages import a, code, curl, table, steps

PAGES = []


def page(**kw):
    kw.setdefault("kind", "compare")
    PAGES.append(kw)


def sources(*links, checked="21 November 2026"):
    return f'<p class="sources">Sources, checked {checked}: ' + ", ".join(
        f'<a href="{u}" rel="nofollow noopener">{t}</a>' for t, u in links) + ". Prices change; check their pages before you buy.</p>"


# Firecrawl -----------------------------------------------------------------------------------------
S = "firecrawl-alternative"
page(
    slug=S, tool="web-page-to-markdown",
    title="Firecrawl Alternatives: Free and Pay-per-Page Options (2026)",
    h1="Firecrawl alternatives: free, open-source and pay-per-page options",
    description="Firecrawl vs Jina Reader, Crawl4AI, Apify Website Content Crawler and Pandapi Website to Markdown: prices, free tiers, crawling, chunking and when each one is the better pick.",
    lede="Firecrawl is the best-known way to turn websites into LLM-ready Markdown. It's also a monthly credit plan, and many people only need a few thousand pages, or a whole docs site once a week. Here are the alternatives, with prices and the cases where Firecrawl is still the right choice.",
    body=f"""
<h2>The short answer</h2>
<ul>
<li><b>Free and self-hosted:</b> Crawl4AI (open source, Python) or Firecrawl's own open-source version.</li>
<li><b>Free for single pages:</b> Jina Reader (put <code>r.jina.ai/</code> in front of a URL).</li>
<li><b>Pay per page, no subscription:</b> {a('web-page-to-markdown', S, 'Pandapi Website to Markdown')} at $1 per 1,000 pages, failed pages free.</li>
<li><b>Stay with Firecrawl</b> if you need web search, LLM extraction to JSON or browser actions in the same API.</li>
</ul>

<h2>Comparison</h2>
{table(["", "Firecrawl", "Jina Reader", "Crawl4AI", "Apify Website Content Crawler", "Pandapi Website to Markdown"], [
    ["Pricing", "Credits: free 1,000 pages/month, Hobby $19/month for 5,000, Standard $99/month for 100,000", "Free without a key (20 requests/min); a key raises limits; paid by output tokens", "Free, you host it", "Free actor; you pay Apify compute", "$1 per 1,000 pages, no subscription; failed pages free"],
    ["Whole-site crawl", "Yes", "No (one URL per call)", "Yes", "Yes", "Yes: URL list, sitemap or crawl with a path scope"],
    ["JavaScript pages", "Yes", "Yes", "Yes", "Yes", "Yes, browser only when a page needs it"],
    ["RAG chunks", "Not built in", "Not built in", "Yes, configurable", "Not built in", "Yes: heading path, token count and #anchor link per chunk"],
    ["Search and LLM extraction", "Yes", "Search via s.jina.ai", "LLM extraction", "No", "No"],
    ["Docs tabs (MkDocs, Docusaurus)", "Not stated", "Not stated", "Not stated", "Not stated", "Selected tab or all tabs"],
])}
<p>Cost for the same job, 5,000 pages a month: Firecrawl Hobby $19; Pandapi $5 (covered by Apify's free $5 monthly credit). At 100,000 pages Firecrawl Standard ($99) and Pandapi ($100) cost about the same, so pick on features.</p>

<h2>Where Firecrawl is better</h2>
<ul><li>One API for search, scrape, crawl and structured extraction.</li><li>A large ecosystem: SDKs, LangChain and LlamaIndex loaders, an MCP server.</li><li>Browser actions (click, scroll, type) before scraping.</li></ul>

<h2>Where Pandapi is better</h2>
<ul><li>No monthly plan: a 300-page site once a month costs $0.30.</li><li>RAG-ready chunks with heading paths and anchors, and token counts on every page.</li><li>Failed pages cost nothing.</li><li>Runs inside Apify: schedules, webhooks, n8n and Make, and an MCP server for agents.</li></ul>

<h2>Try it on your own site</h2>
{curl("web-page-to-markdown", {"sitemapUrls": [{"url": "https://your-docs.example.com/sitemap.xml"}], "maxPages": 300, "chunkSize": 800})}
{sources(("Firecrawl pricing", "https://www.firecrawl.dev/pricing"), ("Jina Reader", "https://jina.ai/reader"), ("Crawl4AI", "https://github.com/unclecode/crawl4ai"), ("Apify Website Content Crawler", "https://apify.com/apify/website-content-crawler"))}
""",
    faq=[
        ("Is there a free Firecrawl alternative?", "Yes. Crawl4AI is open source and free to self-host, Jina Reader converts single URLs free at low rate limits, and Apify's free plan gives $5 of credit a month, which covers about 5,000 pages with Pandapi Website to Markdown."),
        ("Is Firecrawl free?", "Firecrawl's free plan includes 1,000 page credits a month with 2 concurrent requests. Paid plans start at $19 a month for 5,000 credits, per its pricing page."),
        ("Which is cheapest for a one-off crawl?", "A pay-per-page API. A 2,000-page docs site costs $2 with Pandapi, with no plan to cancel afterwards."),
        ("Can I self-host Firecrawl?", "Yes, Firecrawl publishes an open-source version. Self-hosting means running and scaling the browsers yourself."),
    ],
    related=["jina-reader-alternative", "website-to-markdown-api", "firecrawl-mcp-alternative"],
    free_tools=["html-to-markdown"],
)

# Jina Reader ---------------------------------------------------------------------------------------
S = "jina-reader-alternative"
page(
    slug=S, tool="web-page-to-markdown",
    title="Jina Reader Alternatives for Whole Sites and RAG Chunks",
    h1="Jina Reader alternatives: when one URL at a time isn't enough",
    description="Jina Reader (r.jina.ai) turns one URL into Markdown for free at low rate limits. Here's when you need an alternative: whole-site crawls, sitemaps, RAG chunks, schedules. Options and prices compared.",
    lede="Putting <code>https://r.jina.ai/</code> in front of a URL is the fastest way to get Markdown for an LLM, and it's free to try. It's one URL per request, though. Once you need a whole docs site, a sitemap, chunks or a nightly sync, you're writing a crawler around it.",
    body=f"""
<h2>What Jina Reader does well</h2>
<ul><li>No setup: <code>curl https://r.jina.ai/https://example.com</code> returns Markdown.</li><li>Free without a key at 20 requests a minute; a free or paid key raises it to 500 requests a minute. Paid use is billed by output tokens.</li><li>Handles JavaScript pages and PDFs by URL.</li></ul>

<h2>Where you need something else</h2>
{table(["Need", "Jina Reader", "Pandapi Website to Markdown"], [
    ["Convert one URL now", "Best fit", "Works, but a run takes a few seconds to start"],
    ["Every page of a docs site", "You write the crawler and the queue", "Crawl from a start URL or read the sitemap"],
    ["Stay inside /docs/", "Your code", "crawlScope path"],
    ["RAG chunks", "Your code", "chunkSize + overlap, heading path, #anchor link"],
    ["Retries and failures", "Your code", "Retries built in; failed pages free"],
    ["Price model", "Tokens of output", "$1 per 1,000 pages, whatever their length"],
    ["Schedules and webhooks", "Your server", "Apify schedules, webhooks, n8n and Make"],
])}
<p>Per-page pricing favours long pages (docs, articles); token pricing favours short ones. For a typical 2,000-token docs page, 1,000 pages is 2 million tokens.</p>

<h2>Switching takes one call</h2>
{curl("web-page-to-markdown", {"urls": [{"url": "https://docs.example.com/"}], "crawl": True, "crawlScope": "path", "maxPages": 500, "chunkSize": 800})}
<p>Other options: Firecrawl (credit plans, search and extraction), Crawl4AI (free, self-hosted). See <a href="../firecrawl-alternative/">Firecrawl alternatives</a>.</p>
{sources(("Jina Reader", "https://jina.ai/reader"), ("Jina API rate limits", "https://jina.ai/api-dashboard/rate-limit/"))}
""",
    faq=[
        ("Is Jina Reader free?", "You can call r.jina.ai without a key at 20 requests a minute. With a key the limit rises to 500 a minute, and usage is billed by output tokens after any free allowance."),
        ("Can Jina Reader crawl a whole website?", "Not by itself: it converts one URL per request. You need your own crawler, or an API that crawls, such as Pandapi Website to Markdown or Firecrawl."),
        ("What's a good alternative for RAG?", "One that returns chunks with their heading path and a source link, so answers can cite the section. Pandapi Website to Markdown does that at $1 per 1,000 pages."),
    ],
    related=["firecrawl-alternative", "website-to-markdown-api", "mcp-server-for-web-and-pdf"],
    free_tools=["html-to-markdown"],
)

# Camelot vs Tabula ---------------------------------------------------------------------------------
S = "camelot-vs-tabula"
page(
    slug=S, tool="pdf-to-text-markdown",
    title="Camelot vs Tabula: Which Extracts PDF Tables Better?",
    h1="Camelot vs Tabula for PDF tables (and a no-code option)",
    description="Camelot vs tabula-py for extracting tables from PDFs in Python: lattice vs stream, setup, accuracy on borderless tables, multi-page tables, and when a hosted API is less work.",
    lede="Both are free, open source and good. They differ in setup, in how they find columns, and in how much tuning they need per layout. Here's how to choose, with code for each.",
    body=f"""
<h2>At a glance</h2>
{table(["", "Camelot", "tabula-py", "Pandapi PDF API"], [
    ["Language", "Python", "Python wrapper around Tabula (Java)", "HTTP API, any language or no code"],
    ["Setup", "pip install camelot-py (plus Ghostscript or pdfium backend)", "pip install tabula-py, needs Java", "None"],
    ["Ruled tables", "lattice mode, very good", "lattice mode, good", "Yes"],
    ["Borderless tables", "stream mode, often needs column hints", "stream mode, good on simple layouts", "Yes, columns from text alignment"],
    ["Table across pages", "Separate tables; join yourself", "Separate tables; join yourself", "Joined automatically"],
    ["Wrapped cell text", "Extra rows", "Extra rows", "Merged into the cell"],
    ["Scanned PDFs", "No", "No", "OCR text (tables on scans not detected yet)"],
    ["Accuracy report", "Yes (parsing report, whitespace)", "No", "Method per table (ruled/borderless)"],
    ["Cost", "Free", "Free", "$3 per 1,000 PDFs"],
])}

<h2>Camelot</h2>
{code('''import camelot
tables = camelot.read_pdf("report.pdf", pages="1-end", flavor="lattice")  # or "stream"
print(tables[0].parsing_report)
tables.export("report.xlsx", f="excel")''', 'python')}
<p>Pick Camelot when you can look at the output and tune it: <code>table_areas</code>, <code>columns</code> and <code>row_tol</code> fix most stream-mode problems.</p>

<h2>tabula-py</h2>
{code('''import tabula
dfs = tabula.read_pdf("report.pdf", pages="all", lattice=True)  # or stream=True
tabula.convert_into("report.pdf", "report.csv", output_format="csv", pages="all")''', 'python')}
<p>Pick tabula-py when Java is already there and the tables are simple. The Tabula desktop app is handy for drawing table areas by hand.</p>

<h2>When neither is worth the time</h2>
<p>When the PDFs come from many different sources (bank statements from ten banks, supplier invoices), each new layout means new tuning. A hosted API that handles borderless tables, page joins and numbers is less work:</p>
{curl("pdf-to-text-markdown", {"urls": [{"url": "https://example.com/statement.pdf"}], "spreadsheetOutput": "xlsx", "mergeMultiPageTables": True})}
<p>More in <a href="../extract-tables-from-pdf-to-excel/">extract tables from PDF to Excel</a>.</p>
{sources(("Camelot docs", "https://camelot-py.readthedocs.io/"), ("tabula-py docs", "https://tabula-py.readthedocs.io/"))}
""",
    faq=[
        ("Is Camelot better than Tabula?", "On ruled tables they're close. Camelot gives you more control and a parsing report, which helps on borderless tables; tabula-py is simpler if Java is installed. Neither joins tables across pages."),
        ("Does Camelot need Java?", "No. Camelot is pure Python with a Ghostscript or pdfium backend. tabula-py needs Java because it wraps Tabula."),
        ("Can either read scanned PDFs?", "No. Both need a text layer. Run OCR first (for example OCRmyPDF), or use an API with OCR."),
        ("Is there a no-code option?", "Yes. The Pandapi PDF API takes PDF links and returns Excel or CSV, $3 per 1,000 PDFs, with Apify's free credit covering about 1,600 PDFs a month."),
    ],
    related=["extract-tables-from-pdf-to-excel", "bank-statement-pdf-to-excel", "best-free-pdf-to-excel-converters"],
    free_tools=["pdf-to-markdown", "html-table-to-excel"],
)

# Best free PDF to Excel -----------------------------------------------------------------------------
S = "best-free-pdf-to-excel-converters"
page(
    slug=S, tool="pdf-to-text-markdown",
    title="Best Free PDF to Excel Converters for Tables (2026)",
    h1="The best free ways to convert PDF tables to Excel",
    description="Free ways to convert PDF tables to Excel compared: Excel's own PDF import, Smallpdf, iLovePDF, Adobe Acrobat online, Tabula, Camelot and a pay-per-PDF API. What each handles, privacy, and limits.",
    lede="\"PDF to Excel\" tools all claim the same thing. The differences show up on real files: borderless bank statements, tables over several pages, numbers that land as text. Here's what each free option is good at.",
    body=f"""
<h2>Compared</h2>
{table(["Option", "Best for", "Privacy", "Watch out for"], [
    ["Excel (Get Data › From PDF)", "Clean ruled tables, if you have Microsoft 365", "Stays on your computer", "Borderless and multi-page tables; Windows Microsoft 365 only"],
    ["Smallpdf, iLovePDF, Adobe online", "One file, now, no install", "Files are uploaded", "Daily limits on free tiers; scanned PDFs usually need a paid plan"],
    ["Tabula (desktop)", "Drawing table areas by hand", "Local", "Needs Java; one layout at a time"],
    ["Camelot / tabula-py", "Developers with repeatable layouts", "Local", "Tuning per layout; no OCR"],
    ["Pandapi PDF API", "Many PDFs, mixed layouts, automation", "Your own Apify account", "Not free beyond Apify's $5 monthly credit (about 1,600 PDFs)"],
])}

<h2>How to pick</h2>
<ul>
<li><b>One file, ruled table:</b> Excel's PDF import or an online converter.</li>
<li><b>Sensitive file:</b> something local: Excel, Tabula or Camelot. Our free <a href="../pdf-to-markdown/">PDF to Markdown</a> tool also runs fully in your browser if you need the text.</li>
<li><b>Bank statements or reports every month:</b> an API, so the same job runs on a schedule. See <a href="../bank-statement-pdf-to-excel/">bank statement PDF to Excel</a>.</li>
<li><b>Developer, one known layout:</b> Camelot. See <a href="../camelot-vs-tabula/">Camelot vs Tabula</a>.</li>
</ul>

<h2>Test any of them with this checklist</h2>
<ol><li>Are numbers real numbers (can you SUM the column)?</li><li>Is a table that spans two pages one table?</li><li>Do wrapped descriptions stay in one cell?</li><li>Are negative amounts like (12.00) kept?</li><li>Did a borderless table keep its columns?</li></ol>
<p>The {a('pdf-to-text-markdown', S, 'Pandapi PDF API')} was built around that list.</p>
""",
    faq=[
        ("What is the best free PDF to Excel converter?", "For one ruled table, Excel's own PDF import (Microsoft 365) or an online converter. For private files, a local tool like Tabula. For many PDFs or borderless statements, an API; Pandapi's costs $3 per 1,000 PDFs and Apify's free credit covers about 1,600 a month."),
        ("Can I convert PDF to Excel without uploading?", "Yes: Excel's PDF import, Tabula and Camelot run on your computer."),
        ("Why do my numbers come out as text?", "Thousands separators, currency signs and brackets for negatives make Excel treat cells as text. A converter that parses numbers fixes this; otherwise use Data › Text to Columns."),
    ],
    related=["extract-tables-from-pdf-to-excel", "camelot-vs-tabula", "convertio-alternative"],
    free_tools=["pdf-to-markdown", "html-table-to-excel"],
)

# Bank statements ----------------------------------------------------------------------------------------
S = "bank-statement-pdf-to-excel"
page(
    slug=S, tool="pdf-to-text-markdown",
    title="Convert Bank Statement PDFs to Excel (Bulk, Real Numbers)",
    h1="Convert bank statement PDFs to Excel, in bulk",
    description="Bank statements are borderless tables over many pages, which breaks most PDF converters. How to convert them to Excel or CSV with real numbers, one or hundreds at a time.",
    lede="Accountants and bookkeepers get statements as PDFs and need them in Excel, Xero, QuickBooks or Tally. Statements are the hardest PDF tables: no lines between columns, descriptions that wrap, and transactions that run over many pages.",
    body=f"""
<h2>Why statements break converters</h2>
<ul><li>No ruling lines, so tools that look for cell borders find nothing.</li><li>The transaction table continues on every page, with the header repeated.</li><li>Long descriptions wrap onto a second line and become a fake row.</li><li>Amounts like <code>1,204.50</code> or <code>(85.00)</code> land as text.</li></ul>

<h2>Free route for one statement</h2>
<p>Try Excel's Data › Get Data › From PDF first. If columns run together, Tabula's desktop app lets you draw the table area and pick "stream" mode. Check that the closing balance matches before you trust it.</p>

<h2>Many statements: the API route</h2>
{steps([
    f"Open the {a('pdf-to-text-markdown', S, 'PDF to Excel API on Apify')}.",
    "Add the statement PDFs (links, or upload in the console). Add the password if the bank protects them.",
    "Keep <b>mergeMultiPageTables</b> and <b>numbersAsNumbers</b> on and pick xlsx. Each statement gets its own workbook, and <code>tables.xlsx</code> collects every statement's tables in one file.",
    "Run, download the workbook, and check the balance column sums.",
])}
{curl("pdf-to-text-markdown", {"urls": [{"url": "https://example.com/statements/2026-09.pdf"}, {"url": "https://example.com/statements/2026-10.pdf"}], "spreadsheetOutput": "xlsx", "mergeMultiPageTables": True, "numbersAsNumbers": True})}
<p>Price: $3 per 1,000 PDFs whatever the page count; a year of monthly statements for 25 clients (300 PDFs) costs $0.90. Scanned statements get OCR text at $5 per 1,000 pages, but table cells aren't detected on scans yet, so ask the bank for the digital PDF when you can.</p>
<p>Dedicated statement converters (subscription tools priced per page) add bank-specific templates and direct exports to accounting software; worth it if that is your whole job.</p>
""",
    faq=[
        ("How do I convert a bank statement PDF to Excel for free?", "Try Excel's PDF import or Tabula's stream mode for one statement. For many, Apify's free $5 monthly credit covers about 1,600 PDFs through the Pandapi PDF API."),
        ("Will the numbers be real numbers?", "Yes, with numbersAsNumbers on: separators and currency signs are removed and bracketed amounts become negatives."),
        ("Does it work with scanned statements?", "It returns OCR text for scanned pages, but doesn't rebuild table cells from scans yet. Digital PDFs from online banking work best."),
    ],
    related=["extract-tables-from-pdf-to-excel", "best-free-pdf-to-excel-converters", "camelot-vs-tabula"],
    free_tools=["pdf-to-markdown"],
)

# Convertio -------------------------------------------------------------------------------------------------
S = "convertio-alternative"
page(
    slug=S, tool="pdf-to-text-markdown",
    title="Convertio Alternative for PDFs, JSON and CSV: No Upload",
    h1="A Convertio alternative for data files that never uploads them",
    description="Convertio converts 300+ formats by uploading your files. For PDF to Markdown, Markdown to PDF, JSON or CSV to Excel and HTML tables, Pandapi's free tools convert in your browser with no upload and no limits.",
    lede="Convertio is a great all-rounder: video, audio, images, documents, 300+ formats. For data files it has two downsides: your file goes to a server, and the free tier has daily limits. For the formats below, there's a free way that never uploads anything.",
    body=f"""
<h2>Which tool for which job</h2>
{table(["Job", "Convertio", "Pandapi free tool (in your browser)"], [
    ["PDF to Markdown or text", "Upload, convert, download", '<a href="../pdf-to-markdown/">PDF to Markdown</a>: batch, headers and page numbers removed'],
    ["Markdown to PDF", "Upload", '<a href="../markdown-to-pdf/">Markdown to PDF</a>: real text, table of contents'],
    ["JSON to Excel", "Upload", '<a href="../json-to-excel/">JSON to Excel</a>: nested JSON flattened, real .xlsx'],
    ["CSV or Excel to JSON", "Upload", '<a href="../csv-to-json/">CSV and Excel to JSON</a>'],
    ["HTML table to Excel", "Not its focus", '<a href="../html-table-to-excel/">HTML table to Excel</a>: paste from any page'],
    ["Video, audio, images, ebooks", "Yes, 300+ formats", "No: use Convertio"],
])}

<h2>Limits compared</h2>
<ul>
<li><b>Convertio free:</b> its terms list files up to 100 MB and a daily allowance of conversion time; paid plans start at $9.99 a month.</li>
<li><b>Pandapi free tools:</b> no account, no file size cap beyond your computer's memory, no daily limit, and nothing leaves your browser.</li>
</ul>

<h2>When you need it in bulk</h2>
<p>For thousands of PDFs, scanned files (OCR) or real Excel tables from PDFs, the {a('pdf-to-text-markdown', S, 'Pandapi PDF API')} costs $3 per 1,000 PDFs and runs on a schedule.</p>
{sources(("Convertio terms", "https://convertio.co/terms"))}
""",
    faq=[
        ("Is there a Convertio alternative that doesn't upload files?", "For PDF, Markdown, JSON, CSV and HTML table conversions, yes: Pandapi's free tools run in your browser, so files never leave your computer."),
        ("Is Convertio free?", "It has a free tier with a 100 MB file limit and a daily conversion allowance, per its terms; paid plans start at $9.99 a month."),
        ("Can it convert video or images?", "Pandapi's tools are for data and documents only. For media formats, Convertio is the better choice."),
    ],
    related=["tableconvert-alternative", "best-free-pdf-to-excel-converters", "extract-tables-from-pdf-to-excel"],
    free_tools=["pdf-to-markdown", "markdown-to-pdf", "json-to-excel", "csv-to-json"],
)

# TableConvert -----------------------------------------------------------------------------------------------
S = "tableconvert-alternative"
page(
    slug=S, tool="web-page-to-markdown",
    title="TableConvert Alternative: Free Table Converters, No Upload",
    h1="TableConvert alternatives for Excel, CSV, JSON and HTML tables",
    description="TableConvert converts tables between 30+ formats. If you need HTML tables to Excel, JSON to Excel with nested data, or CSV and Excel to JSON, Pandapi's free tools do it in your browser, with real .xlsx files and no limits.",
    lede="TableConvert is the Swiss army knife of table formats: Markdown, LaTeX, SQL, MediaWiki and more. For the everyday jobs (a web table into Excel, an API response into a spreadsheet) these free tools go deeper.",
    body=f"""
<h2>Side by side</h2>
{table(["Job", "TableConvert", "Pandapi free tools"], [
    ["Formats", "30+ (Markdown, LaTeX, SQL, MediaWiki, ASCII...)", "Excel, CSV, JSON, HTML, Markdown"],
    ["HTML table to Excel", "Paste HTML", 'Paste straight from a web page; merged cells, footnotes and numbers handled (<a href="../html-table-to-excel/">tool</a>)'],
    ["Nested JSON to Excel", "Flat JSON", 'Nested objects flattened to columns, lists to rows, real .xlsx (<a href="../json-to-excel/">tool</a>)'],
    ["CSV / Excel to JSON", "Yes", 'Yes, with types, nesting by dotted headers (<a href="../csv-to-json/">tool</a>)'],
    ["API", "Free plan: 100 conversions in total, then paid plans", "Browser tools are free; bulk data comes from our APIs"],
    ["Where it runs", "See its privacy notes", "In your browser; nothing uploaded"],
])}

<h2>Pick TableConvert when</h2>
<p>You need LaTeX, SQL INSERTs, MediaWiki or ASCII tables, or an online table editor. It covers far more output formats.</p>

<h2>Pick Pandapi when</h2>
<p>You want a real Excel file with numbers as numbers, nested JSON handled properly, or tables copied straight from a web page, with no upload and no limits.</p>

<h2>Tables from hundreds of pages?</h2>
<p>Copying tables page by page doesn't scale. The {a('web-page-to-markdown', S, 'Website to Markdown API')} fetches a list of URLs or a sitemap and returns every page's tables as Markdown tables, for $1 per 1,000 pages.</p>
{sources(("TableConvert pricing", "https://tableconvert.com/pricing"))}
""",
    faq=[
        ("Is there a free alternative to TableConvert?", "Yes. Pandapi's free tools convert HTML tables, JSON, CSV and Excel in your browser with no account and no limits. TableConvert remains better for exotic formats like LaTeX and SQL."),
        ("How do I copy a table from a website into Excel?", "Select the table on the page, copy it, and paste it into the HTML table to Excel tool. Download the .xlsx; numbers stay numbers."),
        ("Does TableConvert have an API?", "Yes. Its pricing page lists a free plan with 100 conversions in total and paid monthly plans above that."),
    ],
    related=["convertio-alternative", "website-to-markdown-api"],
    free_tools=["html-table-to-excel", "json-to-excel", "csv-to-json"],
)

# Hunter.io ---------------------------------------------------------------------------------------------------
S = "hunter-io-alternative"
page(
    slug=S, tool="website-contact-finder",
    title="Hunter.io Alternative: Company Contacts by Website, Pay per Site",
    h1="Hunter.io alternatives for finding company contact details",
    description="Hunter.io finds and verifies personal work emails with monthly credits. If you need the public contact details companies publish (info@, phone, socials, address) for a list of websites, here's a pay-per-site alternative and how they differ.",
    lede="Hunter is built to find a specific person's work email and verify it. A lot of people searching for \"Hunter alternative\" actually need something simpler: the published contact details of a list of companies for a CRM. That's a different tool, and much cheaper.",
    body=f"""
<h2>Two different jobs</h2>
{table(["", "Hunter.io", "Pandapi Website Contact Finder"], [
    ["Finds", "Personal work emails by name and domain, from its index and patterns", "Contacts published on the site: role emails, phones, socials, address"],
    ["Verification", "Yes, email verifier", "No"],
    ["Data source", "Hunter's database", "Live crawl of the site's own pages (contact, about, imprint)"],
    ["Pricing", "Free plan with 50 credits a month; paid plans from $49 a month (2,000 credits)", "$5 per 1,000 websites with contacts; nothing found = free"],
    ["Output", "Per person", "One CRM-ready row per website"],
])}
<p>If you need named decision-makers and verified addresses, Hunter (or Apollo, Snov.io) is the right tool. If you need "how do I reach this company", the site already tells you, and reading it is cheap.</p>

<h2>Example: 500 suppliers into a CRM</h2>
{steps(["Export the websites to a list.", f"Paste them into the {a('website-contact-finder', S, 'Website Contact Finder')}.", "Download the CSV: emails, phones, LinkedIn, Facebook, Instagram, X and address per site.", "Import into HubSpot, Pipedrive or a sheet."])}
<p>If 400 of the 500 publish contacts, that costs $2.</p>

<h2>Use it lawfully</h2>
<p>Use published business contacts for relevant B2B outreach and follow GDPR, CAN-SPAM and CASL. Role addresses (info@, sales@) are the default; personal addresses are off unless you change it.</p>
{sources(("Hunter pricing", "https://hunter.io/pricing"))}
""",
    faq=[
        ("What is a cheaper alternative to Hunter.io?", "For company-level contacts (role emails, phones, socials), a website crawler like Pandapi's Website Contact Finder at $5 per 1,000 sites with results. For verified personal emails, Hunter's free plan (50 credits a month) or similar tools."),
        ("Does Hunter.io have a free plan?", "Yes, 50 credits a month per its pricing page; paid plans start at $49 a month."),
        ("Does the contact finder verify emails?", "No. It returns addresses the site itself publishes, with the page they were found on."),
    ],
    related=["find-emails-from-websites", "company-jobs-api"],
    free_tools=["email-extractor", "link-extractor"],
)

# ScreenshotOne ----------------------------------------------------------------------------------------------
S = "screenshotone-alternative"
page(
    slug=S, tool="website-screenshot",
    title="ScreenshotOne Alternatives for Bulk Screenshots (2026)",
    h1="ScreenshotOne alternatives for bulk website screenshots",
    description="ScreenshotOne, Apify's free Screenshot URL actor and Pandapi Website Screenshot compared: free tiers, price per 1,000 shots, full page, mobile, cookie banners, and real-time vs batch.",
    lede="ScreenshotOne is a polished real-time screenshot API with a monthly plan. If your job is a batch (200 client sites, a weekly visual record, a landing-page audit), paying per shot with no subscription can be cheaper.",
    body=f"""
<h2>Compared</h2>
{table(["", "ScreenshotOne", "Apify Screenshot URL", "Pandapi Website Screenshot"], [
    ["Model", "Real-time API, monthly plans", "Free actor (you pay Apify compute)", "Batch, pay per screenshot"],
    ["Free", "100 screenshots a month", "Within Apify's $5 credit", "About 1,250 a month with Apify's $5 credit"],
    ["Paid", "Basic $17/month for 2,000; Growth $79/month for 10,000", "Compute cost", "$4 per 1,000 successful shots"],
    ["Full page", "Yes", "Yes", "Yes"],
    ["Desktop + mobile in one run", "One device per call", "Check its options", "Yes, plus laptop and tablet"],
    ["Cookie banners hidden", "Yes, plus ad blocking", "Check its options", "Yes"],
    ["PDF output", "Yes", "Check its options", "Yes"],
    ["Failed pages", "See their terms", "Compute used", "Free; 4xx/5xx pages reported, not charged"],
])}

<h2>Choose ScreenshotOne when</h2>
<p>You render screenshots on demand inside your app (link previews, OG images), need caching, signed URLs, ad blocking and many rendering options, and a few hundred milliseconds matter.</p>

<h2>Choose a batch API when</h2>
<p>You have a list and want a folder of images: {a('website-screenshot', S, 'Pandapi Website Screenshot')} takes the list, does desktop and mobile in one run and charges only for shots that worked.</p>
{curl("website-screenshot", {"urls": [{"url": "https://example.com"}], "devices": ["desktop", "mobile"], "fullPage": True})}
{sources(("ScreenshotOne pricing", "https://screenshotone.com/pricing"), ("Apify Screenshot URL", "https://apify.com/apify/screenshot-url"))}
""",
    faq=[
        ("Is ScreenshotOne free?", "It has a free plan with 100 screenshots a month; paid plans start at $17 a month for 2,000, per its pricing page."),
        ("What's the cheapest way to screenshot 1,000 websites?", "A pay-per-shot batch API. Pandapi charges $4 per 1,000 successful screenshots, and Apify's free credit covers about 1,250 a month."),
        ("Can I take mobile screenshots too?", "Yes. Add mobile (and tablet) to devices; each URL is captured on each device in the same run."),
    ],
    related=["website-screenshots-in-bulk", "html-to-pdf-api"],
    free_tools=["markdown-to-pdf"],
)

# Screaming Frog ----------------------------------------------------------------------------------------------
S = "screaming-frog-alternative"
page(
    slug=S, tool="broken-link-checker",
    title="Screaming Frog Alternative for Broken Links (Cloud, No Licence)",
    h1="A Screaming Frog alternative for finding broken links",
    description="Screaming Frog is a full SEO crawler; the free version stops at 500 URLs. If you just need broken links on a bigger site, checked on a schedule in the cloud, here are the alternatives and what they cost.",
    lede="Screaming Frog SEO Spider is the standard desktop SEO crawler, and its free version is generous for small sites. When your site is bigger than 500 URLs and all you need is broken links, a £199-a-year licence and a desktop app left running may be more than the job needs.",
    body=f"""
<h2>Compared for the broken-link job</h2>
{table(["", "Screaming Frog (free)", "Screaming Frog (paid)", "Google Search Console", "Pandapi Broken Link Checker"], [
    ["Limit", "500 URLs per crawl", "Unlimited (your machine)", "What Google crawled", "Your maxPagesToCrawl / maxLinksToCheck"],
    ["Cost", "Free", "£199 per user per year", "Free", "$0.80 per 1,000 links checked"],
    ["Runs", "Desktop", "Desktop, schedulable", "Google's schedule", "Cloud, Apify schedules"],
    ["Where each broken link is", "Yes (inlinks)", "Yes", "Partly", "Yes: page, anchor text, count"],
    ["External links", "Yes", "Yes", "No", "Yes, bot-blocked sites marked blocked"],
    ["Rest of SEO audit", "Limited", "Full: titles, canonicals, hreflang, JS rendering...", "Indexing, performance", "No: links only"],
])}

<h2>Keep Screaming Frog when</h2>
<p>You do technical SEO audits. It checks far more than links, and nothing here replaces it.</p>

<h2>Use a cloud checker when</h2>
<p>You want broken links found every week without opening a desktop app, results in Slack or a sheet, and to pay only for what you check: a 3,000-link site costs $2.40 a run.</p>
{curl("broken-link-checker", {"startUrls": [{"url": "https://example.com/"}], "maxPagesToCrawl": 500, "onlyBroken": True})}
<p>Start with the {a('broken-link-checker', S, 'Broken Link Checker')}, or read <a href="../broken-link-checker-api/">how to find broken links</a>.</p>
{sources(("Screaming Frog pricing", "https://www.screamingfrog.co.uk/seo-spider/pricing/"))}
""",
    faq=[
        ("Is Screaming Frog free?", "The free version crawls up to 500 URLs per crawl and can't save crawls. A licence is £199 per user per year, per its pricing page."),
        ("What's a free alternative for broken links?", "Google Search Console's Not found report, Screaming Frog's free version for small sites, or a cloud checker with free credit: Apify's $5 a month covers about 6,000 links with Pandapi."),
        ("Can it run every week automatically?", "Yes. Schedule the run on Apify and send the results by email, Slack or webhook."),
    ],
    related=["broken-link-checker-api", "website-screenshots-in-bulk"],
    free_tools=["link-extractor"],
)

# PDFShift / wkhtmltopdf --------------------------------------------------------------------------------------
S = "pdfshift-alternative"
page(
    slug=S, tool="html-to-pdf",
    title="PDFShift and wkhtmltopdf Alternatives for HTML to PDF",
    h1="PDFShift, DocRaptor and wkhtmltopdf alternatives for HTML to PDF",
    description="HTML to PDF options compared: wkhtmltopdf (archived), Puppeteer/Playwright, Gotenberg, PDFShift's credit plans and a pay-per-PDF API with templates. Price per 1,000 PDFs and when each fits.",
    lede="wkhtmltopdf was the default for years; it's archived now and its old WebKit doesn't understand modern CSS. The replacements are headless Chrome (do it yourself), a hosted API with a monthly plan, or a pay-per-PDF API.",
    body=f"""
<h2>Options</h2>
{table(["Option", "Engine", "Cost", "Good for"], [
    ["wkhtmltopdf", "Old Qt WebKit", "Free", "Legacy only: the project is archived; flexbox and grid don't work"],
    ["Puppeteer / Playwright", "Chrome", "Free + your servers", "Developers who can run browsers"],
    ["Gotenberg", "Chrome + LibreOffice in Docker", "Free + your servers", "Self-hosted API"],
    ["WeasyPrint", "Own engine", "Free", "Print-style CSS, no JavaScript"],
    ["PDFShift", "Chrome", "Free 50 credits a month; paid plans from about $9 a month for 500", "Real-time conversions from your app"],
    ["DocRaptor", "Prince", "Paid plans", "Complex print layouts (footnotes, PDF/UA)"],
    ["Pandapi HTML to PDF", "Chrome", "$3 per 1,000 PDFs, any page count", "Batches: URLs, HTML, or template + JSON rows"],
])}

<h2>What makes Pandapi different</h2>
<ul>
<li><b>Template + data:</b> a Handlebars template and an array of rows give one PDF per row, named from your data (invoices, certificates, reports).</li>
<li><b>No plan:</b> 500 invoices a month cost $1.50; failed documents are free.</li>
<li><b>Page count doesn't matter:</b> a 40-page report costs the same as a 1-page invoice.</li>
</ul>
<p>Choose PDFShift or DocRaptor if you convert on demand inside a web request and need an answer in a second, or if you need Prince-level print typography.</p>
{curl("html-to-pdf", {"urls": [{"url": "https://example.com/report"}], "pageFormat": "A4", "pageNumbers": True, "hideCookieBanners": True})}
<p>Start with the {a('html-to-pdf', S, 'HTML to PDF API')}.</p>
{sources(("PDFShift FAQ", "https://pdfshift.io/faq"), ("wkhtmltopdf status", "https://wkhtmltopdf.org/status.html"))}
""",
    faq=[
        ("What replaced wkhtmltopdf?", "Most projects moved to headless Chrome (Puppeteer or Playwright), Gotenberg for a self-hosted API, or a hosted HTML to PDF API."),
        ("Is PDFShift free?", "It gives 50 free credits a month, per its FAQ, with paid plans for more."),
        ("How do I make 1,000 invoices as PDFs?", "Write one HTML invoice template with Handlebars placeholders, put the 1,000 invoices in a JSON array, and run the HTML to PDF API. It costs $3."),
    ],
    related=["html-to-pdf-api", "screenshotone-alternative"],
    free_tools=["markdown-to-pdf"],
)

# AppFollow ---------------------------------------------------------------------------------------------------
S = "appfollow-alternative"
page(
    slug=S, tool="app-store-reviews-scraper",
    title="AppFollow Alternative for Exporting App Reviews (Pay per Review)",
    h1="AppFollow alternatives when you just need the reviews",
    description="AppFollow is a full review management suite with monthly plans. If you need App Store and Google Play reviews exported to CSV, filtered and monitored, a pay-per-review API costs cents. Compared honestly.",
    lede="AppFollow, Appbot and AppFigures are review management platforms: reply from one inbox, AI tags, alerts, ASO. Teams that only need the reviews in a spreadsheet or a data warehouse pay for a lot they don't use.",
    body=f"""
<h2>Suite vs data</h2>
{table(["", "AppFollow", "Pandapi review scrapers"], [
    ["What it is", "Review management and ASO platform", "Data APIs: App Store, Google Play, Shopify"],
    ["Reply to reviews", "Yes, with AI replies", "No"],
    ["Competitor reviews", "Yes", "Yes, any public app"],
    ["CSV / Excel export", "On paid plans (Essential and up)", "Every run: CSV, Excel, JSON"],
    ["Price", "Free for 2 apps; Essential $179/month ($129 billed yearly)", "$0.15 per 1,000 App Store reviews, $0.10 per 1,000 Google Play reviews"],
    ["Monitoring", "Alerts", "Only-new-reviews runs on a schedule"],
    ["Insights", "Dashboards, tags", "Free summary per app: rating by version and country, top complaint phrases"],
])}

<h2>Keep a suite when</h2>
<p>Support teams answer reviews daily, you need ASO keyword tracking, or non-technical people need dashboards.</p>

<h2>Use the APIs when</h2>
<p>You want raw reviews for analysis, an LLM, a BI tool or a one-off competitor study. Monitoring 10 apps weekly costs a few cents a week.</p>
{curl("app-store-reviews-scraper", {"apps": ["https://apps.apple.com/us/app/duolingo-language-lessons/id570060128"], "countries": ["us", "gb"], "onlyNewReviews": True, "monitorKey": "competitors"})}
<p>Start with the {a('app-store-reviews-scraper', S, 'App Store Reviews Scraper')}, or see <a href="../export-google-play-reviews/">Google Play</a> and <a href="../shopify-app-reviews-export/">Shopify</a>.</p>
{sources(("AppFollow plans (AppFollow blog)", "https://appfollow.io/blog/new-plans-at-appfollow-and-how-to-choose-the-right-one"))}
""",
    faq=[
        ("Is there a cheaper alternative to AppFollow?", "If you need review data rather than a reply inbox, yes: pay-per-review APIs cost $0.10 to $0.15 per 1,000 reviews, and Apify's free credit covers tens of thousands a month."),
        ("Can I export competitor app reviews?", "Yes. App Store and Google Play reviews are public; paste the app link or name."),
        ("Does it tag sentiment?", "The free summary lists top complaint and praise phrases and the worst recent reviews. For full sentiment tagging, send the CSV to your own model or a suite."),
    ],
    related=["export-app-store-reviews", "export-google-play-reviews", "shopify-app-reviews-export"],
    free_tools=["json-to-excel"],
)

# google-play-scraper ----------------------------------------------------------------------------------------
S = "google-play-scraper-alternative"
page(
    slug=S, tool="google-play-reviews-scraper",
    title="google-play-scraper Alternatives: Hosted Google Play Reviews API",
    h1="google-play-scraper vs hosted Google Play review scrapers",
    description="The google-play-scraper library (Python and Node) is free and good. Here's when a hosted scraper is less work: many apps and languages, monitoring, schedules, no breakage. Apify options compared by users, rating and price.",
    lede="The open-source <code>google-play-scraper</code> packages (Python and npm) are how most people start. They're free and they work, until you need many languages, a schedule, or a fix the morning Google changes its page.",
    body=f"""
<h2>Library vs hosted</h2>
{table(["", "google-play-scraper (library)", "Hosted scraper"], [
    ["Cost", "Free", "Per review"],
    ["Setup", "pip/npm, your server", "None"],
    ["Breakage", "Wait for a maintainer fix", "The scraper's owner fixes it"],
    ["Several languages", "One call per language", "One run, merged"],
    ["Only new reviews", "Your own database", "Built in (Pandapi)"],
    ["Schedules and exports", "Your cron and code", "Apify schedules, CSV, Sheets, webhooks"],
])}

<h2>Hosted options on Apify</h2>
{table(["Actor", "Users (30 days)", "Rating", "Price", "Notes"], [
    ["thewolves/google-play-reviews-scraper", "556", "3.97 (8 reviews)", "$0.10 per 1,000", "One country and language per run"],
    ["neatrat/google-play-store-reviews-scraper", "434", "4.95 (10)", "From $0.10 to $0.15 per 1,000 by plan", "One app per run; star, keyword, date filters"],
    ["Pandapi Google Play Reviews", "new", "no reviews yet", "$0.10 per 1,000", "Many apps × languages, monitoring, free summary, no reviewer names"],
])}
<p>We're the newest of the three, and we built it to fix what users of the others asked for: several languages in one run and only-new-reviews monitoring.</p>
{curl("google-play-reviews-scraper", {"apps": ["com.duolingo", "com.babbel.mobile.android.en"], "languages": ["en", "es"], "maxReviewsPerApp": 1000, "onlyNewReviews": True})}
<p>Try the {a('google-play-reviews-scraper', S, 'Google Play Reviews Scraper')}.</p>
{sources(("Apify Store", "https://apify.com/store"), ("google-play-scraper on PyPI", "https://pypi.org/project/google-play-scraper/"))}
""",
    faq=[
        ("Is google-play-scraper free?", "Yes, the Python and Node libraries are open source. You run and maintain them yourself."),
        ("Why use a hosted scraper?", "No server, several languages merged in one run, monitoring of new reviews, schedules and exports, and someone else fixes it when Google changes its pages."),
        ("Which is cheapest?", "Pandapi and thewolves both charge $0.10 per 1,000 reviews with no start fee."),
    ],
    related=["export-google-play-reviews", "export-app-store-reviews", "appfollow-alternative"],
    free_tools=["json-to-excel"],
)

# SAM.gov ------------------------------------------------------------------------------------------------------
S = "sam-gov-api-alternative"
page(
    slug=S, tool="public-tenders-feed",
    title="SAM.gov API Alternative: No Key, No 10-Requests-a-Day Limit",
    h1="SAM.gov API alternatives for contract opportunities",
    description="The SAM.gov Opportunities API needs an API key and allows 10 requests a day for non-federal users without a role. Alternatives compared: the SAM.gov website, scrapers, and one feed with SAM.gov, TED, UK and Canada.",
    lede="SAM.gov's API is official and free, but it's built for occasional use: a personal key, and a low daily request limit unless your account has a role in SAM.gov. If you search every day across keywords, or also bid in Europe or Canada, here are the alternatives.",
    body=f"""
<h2>SAM.gov API limits</h2>
<p>GSA's documentation lists 10 requests a day for a non-federal user with no role in SAM.gov, and 1,000 a day for a non-federal user with a role (for example an entity registration) or a system account. Every request needs your API key.</p>

<h2>Alternatives</h2>
{table(["Option", "Coverage", "Cost", "Catch"], [
    ["SAM.gov website + saved searches", "US federal", "Free", "Manual; email alerts only"],
    ["SAM.gov API with a role", "US federal", "Free", "Needs an entity registration role; you write the code"],
    ["Apify SAM.gov scrapers", "US federal", "Roughly $1 to $3 per 1,000 items, some with start fees", "US only"],
    ["Commercial bid platforms", "US, more", "Subscriptions", "Priced per seat"],
    ["Pandapi Government Tenders API", "SAM.gov + TED (EU) + UK + CanadaBuys + World Bank", "$2 per 1,000 notices", "No state/local portals yet"],
])}

<h2>One query, five sources</h2>
{curl("public-tenders-feed", {"keywords": ["cybersecurity"], "sources": ["sam", "ted", "uk-fts", "canadabuys"], "naicsCodes": ["541512"], "postedWithinDays": 7, "onlyNew": True, "stateKey": "cyber"})}
<p>You get US opportunities with NAICS, PSC and set-aside, next to European, UK and Canadian tenders in the same columns. Try the {a('public-tenders-feed', S, 'Government Tenders API')}, or read the <a href="../government-tenders-api/">full guide</a>.</p>
{sources(("GSA Get Opportunities Public API", "https://open.gsa.gov/api/get-opportunities-public-api/"), ("GSA Exclusions API rate limits", "https://open.gsa.gov/api/exclusions-api"))}
""",
    faq=[
        ("What is the SAM.gov API rate limit?", "GSA documents 10 requests a day for a non-federal personal key with no SAM.gov role, and 1,000 a day with a role or a system account."),
        ("Can I search SAM.gov without an API key?", "On the SAM.gov website, yes. For data in bulk, use a feed or scraper that handles access for you, such as the Pandapi Government Tenders API."),
        ("Does it include NAICS and set-asides?", "Yes, for SAM.gov notices: NAICS, PSC, set-aside, response deadline and contacts where published."),
    ],
    related=["government-tenders-api", "company-jobs-api"],
    free_tools=["json-to-excel"],
)

# TheirStack ---------------------------------------------------------------------------------------------------
S = "theirstack-alternative"
page(
    slug=S, tool="company-jobs-tracker",
    title="TheirStack Alternative: Track Jobs at Companies You Name",
    h1="TheirStack alternatives for tracking company hiring",
    description="TheirStack sells job postings and tech-stack data from a large database by credits. If you track a known list of companies, reading their career sites live costs $1 per 1,000 jobs, with new and closed jobs tracked. Compared.",
    lede="Job-data providers answer \"which companies are hiring for X?\" across the whole market. Many sales and recruiting teams ask a narrower question: \"what are these 50 companies hiring for, and what changed this week?\" That one is cheaper to answer.",
    body=f"""
<h2>Compared</h2>
{table(["", "TheirStack", "fantastic-jobs Career Site API (Apify)", "Pandapi Company Jobs Tracker"], [
    ["Question it answers", "Search jobs and tech stacks across the market", "Search a database of career-site jobs", "All jobs at the companies you name"],
    ["Source", "Many job boards and sites", "Career sites, enriched", "Live from 11 ATS (Greenhouse, Lever, Ashby...)"],
    ["Pricing", "Free plan 200 API credits a month; paid from $59 a month; 1 credit per job", "Per job + start fee", "$1 per 1,000 jobs; summaries and closed jobs free"],
    ["New and closed jobs", "Filters by date", "Not stated", "Yes: new, closed, days open per watchlist"],
    ["Tech stack data", "Yes", "No", "No"],
    ["Workday, LinkedIn, Indeed", "Yes", "Workday via separate actor", "No"],
])}

<h2>Choose TheirStack when</h2>
<p>You're searching the market (every company using Snowflake and hiring data engineers), or you need tech-stack data.</p>

<h2>Choose a watchlist when</h2>
<p>You know the companies: your accounts, competitors or portfolio. Live career-site data is exact, and closed jobs plus days open tell you more than a snapshot.</p>
{curl("company-jobs-tracker", {"companies": ["Airbnb", "stripe.com", "https://jobs.ashbyhq.com/notion"], "trackChanges": True, "watchlistName": "accounts"})}
<p>Start with the {a('company-jobs-tracker', S, 'Company Jobs Tracker')}.</p>
{sources(("TheirStack plans", "https://theirstack.com/en/docs/pricing/plans"), ("TheirStack credits", "https://theirstack.com/en/docs/pricing/credits"), ("Apify Store", "https://apify.com/fantastic-jobs/career-site-job-listing-api"))}
""",
    faq=[
        ("Is there a free alternative to TheirStack?", "For known companies, the ATS job-board APIs (Greenhouse, Lever, Ashby) are free to call yourself. The Jobs Tracker reads 11 of them for $1 per 1,000 jobs, and Apify's free credit covers about 5,000 jobs a month."),
        ("How much does TheirStack cost?", "Per its docs, there's a free plan with 200 API credits a month for new users, and paid plans; a job in the job search endpoint costs 1 credit."),
        ("Can I see when a job was closed?", "Yes, with trackChanges on: closed jobs come with first-seen date, closed date and days open, free."),
    ],
    related=["company-jobs-api", "find-emails-from-websites"],
    free_tools=["json-to-excel", "csv-to-json"],
)

# PurgoMalum ---------------------------------------------------------------------------------------------------
S = "purgomalum-alternative"
page(
    slug=S, tool="profanity-filter",
    title="PurgoMalum Alternative: Multilingual Profanity Filter API",
    h1="PurgoMalum alternatives for profanity filtering",
    description="PurgoMalum is a free, English-focused profanity filter web service. Alternatives compared: bad-words libraries, Neutrino, WebPurify and Pandapi's 26-language filter with leetspeak detection and PurgoMalum-compatible endpoints.",
    lede="PurgoMalum is free and simple, which is why so many small apps use it. Teams move on when they get users in other languages, see leetspeak getting through, or need an SLA.",
    body=f"""
<h2>Compared</h2>
{table(["", "PurgoMalum", "bad-words / better-profanity", "Pandapi Profanity Filter"], [
    ["Cost", "Free, no SLA", "Free library", "$0.20 per 1,000 texts"],
    ["Languages", "English", "English", "26, auto-detect by script"],
    ["Leetspeak, spacing, f*ck", "Some character swaps", "Limited", "Leetspeak, spaced, stretched, self-censored, look-alike letters"],
    ["Scunthorpe / Password", "Safe-word list", "Varies", "Whole words; tested on 370,105 English words"],
    ["Modes", "Mask or replace; contains check", "Clean or check", "Mask, replace, remove or flag; standard or strict"],
    ["Bulk", "No", "Your loop", "Yes, or another dataset"],
    ["Migration", "", "", "PurgoMalum-compatible endpoints"],
])}

<h2>Stay with PurgoMalum when</h2>
<p>Your users write in English, volume is small and a missed word is not a problem.</p>

<h2>Switch when</h2>
<p>You moderate reviews, chat or usernames in several languages, or users are actively getting around the filter.</p>
{curl("profanity-filter", {"texts": ["Ce produit est de la merde", "great app, love it"], "languages": ["auto"], "mode": "flag"})}
<p>Try the {a('profanity-filter', S, 'Profanity Filter API')}. Commercial moderation services such as WebPurify add human review and image moderation, at subscription prices.</p>
{sources(("PurgoMalum", "https://www.purgomalum.com/"))}
""",
    faq=[
        ("Is PurgoMalum free?", "Yes. It's a free web service with no SLA."),
        ("Is there a multilingual profanity API?", "Yes. Pandapi's filter covers 26 languages with automatic detection, for $0.20 per 1,000 texts."),
        ("How hard is it to switch from PurgoMalum?", "The instant API has PurgoMalum-compatible endpoints, so it's a base-URL change plus your Apify token."),
    ],
    related=["profanity-filter-api"],
    free_tools=["csv-to-json"],
)

# ZipCodeAPI --------------------------------------------------------------------------------------------------
S = "zipcodeapi-alternative"
page(
    slug=S, tool="postal-code-lookup",
    title="ZipCodeAPI & Zippopotam Alternatives: Distance, Radius, Bulk",
    h1="ZipCodeAPI and Zippopotam.us alternatives",
    description="ZipCodeAPI.com allows 10 free requests an hour (US and Canada); Zippopotam.us does free lookups only. Alternatives for distance, radius and bulk postal code lookups in 124 countries, compared.",
    lede="Two free services cover most hobby needs: Zippopotam.us for lookups and ZipCodeAPI.com for US distance and radius. Their limits show up quickly in a store locator or a territory map.",
    body=f"""
<h2>Compared</h2>
{table(["", "Zippopotam.us", "ZipCodeAPI.com", "GeoNames files", "Pandapi ZIP & Postal Code API"], [
    ["Countries", "About 60", "US and Canada", "100+", "124"],
    ["Lookup", "Yes", "Yes", "Your code", "Yes"],
    ["Distance / radius", "No", "Yes", "Your code", "Yes, plus place to codes and nearest code to a point"],
    ["Free limit", "Free, no SLA", "10 requests an hour", "Free download (CC BY 4.0)", "About 16,000 results a month with Apify's $5 credit"],
    ["Paid", "None", "Paid plans", "None", "$0.30 per 1,000 results; not found free"],
    ["Bulk", "One per call", "One per call", "Yes", "Thousands per run, or instant API"],
])}
<p>For full UK, Canadian and Dutch codes, all open-data options (including ours) only have the first part of the code. Address-level data needs the national postal service's paid file.</p>
{curl("postal-code-lookup", {"radiusCenters": ["US 60601"], "radius": 25, "radiusUnit": "mi", "distancePairs": ["US 10001; US 94105"]})}
<p>Try the {a('postal-code-lookup', S, 'ZIP & Postal Code API')}, or read the <a href="../zip-code-api/">guide</a>.</p>
{sources(("ZipCodeAPI plans", "https://www.zipcodeapi.com/Plans"), ("Zippopotam.us", "https://www.zippopotam.us/"), ("GeoNames postal codes", "https://download.geonames.org/export/zip/"))}
""",
    faq=[
        ("Is ZipCodeAPI free?", "It has a free tier of 10 requests an hour, per its plans page, for US and Canadian codes."),
        ("What's a free ZIP code radius API?", "ZipCodeAPI's free tier for low volume, or Apify's free $5 monthly credit with Pandapi's API, which covers about 16,000 results."),
        ("Does it work outside the US?", "Yes, 124 countries from GeoNames data."),
    ],
    related=["zip-code-api"],
    free_tools=["csv-to-json", "json-to-excel"],
)

# Hacker News ---------------------------------------------------------------------------------------------------
S = "hacker-news-api-vs-scraper"
page(
    slug=S, tool="hacker-news-scraper",
    title="Hacker News API vs Algolia vs a Scraper: Which to Use",
    h1="Hacker News Firebase API vs Algolia search vs a scraper",
    description="Hacker News has two free APIs: Firebase (items by ID, live lists) and Algolia (search). What each does, their limits like the 1,000-result cap, and when a no-code scraper is easier.",
    lede="Both official HN APIs are free and need no key. They solve different problems, and neither exports a CSV for you.",
    body=f"""
{table(["", "Firebase API", "Algolia HN Search", "Pandapi HN Scraper"], [
    ["Endpoint", "hacker-news.firebaseio.com/v0", "hn.algolia.com/api/v1", "Apify actor"],
    ["Best for", "Live front page, one item by ID, comment trees", "Keyword search with date and points filters", "Exports and schedules without code"],
    ["Search", "No", "Yes", "Yes (uses Algolia)"],
    ["Limits", "One item per request", "1,000 hits per query", "Pages past 1,000 for you"],
    ["Output", "JSON per item", "JSON pages", "CSV, Excel, JSON"],
    ["Cost", "Free", "Free", "$0.20 per 1,000 items"],
])}

<h2>Firebase: the live site</h2>
{code('''curl https://hacker-news.firebaseio.com/v0/topstories.json
curl https://hacker-news.firebaseio.com/v0/item/8863.json''', 'bash')}
<h2>Algolia: search</h2>
{code('curl "https://hn.algolia.com/api/v1/search?query=sqlite&tags=show_hn&numericFilters=points>100"', 'bash')}
<h2>No code</h2>
<p>When you want "every Show HN about AI agents since June with 50+ points, as a spreadsheet, every Monday", the {a('hacker-news-scraper', S, 'Hacker News Scraper')} does the paging and export.</p>
{curl("hacker-news-scraper", {"searchQuery": "AI agents", "contentType": "show_hn", "minPoints": 50, "dateFrom": "2026-06-01", "maxItems": 1000})}
{sources(("HN Firebase API", "https://github.com/HackerNews/API"), ("Algolia HN Search API", "https://hn.algolia.com/api"))}
""",
    faq=[
        ("Is the Hacker News API free?", "Yes, both the Firebase API and the Algolia search API are free and need no key."),
        ("How do I get more than 1,000 search results?", "Split the query by date ranges with numericFilters on created_at_i, or use a scraper that does it for you."),
        ("Which API has comments?", "Both. Firebase gives comment trees by item ID; Algolia can search comments by keyword."),
    ],
    related=["hacker-news-api-export"],
    free_tools=["json-to-excel"],
)

# Firecrawl MCP / web MCP ------------------------------------------------------------------------------------------
S = "firecrawl-mcp-alternative"
page(
    slug=S, tool="pandapi-mcp-server",
    title="Firecrawl MCP Alternatives: Web, PDF and Data MCP Servers",
    h1="Firecrawl MCP alternatives for Claude, Cursor and other agents",
    description="MCP servers for web data compared: Firecrawl MCP, Apify's MCP server, Bright Data MCP and the Pandapi MCP server. Tools, pricing, context size and when each one fits.",
    lede="An MCP server gives your agent hands. For web work, the choices are a focused scraper (Firecrawl), a huge catalogue (Apify, Bright Data), or a small set of data tools. The trade-off is context size against reach.",
    body=f"""
{table(["", "Firecrawl MCP", "Apify MCP server", "Bright Data MCP", "Pandapi MCP"], [
    ["Tools", "Scrape, crawl, map, search, extract", "Generic tools plus any Apify actor", "Many (search, scrape, browser)", "14 data tools: web, PDF, screenshots, links, contacts, tenders, reviews, jobs, postal codes, HN, profanity"],
    ["Results", "In the answer", "call-actor, then fetch the dataset", "In the answer", "In the answer (long jobs return a run ID)"],
    ["Pricing", "Firecrawl credits (free 1,000 a month)", "Each actor's price", "Bright Data plans", "Server free; each call at that API's price"],
    ["PDFs and tables", "Via scrape", "Depends on the actor", "Via scrape", "Yes, tables to Excel"],
    ["Spend cap per call", "Not stated", "Not stated", "Not stated", "maxCostUsd, default $1"],
])}

<h2>Pick by job</h2>
<ul>
<li>Web research with search: Firecrawl or Bright Data.</li>
<li>Any of 10,000+ scrapers: Apify's MCP server.</li>
<li>Read docs and PDFs, check sites, pull reviews, tenders or jobs with small tool definitions and a cost cap: Pandapi.</li>
</ul>
<p>Add it in Claude or Cursor with <code>https://mcp.apify.com/?tools=blueberry_rainstorm/pandapi-mcp-server</code>. Details on the {a('pandapi-mcp-server', S, 'Pandapi MCP Server page')} and in our <a href="../mcp-server-for-web-and-pdf/">MCP guide</a>.</p>
{sources(("Firecrawl pricing", "https://www.firecrawl.dev/pricing"), ("Apify MCP", "https://mcp.apify.com/"))}
""",
    faq=[
        ("Is there a free Firecrawl MCP alternative?", "The Pandapi MCP server is free; tool calls are billed per result on your Apify account, and Apify's free plan includes $5 a month."),
        ("Which MCP server is best for PDFs?", "One with a real PDF tool. Pandapi's pdf_extract returns Markdown, text and tables (Excel), and reads scans with OCR."),
        ("Do MCP tools use up my context window?", "Yes, every tool definition is sent to the model. Smaller servers leave more room for your task; we measured our tools at about a sixth of the same actors through a generic connection."),
    ],
    related=["mcp-server-for-web-and-pdf", "firecrawl-alternative", "website-to-markdown-api"],
    free_tools=["html-to-markdown", "pdf-to-markdown"],
)

# Prisync (strategy v3: FOCUS product, written for store owners, no code) --------------------------------------
S = "prisync-alternative"
_TASK = "https://console.apify.com/create-task-from-example/Zhd4WMwiEeWgKkVXT"
page(
    slug=S, tool="shopify-products-price-monitor", published="2026-11-25", updated_text="25 November 2026",
    title="Prisync Alternative for Shopify Competitors: Price Alerts for Cents",
    h1="Prisync alternative: competitor price alerts for Shopify stores",
    description="Prisync starts at $99 a month for 100 products. If your competitors sell on Shopify or WooCommerce, you can get daily price, stock and new-product alerts for about $0.30 a month. Honest comparison, real sample, no code.",
    lede="Prisync is a solid price-tracking tool for retailers: you list your products, add each competitor's product URL, and it checks prices up to 3 times a day, from $99 a month. Many small Shopify brands only want one thing: an email when a competitor changes a price, launches a product or runs out of stock. That costs a few cents a month.",
    body=f"""
<h2>The short answer</h2>
<ul>
<li><b>Your competitors sell on Shopify or WooCommerce</b> (most direct-to-consumer brands do): paste their store links and get a daily change list for <b>about $0.30 a month</b>, with no product mapping. <a href="../competitor-price-monitoring/">See how it works</a>.</li>
<li><b>You need Amazon, Walmart or big retailers, repricing rules or a team dashboard</b>: stay with Prisync or a similar tool. Ours can't do those.</li>
</ul>

<h2>Side by side</h2>
{table(["", "Prisync", "Pandapi price alerts"], [
    ["Price", "$99 a month for 100 products, $199 for 1,000, $399 for 5,000 (URL-based plans)", "<b>about $0.30 a month</b> for 3 stores of 100 products checked daily; unchanged products free"],
    ["How you set it up", "Add your products, then each competitor's product URL", "Paste competitor store links; their whole catalog is watched"],
    ["A competitor launches a new product", "Not seen until you add its URL", "In your next daily alert"],
    ["Price, stock, new and removed product alerts", "Yes (email notifications on Premium)", "Yes, by email, Slack or Google Drive"],
    ["How often", "Up to 3 times a day", "As often as you schedule it (daily is typical)"],
    ["Which sites", "Any website, Amazon and marketplaces", "Shopify and WooCommerce stores only"],
    ["Repricing, MAP, dashboard", "Yes", "No"],
    ["Free to try", "Free trial", "Free: Apify's free plan includes $5 of credit every month, no card"],
])}

<h2>A real example</h2>
<p>On 25 November 2026, before Black Friday, we read 250 products from each of three Shopify shoe and apparel stores. This is the free store summary every run gives you:</p>
{table(["Store", "Products on sale", "Average discount", "Out of stock"], [
    ["Allbirds", "61%", "46% off", "1%"],
    ["Rothy's", "92%", "26% off", "3%"],
    ["Tentree", "80%", "25% off", "4%"],
])}
<p>The next runs list only what changed: each price drop or increase (old price, new price, % change), new and removed products, and items going out of or back in stock. <a href="../samples/sustainable-shoes-apparel-black-friday-prices/">Full sample report</a>.</p>
<p class="sources">Source: Apify run ZzxHjohCkQbkbLrLl, dataset p6ArXavmSVR7bb4LE, 25 Nov 2026. Nothing here is made up.</p>

<h2>Set it up in 3 minutes, no code</h2>
{steps([
    f'<a href="{_TASK}">Open the ready-made task</a> and create a free Apify account (Google sign-in works).',
    "Replace the example with your competitors' store links, one per line, and type your email in <b>Email me the report at</b>. Click <b>Save &amp; Start</b>.",
    "Click <b>Schedules</b>, then <b>Create new</b>, then <b>Daily</b>, and add your task. Every morning you get the changes by email.",
])}
<p>The <a href="../competitor-price-monitoring/">step-by-step guide with screenshots</a> also shows the Slack option.</p>

<h2>Want to see your own competitors first?</h2>
<p>Send us a competitor's store link and we'll run a free sample report for you: open a <a href="https://github.com/rabroubx-coder/pandapi-examples/issues/new?title=Free%20sample%20report%3A%20Competitor%20price%20alerts&amp;labels=sample-report">short request form</a> or message <a href="https://x.com/PandapiDev">@PandapiDev on X</a>.</p>

<h2>Where Prisync is the better choice</h2>
<ul><li>You compete with Amazon, Walmart or retailers that don't run on Shopify or WooCommerce.</li><li>You want automatic repricing rules or MAP monitoring.</li><li>A team needs one dashboard with your products matched to competitors'.</li></ul>

<div class="card"><p><b>For developers:</b> the same monitor is an API on Apify ({a('shopify-products-price-monitor', S, 'Competitor Price Monitor')}), with webhooks, n8n and Make integrations and an MCP server for AI agents.</p></div>
{sources(("Prisync pricing", "https://prisync.com/pricing/"), ("Apify pricing", "https://apify.com/pricing"), checked="25 November 2026")}
""",
    faq=[
        ("Is there a cheaper alternative to Prisync?", "If your competitors run on Shopify or WooCommerce, yes: a scheduled price monitor on Apify costs about $0.30 a month for 3 stores of 100 products checked daily, and Apify's free plan includes $5 of credit a month."),
        ("How much does Prisync cost?", "Its URL-based plans are listed at $99 a month for 100 products, $199 for 1,000 and $399 for 5,000, with higher prices for its other plans (checked 25 November 2026)."),
        ("Can I track competitor prices for free?", "Yes, within Apify's free $5 monthly credit: you pay $0.50 per 1,000 products on the first run and $1 per 1,000 changes after that, and unchanged products are free."),
        ("Does it work on Amazon?", "No. It reads the public catalog of Shopify and WooCommerce stores. For Amazon and big retailers, Prisync or a similar tool is the better pick."),
    ],
    related=["competitor-price-monitoring"],
    free_tools=[],
)

# GovWin IQ (strategy v3: FOCUS tender alerts, written for small bid teams, no code) -----------------------------
S = "govwin-alternative"
_TASK = "https://console.apify.com/create-task-from-example/hdv8OVr0yH8q0Oqhg"
page(
    slug=S, tool="public-tenders-feed", published="2026-11-26", updated_text="26 November 2026",
    title="GovWin IQ Alternative for Small Bid Teams: Daily Tender Alerts for Cents",
    h1="GovWin alternative: daily tender alerts on your keywords for small bid teams",
    description="GovWin IQ is an annual, quote-based subscription. If you mainly need new tenders on your keywords every morning from SAM.gov, the EU, the UK, Canada and the World Bank, a daily alert costs about $0.60 a month. Honest comparison, real sample, no code.",
    lede="Deltek GovWin IQ is the heavyweight of government market intelligence: analyst research, forecasts, contract history and buyer contacts across US federal, state and local and Canadian markets, sold as an annual subscription on quote. Many small bid teams use only one part of it: a morning list of new tenders that match their keywords. That part costs cents.",
    body=f"""
<h2>The short answer</h2>
<ul>
<li><b>You want new tenders on your keywords every morning</b>, from US federal (SAM.gov), the EU (TED), the UK, Canada and World Bank projects: a daily alert costs <b>about $0.60 a month</b>. <a href="../government-tender-alerts/">See how it works</a>.</li>
<li><b>You sell to US state and local government, or you need forecasts before solicitation, contract history, analyst reports and buyer contacts</b>: GovWin IQ (or GovSpend) is the right tool. Ours does none of that.</li>
</ul>

<h2>Side by side</h2>
{table(["", "GovWin IQ", "Pandapi tender alerts"], [
    ["Price", "No public price. Annual subscription, quoted by market, seats and modules (third-party estimates start around $5,000 a year)", "<b>about $0.60 a month</b> for a daily alert that finds about 10 new tenders a day"],
    ["US federal (SAM.gov)", "Yes", "Yes"],
    ["US state, local and education", "Yes (separate package)", "No"],
    ["Canada", "Yes (federal, provincial and local)", "Federal (CanadaBuys)"],
    ["EU (TED), UK (Contracts Finder, Find a Tender), World Bank", "Not its focus", "Yes, in the same list"],
    ["Daily email with only new tenders", "Yes", "Yes, by email, Slack or Google Drive"],
    ["Forecasts, contract history, buyer contacts, analyst research", "Yes", "No"],
    ["Contract and setup", "Annual contract, sales call", "No contract. Apify's free plan includes $5 of credit every month, no card"],
])}

<h2>A real example</h2>
<p>On 25 November 2026 we ran the alert for a cybersecurity firm (keywords: cybersecurity, cyber security, penetration testing). The email headline: <b>27 new tenders on your keywords, 4 closing within 7 days</b>. A few rows:</p>
{table(["Tender", "Buyer", "Where", "Deadline", "Value"], [
    ['<a href="https://ted.europa.eu/en/notice/-/detail/817289-2026">Provision of Cyber Security Services</a>', "Malta Information Technology Agency", "Malta · TED", "5 Jan 2027", "about $578,462"],
    ['<a href="https://ted.europa.eu/en/notice/-/detail/816280-2026">Renewal and support of the Darktrace cybersecurity platform</a>', "Tusla Child and Family Agency", "Ireland · TED", "8 Jan 2027", "about $6,561,000"],
    ['<a href="https://www.merx.com/public/solicitations/4207909153/abstract?language=EN">IT and OT Cybersecurity Source List</a>', "Defence Construction Canada", "Canada · CanadaBuys", "12 Jan 2027", "not published"],
    ['<a href="https://sam.gov/opp/5ed6173d3e954a7e824b7e2513930985/view">PCI DSS compliance validation, penetration testing and ASV scanning</a>', "US Army (W6QK ACC-APG)", "US · SAM.gov", "7 Dec 2026", "not published"],
])}
<p>Each row also has the notice type, days left, CPV or NAICS codes and a link to the official notice. <a href="../samples/cybersecurity-government-tenders/">Full sample report</a>, or the <a href="../samples/janitorial-cleaning-government-tenders/">cleaning services one</a> (43 new tenders the same morning).</p>
<p class="sources">Source: Apify run C0k3XcBWbtfQfCmah, dataset JGwiRk93bLCYuWRh3, 25 Nov 2026. Values are converted to US dollars from the currency the buyer published. Nothing here is made up.</p>

<h2>Set it up in 3 minutes, no code</h2>
{steps([
    f'<a href="{_TASK}">Open the ready-made task</a> and create a free Apify account (Google sign-in works).',
    "Type your keywords (and words to exclude, countries or NAICS/CPV codes if you like) and your email in <b>Email me the report at</b>. Click <b>Save &amp; Start</b>.",
    "Click <b>Schedules</b>, then <b>Create new</b>, then <b>Daily</b>, and add your task. Every morning you get only the tenders you haven't seen.",
])}
<p>The <a href="../government-tender-alerts/">step-by-step guide with screenshots</a> also shows the Slack option.</p>

<h2>Want to see your own keywords first?</h2>
<p>Tell us your keywords and countries and we'll run a free sample report for you: open a <a href="https://github.com/rabroubx-coder/pandapi-examples/issues/new?title=Free%20sample%20report%3A%20Tender%20alerts&amp;labels=sample-report">short request form</a> or message <a href="https://x.com/PandapiDev">@PandapiDev on X</a>.</p>

<h2>Where GovWin IQ is the better choice</h2>
<ul><li>You sell to US state, local or education buyers.</li><li>You want to hear about opportunities before the solicitation is published, from analyst research and forecasts.</li><li>You need past contract values, incumbents and buyer contacts to plan a bid.</li></ul>

<div class="card"><p><b>For developers:</b> the same feed is an API on Apify ({a('public-tenders-feed', S, 'Government Tenders API')}) with one schema for all six portals, plus webhooks, n8n and Make integrations. See also the <a href="../government-tenders-api/">developer guide</a>.</p></div>
{sources(("Deltek GovWin IQ", "https://www.deltek.com/en/govwin"), ("GovWin IQ for Canada", "https://www.deltek.com/en/government-contracting/govwin/canada"), ("Third-party GovWin pricing estimate (Tomba)", "https://tomba.io/blog/deltek-govwin-iq-pricing-reviews-pros-and-cons"), ("Apify pricing", "https://apify.com/pricing"), checked="26 November 2026")}
""",
    faq=[
        ("Is there a cheaper alternative to GovWin IQ?", "For daily alerts on new tenders, yes: a scheduled alert covering SAM.gov, TED, the UK, CanadaBuys and the World Bank costs about $0.60 a month for about 10 new tenders a day, inside Apify's free $5 monthly credit. For forecasts, state and local coverage and contract history, GovWin IQ or GovSpend are still the tools to compare."),
        ("How much does GovWin IQ cost?", "Deltek doesn't publish prices. It sells annual subscriptions quoted by market (federal, state and local, Canada), number of users and modules. Third-party estimates start around $5,000 a year."),
        ("Can I get government tender alerts for free?", "Yes. SAM.gov, TED and CanadaBuys each have free saved-search emails for their own portal. The alert here puts all of them in one email for about $0.60 a month, which Apify's free credit covers."),
        ("Does it cover US state and local bids?", "No. In the US it covers federal notices from SAM.gov."),
    ],
    related=["government-tender-alerts", "government-tenders-api"],
    free_tools=[],
    cta_line="<b>Tender alerts</b>: a daily alert with about 10 new tenders costs about $0.60 a month. Tenders filtered out or already sent are free, and Apify's free plan gives you $5 of credit every month.",
)

# Price2Spy (strategy v3: FOCUS price monitor, written for store owners, no code; real Black Friday changes) ------
S = "price2spy-alternative"
_TASK = "https://console.apify.com/create-task-from-example/Zhd4WMwiEeWgKkVXT"
page(
    slug=S, tool="shopify-products-price-monitor", published="2026-11-27", updated_text="27 November 2026",
    title="Price2Spy Alternative for Shopify Competitors: Daily Price Alerts",
    h1="Price2Spy alternative: daily competitor price alerts for Shopify stores",
    description="Price2Spy no longer lists its plan prices publicly. If your competitors sell on Shopify or WooCommerce, daily price, stock and new-product alerts cost about $0.30 a month. Honest comparison with real Black Friday changes.",
    lede="Price2Spy is a mature price-monitoring tool for retailers and brands: it matches your products to competitors' pages on almost any site, including marketplaces, and adds repricing and MAP monitoring. Since spring 2026 it asks you to start a trial or contact sales instead of listing prices. If your competitors run on Shopify or WooCommerce and you just want an email when they cut prices, launch products or sell out, that costs a few cents a month.",
    body=f"""
<h2>The short answer</h2>
<ul>
<li><b>Your competitors sell on Shopify or WooCommerce</b>: paste their store links and get a daily list of what changed for <b>about $0.30 a month</b>, with no product matching. <a href="../competitor-price-monitoring/">See how it works</a>.</li>
<li><b>You compete on Amazon or marketplaces, or you need repricing, MAP checks or several price checks a day</b>: Price2Spy (or Prisync) is the better tool.</li>
</ul>

<h2>Side by side</h2>
{table(["", "Price2Spy", "Pandapi price alerts"], [
    ["Price", "Not listed publicly since spring 2026 (Starter and Basic were $39.95 and $157.95 a month before that); Premium on request; free trial", "<b>about $0.30 a month</b> for 3 stores of 100 products checked daily; unchanged products free"],
    ["How you set it up", "Import your products, then match each one to competitors' pages (Quick match, Automatch on higher tiers)", "Paste competitor store links; their whole catalog is watched"],
    ["A competitor launches a new product", "Not seen until it is matched", "In your next daily alert"],
    ["Price drops and increases, stock, new and removed products", "Yes (daily digest on Starter, instant alerts on Basic)", "Yes, by email, Slack or Google Drive"],
    ["Which sites", "Almost any website and marketplaces", "Shopify and WooCommerce stores only"],
    ["Repricing, MAP monitoring, dashboard", "Yes", "No"],
    ["Contract", "Monthly plans, sales contact for larger tiers", "None. Apify's free plan includes $5 of credit every month, no card"],
])}

<h2>A real example: Black Friday 2026</h2>
<p>We set up daily alerts on six well-known Shopify brands on 25 November and checked again on Black Friday morning, 27 November. This is what the second alert reported:</p>
{table(["Store", "What changed", "Example"], [
    ["Tentree", "Prices cut on <b>135 products</b> (median 12.5% off, up to 20%)", "Moray Sweater 148 to 118.40, 20% off"],
    ["Kylie Cosmetics", "Prices cut on <b>16 products</b> (median 30% off)", "Skin Tint Blurring Elixir $35 to $23.80, 32% off"],
    ["Rothy's", "Prices cut on <b>18 clogs</b> (16.8% off) and sizes sold out on 47 products", "The Cozy Clog $119 to $99"],
    ["SKIMS", "No price cuts; <b>33 items</b> sold out", "NikeSKIMS Waffle Racer sold out"],
    ["Allbirds", "No new cuts (it was already on sale); sizes sold out on 29 products", ""],
])}
<p>Every price row has the old price, the new price and the % change, with a link to the product. Prices are in each store's own currency. Full reports: <a href="../samples/sustainable-shoes-apparel-black-friday-prices/">shoes and apparel</a> and <a href="../samples/beauty-fashion-black-friday-prices/">beauty and fashion</a>.</p>
<p class="sources">Source: Apify runs AjuzoIwqz4ND0DFe5 (dataset xpm1HG3aKSMeH8R3r) and eHxVRcjll7YmXybW7 (dataset zicTv8e2t4qHNXHKc), 27 Nov 2026, compared with the 25 Nov baseline. Nothing here is made up.</p>

<h2>Set it up in 3 minutes, no code</h2>
{steps([
    f'<a href="{_TASK}">Open the ready-made task</a> and create a free Apify account (Google sign-in works).',
    "Replace the example with your competitors' store links, one per line, and type your email in <b>Email me the report at</b>. Click <b>Save &amp; Start</b>.",
    "Click <b>Schedules</b>, then <b>Create new</b>, then <b>Daily</b>, and add your task. Every morning you get only what changed.",
])}
<p>The <a href="../competitor-price-monitoring/">step-by-step guide with screenshots</a> also shows the Slack option.</p>

<h2>Want to see your own competitors first?</h2>
<p>Send us a competitor's store link and we'll run a free sample report for you: open a <a href="https://github.com/rabroubx-coder/pandapi-examples/issues/new?title=Free%20sample%20report%3A%20Competitor%20price%20alerts&amp;labels=sample-report">short request form</a> or message <a href="https://x.com/PandapiDev">@PandapiDev on X</a>.</p>

<h2>Where Price2Spy is the better choice</h2>
<ul><li>Your competitors sell on Amazon, eBay or sites that don't run on Shopify or WooCommerce.</li><li>You want repricing rules, MAP monitoring or up to 8 price checks a day.</li><li>A team needs a dashboard with your products matched to competitors' and an account manager.</li></ul>

<div class="card"><p><b>For developers:</b> the same monitor is an API on Apify ({a('shopify-products-price-monitor', S, 'Competitor Price Monitor')}), with webhooks, n8n and Make integrations and an MCP server for AI agents. See also our <a href="../prisync-alternative/">Prisync comparison</a>.</p></div>
{sources(("Price2Spy pricing tiers", "https://www.price2spy.com/pricing.html"), ("Price2Spy pricing history (PricingSaaS)", "https://pricingsaas.com/companies/price2spy"), ("Apify pricing", "https://apify.com/pricing"), checked="27 November 2026")}
""",
    faq=[
        ("Is there a cheaper alternative to Price2Spy?", "If your competitors run on Shopify or WooCommerce, yes: a scheduled price monitor on Apify costs about $0.30 a month for 3 stores of 100 products checked daily, inside Apify's free $5 monthly credit."),
        ("How much does Price2Spy cost?", "Price2Spy stopped listing plan prices publicly in spring 2026; you start a free trial or ask for a quote. Before that, its Starter plan was listed at $39.95 a month and Basic at $157.95 (checked 27 November 2026)."),
        ("Do I have to match my products to competitors' products?", "No. You paste a competitor's store link and every product in its catalog is watched. The daily alert lists price changes, new and removed products and stock changes."),
        ("Does it work on Amazon?", "No. It reads the public catalog of Shopify and WooCommerce stores. For Amazon and marketplaces, Price2Spy or Prisync is the better pick."),
    ],
    related=["prisync-alternative"],
    free_tools=[],
)
