"""One SEO page per paid Pandapi API (kind "api"). Facts checked 2026-11-21. See SEO-PAGES.md."""
from seo_pages import a, code, curl, python, table, steps

PAGES = []


def page(**kw):
    kw.setdefault("kind", "api")
    PAGES.append(kw)


# 1. Website to Markdown ------------------------------------------------------------------------
S = "website-to-markdown-api"
page(
    slug=S, tool="web-page-to-markdown",
    title="Website to Markdown API for RAG and LLMs ($1 per 1,000 pages)",
    h1="Website to Markdown for RAG and LLMs: crawl, clean, chunk",
    description="Turn a URL list, a sitemap or a whole docs site into clean Markdown for RAG and LLMs. Main content only, JavaScript pages, token counts and chunks with heading paths. $1 per 1,000 pages.",
    lede="You want a website in your vector database or in a prompt, not its menus, cookie banners and footers. Here is the free way for a few pages, and the API way for a whole site: a list of URLs, a sitemap or a crawl from one start page, returned as clean Markdown with chunks ready to embed.",
    body=f"""
<h2>The free way: one page at a time</h2>
<p>For a handful of pages you don't need an API. Open the page, select the article, copy it and paste it into our free <a href="../html-to-markdown/">HTML to Markdown converter</a>. It runs in your browser, keeps only the main content (the same Readability engine as Firefox Reader View) and gives you GitHub-flavored Markdown with tables and code blocks.</p>
<p>In Python, <code>requests</code> + <code>readability-lxml</code> + <code>markdownify</code> does the same for static pages. It stops working when the site renders with JavaScript (React, Vue, most modern docs), when you need every page of a site, or when you need the text split into chunks for embeddings.</p>

<h2>The API way: a whole site in one run</h2>
{steps([
    f"Open {a('web-page-to-markdown', S, 'Website to Markdown on Apify')} and sign in (the free plan needs no card).",
    "Give it <b>URLs</b>, a <b>sitemap.xml</b>, or one start URL with <b>Crawl</b> on. Crawl scope <code>path</code> stays inside the section you start from, e.g. only <code>/docs/</code>.",
    "Set <b>chunkSize</b> (for example 800 tokens) if you want RAG chunks. Each chunk carries its heading path and a link to the nearest #anchor, so answers can cite the exact section.",
    "Run it. Download Markdown, JSON or CSV, or call it from code, n8n, Make or an AI agent.",
])}
<p>Calling it from code returns the pages in the same HTTP response:</p>
{curl("web-page-to-markdown", {"urls": [{"url": "https://docs.python.org/3/tutorial/"}], "crawl": True, "crawlScope": "path", "maxPages": 200, "chunkSize": 800})}
{python("web-page-to-markdown", {"sitemapUrls": [{"url": "https://react.dev/sitemap.xml"}], "maxPages": 500, "chunkSize": 800}, '    for chunk in item.get("chunks", []):\n        print(chunk["headingPath"], chunk["approxTokens"], chunk["url"])')}

<p class="example">Full working example on GitHub: <a href="https://github.com/rabroubx-coder/pandapi-examples/tree/main/rag-docs-sync">keep a RAG index in sync with a docs site</a> (MIT licence, copy and adapt).</p>
<h2>What you get for each page</h2>
<p>One row per page: <code>url</code>, <code>title</code>, <code>description</code>, <code>language</code>, <code>canonicalUrl</code>, <code>markdown</code>, <code>wordCount</code>, <code>approxTokens</code>, whether a browser was needed, and (with chunking on) <code>chunks</code> with <code>headingPath</code>, <code>text</code>, <code>approxTokens</code>, <code>anchor</code> and <code>url</code>. Code blocks keep their language, tables stay Markdown tables, and docs tabs (MkDocs, Docusaurus, Mintlify, sphinx-design) can be "selected only" or "all tabs".</p>

<h2>What it costs</h2>
{table(["Job", "Pages", "Price"], [
    ["Blog of 120 posts", "120", "$0.12"],
    ["Docs site from its sitemap", "500", "$0.50"],
    ["Nightly re-sync of 2,000 docs pages", "60,000 a month", "$60 a month"],
    ["Pages that fail (404, blocked, timeout)", "any", "free"],
])}
<p>No subscription and no start fee. Apify's free plan includes $5 of usage a month, so about 5,000 pages a month cost you nothing.</p>

<h2>Where it is not the right tool</h2>
<ul>
<li>Sites behind a login or a hard bot wall: the API doesn't log in or solve CAPTCHAs.</li>
<li>Web <i>search</i> (find pages for a query): it converts pages you name or crawl; pair it with a search API.</li>
<li>Structured extraction with an LLM ("give me the price as JSON"): it gives you clean Markdown to feed your own model.</li>
</ul>
<p>Comparing options? Read <a href="../firecrawl-alternative/">Firecrawl alternatives</a> and <a href="../jina-reader-alternative/">Jina Reader alternatives</a>.</p>
""",
    faq=[
        ("How do I convert a whole website to Markdown?", "Give the API the start URL with Crawl on, or the site's sitemap.xml. It follows links inside the scope you choose, converts each page's main content to Markdown and returns one row per page. Set maxPages to cap the run."),
        ("Does it work on JavaScript sites?", "Yes. renderMode auto fetches plain HTML first and switches to a real browser only when a page needs JavaScript, so static pages stay fast and cheap and React or Vue pages still come out complete."),
        ("How big should RAG chunks be?", "500 to 1,000 tokens with about 100 tokens of overlap is a good start for most embedding models. Chunks are cut at headings first, and each one carries its heading path so the model knows the context."),
        ("Can I keep my index in sync?", "Yes. Schedule the run daily or weekly on Apify and compare each page's text or token count with what you stored. You pay $1 per 1,000 pages each time, failed pages free."),
        ("Is there a free option?", "For a few pages, use our free HTML to Markdown converter in the browser. For bulk runs, Apify's free plan gives $5 of credit a month, about 5,000 pages."),
    ],
    related=["firecrawl-alternative", "jina-reader-alternative", "mcp-server-for-web-and-pdf"],
    free_tools=["html-to-markdown", "link-extractor"],
)

# 2. PDF tables to Excel --------------------------------------------------------------------------
S = "extract-tables-from-pdf-to-excel"
page(
    slug=S, tool="pdf-to-text-markdown",
    title="Extract Tables from PDF to Excel in Bulk (free way + API)",
    h1="Extract tables from PDFs to Excel, in bulk",
    description="How to get tables out of PDFs into Excel or CSV: the free way for one file, and an API for hundreds of bank statements, reports or invoices. Borderless tables, multi-page tables joined, numbers as numbers.",
    lede="Copying a PDF table into Excel usually gives you one long column, merged cells or numbers stored as text. Here's what works for one file, what works for Python users, and how to turn hundreds of PDFs into clean spreadsheets without touching each one.",
    body=f"""
<h2>One PDF: try the free routes first</h2>
<ul>
<li><b>Excel itself</b> (Microsoft 365, Windows): Data › Get Data › From File › From PDF. Power Query lists the tables it finds. Good for clean, ruled tables; weak on borderless ones and tables that run across pages.</li>
<li><b>Online converters</b> (Smallpdf, iLovePDF, Adobe): fine for one or two files a day on the free tiers, but you upload the document, and scanned PDFs need a paid plan.</li>
<li><b>Python</b>: <code>camelot</code> (lattice mode for ruled tables, stream for whitespace tables) or <code>tabula-py</code> (needs Java). Great when you can tune them per layout; see <a href="../camelot-vs-tabula/">Camelot vs Tabula</a>.</li>
</ul>
<p>If you only need the text, our free <a href="../pdf-to-markdown/">PDF to Markdown converter</a> works in your browser with no upload and no limit.</p>

<h2>Hundreds of PDFs: the API way</h2>
{steps([
    f"Open the {a('pdf-to-text-markdown', S, 'PDF to Excel API on Apify')}.",
    "Add PDF links, or upload a file in the console. Leave <b>tableDetection</b> on <code>all</code> (ruled and borderless tables).",
    "Pick <b>xlsx</b> or <b>csv</b>. You get a workbook per PDF (one sheet per table) and a <code>tables.xlsx</code> with every table from the run, so 200 statements land in one file. Multi-page tables are joined and wrapped lines merged.",
    "Run. Each PDF row has an <code>excelUrl</code> to the workbook and the tables as JSON, so you can also load them straight into a database.",
])}
{curl("pdf-to-text-markdown", {"urls": [{"url": "https://example.com/statements/2026-10.pdf"}], "tableDetection": "all", "spreadsheetOutput": "xlsx", "numbersAsNumbers": True, "includeMarkdown": False})}
{python("pdf-to-text-markdown", {"urls": [{"url": "https://example.com/report.pdf"}], "spreadsheetOutput": "xlsx"}, '    print(item["fileName"], item["tableCount"], item.get("excelUrl"))')}

<p class="example">Full working example on GitHub: <a href="https://github.com/rabroubx-coder/pandapi-examples/tree/main/pdf-tables-to-excel">PDF tables to Excel in Python</a> (MIT licence, copy and adapt).</p>
<h2>What makes PDF tables hard (and what the API does about it)</h2>
{table(["Problem", "What usually happens", "What the API does"], [
    ["No ruling lines (bank statements)", "Columns run together", "Finds columns from text alignment"],
    ["Table continues on the next page", "Two tables, header repeated", "Joins them into one table"],
    ["Wrapped cell text", "Extra half-empty rows", "Merges wrapped lines into the cell"],
    ["1,234.56 and (12.00)", "Stored as text in Excel", "Real numbers, negatives kept"],
    ["Scanned pages", "Nothing extracted", "OCR text in 12 languages (tables from scans are not detected yet)"],
])}

<h2>What it costs</h2>
<p>$3 per 1,000 PDFs, whatever their page count, plus $5 per 1,000 pages when OCR runs on scanned pages. 300 monthly bank statements cost $0.90. PDFs that fail are free. Apify's free $5 monthly credit covers about 1,600 PDFs.</p>

<h2>Limits, honestly</h2>
<ul>
<li>Tables inside scanned images come out as OCR text, not as spreadsheet cells.</li>
<li>Very complex headers (three levels, merged across groups) may need a quick fix in Excel.</li>
<li>Password-protected PDFs need the password in the input.</li>
</ul>
""",
    faq=[
        ("How do I convert a PDF table to Excel for free?", "In Microsoft 365, use Data › Get Data › From PDF. For text only, our free PDF to Markdown tool works in the browser. For many files, Apify's free $5 monthly credit covers about 1,600 PDFs through the API."),
        ("Can it convert bank statements to Excel?", "Yes. Bank statements are usually borderless tables over several pages, which is the case the API was built for: columns from alignment, pages joined, amounts as real numbers."),
        ("Does it work on scanned PDFs?", "It reads scanned pages with OCR in 12 languages and returns the text. Table cells are not detected on scanned pages yet."),
        ("Can I get CSV instead of Excel?", "Yes. Set spreadsheetOutput to csv. You also get every table as JSON rows in the dataset."),
        ("Are my PDFs stored?", "Files are processed in your own Apify account and the results stay in your storage, which you can delete at any time."),
    ],
    related=["camelot-vs-tabula", "convertio-alternative", "mcp-server-for-web-and-pdf"],
    free_tools=["pdf-to-markdown", "html-table-to-excel", "json-to-excel"],
)

# 3. Government tenders -----------------------------------------------------------------------------
S = "government-tenders-api"
page(
    slug=S, tool="public-tenders-feed",
    title="Government Tenders API: SAM.gov, TED, UK, Canada in One Feed",
    h1="Government tenders API: SAM.gov, TED EU, UK, Canada and the World Bank in one feed",
    description="One API for public tenders and contract awards from SAM.gov, TED (EU), UK Find a Tender and Contracts Finder, CanadaBuys and the World Bank. Keyword, country, CPV and NAICS filters, daily alerts. $2 per 1,000 notices.",
    lede="Bidders, BD teams and consultants check five portals every morning, each with its own search, codes and format. This page shows how to read each official source for free, and how to get all of them as one daily feed with one schema.",
    body=f"""
<h2>The free way: the official portals and their APIs</h2>
{table(["Source", "Covers", "Free access", "Catch"], [
    ["SAM.gov", "US federal opportunities", "Opportunities API with a personal API key", "GSA documents 10 requests a day for a non-federal user with no SAM.gov role"],
    ["TED", "EU/EEA tenders above EU thresholds", "Search API, no key for search", "Its own query syntax and eForms fields"],
    ["UK Find a Tender + Contracts Finder", "UK public sector", "OCDS APIs, no key", "Two services, rate limits, OCDS nesting"],
    ["CanadaBuys", "Canadian federal tenders", "Open data CSV files", "Daily files, not a search API"],
    ["World Bank", "Projects in 100+ countries", "Procurement notices API", "Different fields again"],
])}
<p>If you watch one country, the official portal and its email alerts are enough. The work starts when you need several countries, the same keywords everywhere, and one spreadsheet.</p>

<h2>The API way: one feed, one schema</h2>
{steps([
    f"Open the {a('public-tenders-feed', S, 'Government Tenders API on Apify')}.",
    "Enter keywords (e.g. <code>software</code>, <code>cybersecurity</code>), countries, and optionally CPV, NAICS or UNSPSC codes, a minimum value and how many days must be left.",
    "Turn on <b>onlyNew</b> with a <b>stateKey</b> name to get only notices you haven't seen, and schedule the run daily on Apify.",
    "Send the results to Google Sheets, Slack or email with Apify's integrations, or call it from n8n, Make or code.",
])}
{curl("public-tenders-feed", {"keywords": ["software", "cloud", "cybersecurity"], "countries": ["US", "GB", "DE", "FR", "CA"], "noticeTypes": ["tender", "pre-notice"], "postedWithinDays": 7, "minDaysLeft": 10, "minValueUsd": 50000, "onlyNew": True, "stateKey": "it-tenders"})}
{python("public-tenders-feed", {"keywords": ["translation services"], "sources": ["ted", "uk-fts", "canadabuys"], "postedWithinDays": 3}, '    print(item["source"], item["title"], item.get("deadline"), item.get("valueUsd"))')}

<p class="example">Full working example on GitHub: <a href="https://github.com/rabroubx-coder/pandapi-examples/tree/main/government-tenders-feed">a daily government tenders feed</a> (MIT licence, copy and adapt).</p>
<h2>What each notice looks like</h2>
<p>Every source is mapped to the same fields: title, buyer, country, notice type (tender, pre-notice, award), published date, deadline and days left, estimated value in the original currency and in USD/EUR, CPV/NAICS/UNSPSC codes, set-aside (SAM), a description, the link to the official notice, and buyer contacts where the portal publishes them. Expired tenders are hidden by default.</p>

<h2>What it costs</h2>
<p>$2 per 1,000 notices, no start fee. A daily alert that finds 40 new notices costs $0.08 a day, about $2.40 a month. For comparison, commercial bid databases are sold as subscriptions (GovWin and similar tools are priced per seat per year). Apify's free $5 credit covers about 2,500 notices a month.</p>

<h2>Limits</h2>
<ul>
<li>US state and local portals, Australia's AusTender and UNGM are not included yet.</li>
<li>Tender documents (attachments) are linked, not downloaded.</li>
<li>Smaller EU tenders below the EU thresholds only appear if the country also publishes them to TED.</li>
</ul>
<p>Only need US data? Read <a href="../sam-gov-api-alternative/">SAM.gov API alternatives</a>.</p>
""",
    faq=[
        ("Is there a free government tenders API?", "Yes, each portal has one: SAM.gov (with an API key), TED, UK Find a Tender and Contracts Finder, CanadaBuys open data and the World Bank. They use different formats. The Pandapi feed combines them for $2 per 1,000 notices, and Apify's free credit covers about 2,500 notices a month."),
        ("How do I get daily tender alerts?", "Turn on onlyNew with a stateKey, schedule the run daily on Apify, and add an email, Slack or Google Sheets integration. You only pay for new notices."),
        ("Can I filter by CPV or NAICS codes?", "Yes. CPV prefixes work on TED and UK notices, NAICS and PSC on SAM.gov, UNSPSC and GSIN on CanadaBuys. Sources that can't apply a filter are skipped and the run says why."),
        ("Does it include contract awards?", "Yes. Add award to noticeTypes to get awarded contracts with the winner and value where the portal publishes them."),
    ],
    related=["sam-gov-api-alternative", "company-jobs-api"],
    free_tools=["json-to-excel", "csv-to-json"],
)

# 4. App Store reviews --------------------------------------------------------------------------------
S = "export-app-store-reviews"
page(
    slug=S, tool="app-store-reviews-scraper",
    title="Export App Store Reviews to CSV (any app, any country)",
    h1="Export App Store reviews to CSV or Excel, for any app",
    description="How to export Apple App Store reviews to CSV: the free RSS way (500 per country) and an API for many apps and countries, with star, date and keyword filters, monitoring and a free insights summary. $0.15 per 1,000 reviews.",
    lede="App Store Connect lets you read your own app's reviews but has no CSV button, and it doesn't cover competitors at all. Here are the free ways to export App Store reviews, where they stop, and how to get reviews from every country into one file.",
    body=f"""
<h2>Free way 1: App Store Connect (your own apps)</h2>
<p>You can read and reply to reviews in App Store Connect, and the App Store Connect API has a <code>customerReviews</code> endpoint. It needs an API key and covers only apps in your developer account.</p>

<h2>Free way 2: Apple's public reviews feed (any app)</h2>
<p>Apple serves each app's recent reviews as a public feed, 50 per page and 10 pages at most:</p>
{code('https://itunes.apple.com/us/rss/customerreviews/page=1/id=570060128/sortby=mostrecent/json', 'text')}
<p>Loop pages 1 to 10, read <code>feed.entry</code>, and write date, stars, version, title and text to CSV. It's free and works for any public app. The catch: the feed stops at <b>500 reviews per country and sort order</b>, each of about 175 storefronts is a separate feed, and running it again gives you the same reviews again.</p>

<h2>The API way: many apps, every country, only new reviews</h2>
{steps([
    f"Open the {a('app-store-reviews-scraper', S, 'App Store Reviews Scraper on Apify')}.",
    "Paste App Store links, app IDs, bundle IDs or app names, and pick countries (or all of them).",
    "Filter by stars (e.g. 1 to 2 for complaints), date and keywords before you pay for anything.",
    "Turn on <b>onlyNewReviews</b> and schedule it weekly: later runs return only reviews written since the last run.",
])}
{curl("app-store-reviews-scraper", {"apps": ["https://apps.apple.com/us/app/duolingo-language-lessons/id570060128"], "countries": ["us", "gb", "ca", "au"], "maxReviewsPerApp": 1000, "minRating": 1, "maxRating": 2})}
{python("app-store-reviews-scraper", {"apps": ["notion", "evernote"], "countries": ["us"], "maxReviewsPerApp": 500, "includeSummary": True}, '    if item.get("type") == "review":\n        print(item["rating"], item["date"], item["title"])')}
<p>Each run also writes a <b>free insights summary</b> per app: rating by version and country, top complaint and praise phrases, and the worst recent reviews. Reviewer names are not stored.</p>

<p class="example">Full working example on GitHub: <a href="https://github.com/rabroubx-coder/pandapi-examples/tree/main/app-reviews-export">export App Store and Google Play reviews to CSV</a> (MIT licence, copy and adapt).</p>
<h2>What it costs</h2>
{table(["Job", "Rows", "Price"], [
    ["One app, 1,000 US reviews", "1,000 reviews", "$0.15"],
    ["5 competitors × 4 countries × 500", "10,000 reviews", "$1.50"],
    ["Weekly monitoring of 10 apps", "only new reviews", "a few cents a week"],
    ["App details row", "1 per app", "$0.001"],
])}
<p>Apify's free $5 monthly credit covers over 30,000 reviews. Need Google Play too? See <a href="../export-google-play-reviews/">export Google Play reviews</a>.</p>
""",
    faq=[
        ("Can I export App Store reviews for free?", "Yes. Apple's public RSS feed gives the latest 500 reviews per country and sort order for any app, and App Store Connect's API covers your own apps. For more countries, filters and monitoring, the API costs $0.15 per 1,000 reviews and Apify's free credit covers over 30,000 a month."),
        ("Why can't I get more than 500 reviews?", "Apple's feed caps each country and sort order at 500. The scraper combines most-recent and most-helpful orders (up to about 1,000 unique per country) and lets you add every storefront."),
        ("Can I get competitor reviews?", "Yes. Reviews are public, so any app on the App Store works: paste its link, ID or name."),
        ("Does it include reviewer names?", "No. We leave reviewer names out on purpose. You get the rating, title, text, date, app version and country."),
    ],
    related=["export-google-play-reviews", "appfollow-alternative", "shopify-app-reviews-export"],
    free_tools=["json-to-excel", "csv-to-json"],
)

# 5. Google Play reviews ---------------------------------------------------------------------------------
S = "export-google-play-reviews"
page(
    slug=S, tool="google-play-reviews-scraper",
    title="Export Google Play Reviews to CSV (developer replies included)",
    h1="Export Google Play reviews to CSV, with developer replies",
    description="Export Google Play Store reviews for any Android app: Play Console's CSV for your own app, the free google-play-scraper library, and an API with many apps and languages, filters, monitoring and a free summary. $0.10 per 1,000 reviews.",
    lede="Play Console exports your own reviews as monthly CSV files. For competitor apps, or several languages at once, you need something else. Here's the free route, where it breaks, and the no-code route.",
    body=f"""
<h2>Free way 1: Play Console (your own app)</h2>
<p>Play Console › Ratings and reviews › Reviews has a download, and monthly review reports land in your Cloud Storage bucket. One CSV per app per month, your apps only.</p>

<h2>Free way 2: the google-play-scraper library</h2>
{code('''pip install google-play-scraper

from google_play_scraper import Sort, reviews
result, _ = reviews("com.duolingo", lang="en", country="us", sort=Sort.NEWEST, count=2000)''', 'python')}
<p>Works for any public app. Where it breaks: one language per call (German reviews need a second pass), no memory between runs, and when Google changes its page format the library breaks until someone patches it. You also keep it running yourself.</p>

<h2>The API way</h2>
{steps([
    f"Open the {a('google-play-reviews-scraper', S, 'Google Play Reviews Scraper on Apify')}.",
    "Paste Play Store links, package IDs or app names. Add several languages and countries: results are merged without duplicates.",
    "Filter by stars, date, keywords or app version, so you only pay for the reviews you need.",
    "Turn on <b>onlyNewReviews</b> and schedule it: each run returns only reviews written since the last one.",
])}
{curl("google-play-reviews-scraper", {"apps": ["https://play.google.com/store/apps/details?id=com.duolingo"], "languages": ["en", "de", "fr"], "countries": ["us"], "maxReviewsPerApp": 2000, "minRating": 1, "maxRating": 3})}
{python("google-play-reviews-scraper", {"apps": ["com.spotify.music"], "maxReviewsPerApp": 1000, "keywords": ["crash", "battery"]}, '    if item.get("type") == "review":\n        print(item["rating"], item["text"][:80], item.get("developerReply"))')}

<p class="example">Full working example on GitHub: <a href="https://github.com/rabroubx-coder/pandapi-examples/tree/main/app-reviews-export">export App Store and Google Play reviews to CSV</a> (MIT licence, copy and adapt).</p>
<h2>What you get</h2>
<p>Rating, text, date, app version, thumbs-up count, the developer's reply and its date, language and country. Optional app details (installs, rating histogram, Data safety, similar apps), search and top charts. A free per-app summary shows rating by version and language, developer reply rate and median reply time, and top complaint phrases. Reviewer names are not stored.</p>

<h2>What it costs</h2>
<p>$0.10 per 1,000 reviews, no start fee. 10,000 reviews cost $1. Apify's free credit covers about 50,000 reviews a month.</p>
""",
    faq=[
        ("How do I export Google Play reviews?", "For your own app, use Play Console's review download or monthly reports. For any app, use the google-play-scraper library or the Pandapi API, which handles several apps and languages in one run for $0.10 per 1,000 reviews."),
        ("Can I get reviews in all languages?", "Yes. Google Play splits reviews by language; list the languages you need and the API merges them without duplicates."),
        ("Do I get developer replies?", "Yes, with the reply text and date, and the free summary reports reply rate and median reply time."),
        ("How do I monitor new reviews?", "Turn on onlyNewReviews and schedule the run on Apify. Later runs return only reviews written since the previous run, so you pay only for new ones."),
    ],
    related=["export-app-store-reviews", "google-play-scraper-alternative", "appfollow-alternative"],
    free_tools=["json-to-excel", "csv-to-json"],
)

# 6. Shopify app reviews -------------------------------------------------------------------------------------
S = "shopify-app-reviews-export"
page(
    slug=S, tool="shopify-app-store-reviews",
    title="Shopify App Store Reviews Scraper + Fake-Review Signals",
    h1="Export Shopify App Store reviews, and spot suspicious ones",
    description="Export reviews of any Shopify app with developer replies, merchant country and time using the app, plus app details and pricing plans. Star, date and keyword filters, monitoring and a free fake-review signal score. $0.10 per 1,000 reviews.",
    lede="Shopify app developers and agencies read competitor reviews to find feature gaps, and many suspect review bursts on rival apps. Shopify has no export button. Here's how to get the reviews into a spreadsheet and check them.",
    body=f"""
<h2>The free way</h2>
<p>Every app's reviews are public at <code>apps.shopify.com/&lt;app&gt;/reviews</code>, 10 per page, with a newest-first sort and a star filter. For a few pages, copying them by hand works. For hundreds of pages it doesn't, and Shopify's Partner Dashboard shows only your own apps' reviews.</p>

<h2>The API way</h2>
{steps([
    f"Open the {a('shopify-app-store-reviews', S, 'Shopify App Store Reviews Scraper on Apify')}.",
    "Paste app links or handles (e.g. <code>judgeme</code>). Several apps per run are fine.",
    "Pick a star range (sent to Shopify, so 1-2 star runs are fast), a since-date and keywords.",
    "Turn on monitoring to get only reviews written since the last run, and schedule it weekly.",
])}
{curl("shopify-app-store-reviews", {"apps": ["https://apps.shopify.com/judgeme", "klaviyo-email-marketing"], "maxReviewsPerApp": 500, "minRating": 1, "maxRating": 2, "includeSummary": True})}

<h2>Fake-review signals, explained</h2>
<p>The free summary row for each app adds a 0-100 suspicion score with plain reasons: <b>review bursts</b> (days with far more reviews than the app's normal rate, and how many of them are 5 stars), <b>5-star reviews after less than a day of use</b>, <b>repeated wording</b> across reviews, and <b>very short 5-star reviews</b>. A high score is a reason to look closer, not proof. Shopify developers have asked for exactly this in a long community thread about fake reviews.</p>

<h2>What you get</h2>
<p>Stars, date, text, merchant country, "N months using the app", the developer reply and its date. App details: rating, review count, full star histogram, pricing plans, developer, launch date, categories and the Built for Shopify badge. Merchant store names are left out unless you switch them on.</p>

<h2>What it costs</h2>
<p>$0.10 per 1,000 reviews and $0.002 per app details row; the summary is free. 5,000 reviews of 3 apps cost about $0.51.</p>
""",
    faq=[
        ("Can I export reviews of a Shopify app I don't own?", "Yes. Shopify App Store reviews are public, so the API can read any listed app."),
        ("How are fake reviews detected?", "We don't claim to detect them for sure. The summary flags patterns that often come with paid or incentivised reviews: bursts, 5 stars after under a day of use, repeated wording and very short 5-star texts, with a score and reasons."),
        ("Does it include store names?", "Off by default for privacy. Switch includeStoreNames on if you need them."),
        ("Can I monitor a competitor's new reviews?", "Yes. Turn on onlyNewReviews and schedule the run; each run returns only reviews written since the last one."),
    ],
    related=["export-app-store-reviews", "export-google-play-reviews", "appfollow-alternative"],
    free_tools=["json-to-excel", "csv-to-json"],
)

# 7. Contact finder -------------------------------------------------------------------------------------------
S = "find-emails-from-websites"
page(
    slug=S, tool="website-contact-finder",
    title="Find Contact Emails from a List of Websites (CRM-ready)",
    h1="Find business emails, phones and socials from a list of websites",
    description="Paste company websites and get one CRM-ready row per site: business emails, phone numbers, LinkedIn, Facebook, Instagram, X and address. Contact pages read first. $5 per 1,000 sites with contacts; sites with nothing found are free.",
    lede="You have a list of company websites and need their public contact details in your CRM. Checking each Contact page by hand takes about two minutes a site. Here's the free way for a few, and how to do 1,000 in one run.",
    body=f"""
<h2>The free way</h2>
<p>Open the site, look at the footer, the Contact and About pages, and copy the email and phone. Browser extensions that pull emails from the open page help a little. Our free <a href="../link-extractor/">link extractor</a> lists every <code>mailto:</code> and <code>tel:</code> link on a page you paste, which is quick for a handful of sites.</p>

<h2>The API way: one row per website</h2>
{steps([
    f"Open the {a('website-contact-finder', S, 'Website Contact Finder on Apify')}.",
    "Paste your list of websites (or upload a CSV in the console).",
    "Keep <b>genericEmailsOnly</b> on to return role addresses like info@ and sales@ rather than people's personal addresses.",
    "Run it and export to CSV, Excel, Google Sheets, HubSpot (via Make or n8n) or JSON.",
])}
{curl("website-contact-finder", {"startUrls": [{"url": "https://apify.com"}, {"url": "https://crawlee.dev"}], "maxPagesPerSite": 8, "genericEmailsOnly": True})}
<p>The crawler reads the home page first, then the pages most likely to hold contacts (contact, about, imprint, team, support), up to <b>maxPagesPerSite</b>. You get one row per site: emails, phones, LinkedIn, Facebook, Instagram, X, YouTube, TikTok and the postal address when the site shows it, with the page each item came from.</p>

<h2>What it costs</h2>
<p>$5 per 1,000 websites where contacts were found. Sites with nothing found, or that block the crawler, are free. A list of 400 sites where 300 have contacts costs $1.50.</p>

<h2>Use it responsibly</h2>
<ul>
<li>It reads only public pages and respects robots.txt by default.</li>
<li>It's built for enriching companies you already work with or research, not for bulk cold email. Follow anti-spam and data protection law (GDPR, CAN-SPAM, CASL) where you use the data.</li>
<li>It doesn't guess or verify personal addresses; for that kind of tool see <a href="../hunter-io-alternative/">Hunter.io alternatives</a>.</li>
</ul>
""",
    faq=[
        ("How do I find the email address of a website?", "Check the footer, Contact, About and Imprint pages. To do it for many sites, the Website Contact Finder reads those pages for you and returns one row per site."),
        ("Do I pay for sites with no email?", "No. You pay $5 per 1,000 websites where contacts were found; sites with nothing found or that block the crawler are free."),
        ("Does it find personal emails?", "By default it returns role and business addresses (info@, sales@, support@) published on the site. It doesn't guess or pattern-match personal addresses."),
        ("Can I export to my CRM?", "Yes. Download CSV or Excel, or send rows to HubSpot, Pipedrive or Google Sheets with Apify, Make or n8n integrations."),
    ],
    related=["hunter-io-alternative", "website-screenshots-in-bulk", "company-jobs-api"],
    free_tools=["link-extractor", "json-to-excel"],
)

# 8. Screenshots ------------------------------------------------------------------------------------------------
S = "website-screenshots-in-bulk"
page(
    slug=S, tool="website-screenshot",
    title="Screenshot Multiple URLs at Once: Full Page, Desktop + Mobile",
    h1="Screenshot a list of URLs: full page, desktop and mobile, in one run",
    description="Take full-page screenshots of many websites at once, desktop and mobile in one run, as PNG, JPEG or PDF. Cookie banners hidden, pages left to settle. $4 per 1,000 screenshots, failed ones free.",
    lede="For one page, your browser can take a full-page screenshot. For 200 client sites, a landing-page audit or weekly visual records, you want a list in and a folder of images out.",
    body=f"""
<h2>The free way: one page</h2>
<p>In Chrome, open DevTools (F12), press Ctrl+Shift+P (Cmd+Shift+P on Mac), type <b>screenshot</b> and choose <b>Capture full size screenshot</b>. Firefox has <b>Take Screenshot › Save full page</b> in the right-click menu. For mobile, switch DevTools to device mode first. Great for one page, slow for fifty.</p>
<p>With code, Playwright does it in a few lines (<code>page.screenshot(full_page=True)</code>), and you handle the browser, cookie pop-ups, lazy images and failures yourself.</p>

<h2>The API way: a list in, images out</h2>
{steps([
    f"Open the {a('website-screenshot', S, 'Website Screenshot API on Apify')}.",
    "Paste your URLs. Choose devices (desktop, mobile, tablet), full page or viewport, and PNG, JPEG or PDF.",
    "Leave <b>hideCookieBanners</b> on. Add a delay or a selector to wait for if a page animates in.",
    "Run it. Each row has a <code>screenshotUrl</code> link that opens the image, plus the page title and HTTP status.",
])}
{curl("website-screenshot", {"urls": [{"url": "https://apify.com"}, {"url": "https://en.wikipedia.org/wiki/Web_scraping"}], "devices": ["desktop", "mobile"], "fullPage": True, "format": "png"})}
{python("website-screenshot", {"urls": [{"url": "https://example.com"}], "devices": ["desktop"], "format": "jpeg"}, '    print(item["url"], item["status"], item.get("screenshotUrl"))')}

<h2>What it costs</h2>
<p>$4 per 1,000 screenshots; failed pages are free and pages that answer 4xx/5xx are reported as failures, not charged. 250 sites on desktop and mobile (500 shots) cost $2. Apify's free credit covers about 1,250 shots a month. Comparing with subscription screenshot APIs? See <a href="../screenshotone-alternative/">ScreenshotOne alternatives</a>.</p>

<h2>Limits</h2>
<ul><li>No logins: pages behind a sign-in come out as the sign-in page.</li><li>Very long pages are cut at <code>maxHeightPx</code> (15,000 px by default) to keep images usable.</li></ul>
""",
    faq=[
        ("How do I screenshot multiple URLs at once?", "Paste the list into the Website Screenshot API, pick devices and format, and run it. You get one image link per URL and device."),
        ("Can it take full-page screenshots?", "Yes, fullPage is on by default, with lazy images loaded and cookie banners hidden."),
        ("Can I get a PDF instead of an image?", "Yes, set format to pdf. For proper printable documents with page sizes and headers, use the HTML to PDF API."),
        ("Do failed screenshots cost money?", "No. You pay only for screenshots that succeed."),
    ],
    related=["screenshotone-alternative", "html-to-pdf-api", "broken-link-checker-api"],
    free_tools=["markdown-to-pdf", "link-extractor"],
)

# 9. Broken links ---------------------------------------------------------------------------------------------------
S = "broken-link-checker-api"
page(
    slug=S, tool="broken-link-checker",
    title="Find Broken Links on Your Website (free check + bulk API)",
    h1="Find broken links on any website, and the page each one is on",
    description="Crawl a website and check every link for 404s, dead external links, server errors and redirects. See the page each broken link is on and its anchor text. Free ways compared, plus an API at $0.80 per 1,000 links.",
    lede="Broken links lose visitors and waste crawl budget. The hard part isn't finding a 404, it's knowing which page links to it so you can fix it. Here's how to do it free, and how to run it on a schedule.",
    body=f"""
<h2>Free ways</h2>
<ul>
<li><b>Google Search Console</b> › Pages › Not found (404): shows 404 URLs Google found, with some referring pages. Free and slow to update.</li>
<li><b>Screaming Frog SEO Spider</b> (desktop): the free version crawls up to 500 URLs per crawl. See <a href="../screaming-frog-alternative/">Screaming Frog alternatives</a> for bigger sites.</li>
<li><b>Our free <a href="../link-extractor/">link extractor</a></b>: paste a page's HTML or a sitemap to list every link, then spot-check them.</li>
</ul>

<h2>The API way: crawl, check, report</h2>
{steps([
    f"Open the {a('broken-link-checker', S, 'Broken Link Checker on Apify')}.",
    "Enter your start URL, how many pages to crawl and whether to check external links and images.",
    "Turn on <b>onlyBroken</b> to get just the problems.",
    "Schedule it weekly and send results to Slack or email, so new 404s show up before your visitors find them.",
])}
{curl("broken-link-checker", {"startUrls": [{"url": "https://example.com/"}], "maxPagesToCrawl": 200, "checkExternalLinks": True, "onlyBroken": True})}
<p>Each row: the link, its HTTP status, a category (<code>broken</code>, <code>blocked</code>, <code>error</code>, <code>ok</code>), whether it redirects and where, internal or external, the page it was found on, its anchor text, and how many pages link to it.</p>

<h2>What it costs</h2>
<p>$0.80 per 1,000 links checked. A site with 3,000 links costs $2.40; Apify's free credit covers about 6,000 links a month. It doesn't use a browser, so it's fast, and it respects robots.txt.</p>

<h2>Limits</h2>
<ul><li>Some sites (LinkedIn, some shops) block automated checks; those links are reported as <code>blocked</code>, not broken.</li><li>Links added by JavaScript after load are not seen.</li></ul>
""",
    faq=[
        ("How do I find broken links on my website for free?", "Use Google Search Console's Not found report, Screaming Frog's free version (500 URLs per crawl), or the Broken Link Checker with Apify's free $5 monthly credit, which covers about 6,000 links."),
        ("Does it show where the broken link is?", "Yes. Every broken link comes with the page it's on, its anchor text and how many pages link to it."),
        ("Does it check external links?", "Yes, checkExternalLinks is on by default. Sites that block bots are marked blocked so they don't flood your report."),
        ("Can I check images too?", "Yes, turn on checkImages to test image URLs as well."),
    ],
    related=["screaming-frog-alternative", "website-screenshots-in-bulk", "website-to-markdown-api"],
    free_tools=["link-extractor"],
)

# 10. Hacker News --------------------------------------------------------------------------------------------------------
S = "hacker-news-api-export"
page(
    slug=S, tool="hacker-news-scraper",
    title="Export Hacker News Stories and Comments to CSV",
    h1="Export Hacker News stories, comments and jobs to CSV",
    description="Search Hacker News stories, comments, Ask HN, Show HN and job posts by keyword, date, points or author, and export them to CSV or JSON. The free Algolia API explained, plus a no-code scraper at $0.20 per 1,000 items.",
    lede="Founders track mentions of their product, recruiters read Who is Hiring threads and researchers study what developers talk about. Hacker News has two free official APIs. Here's how to use them, and when a hosted scraper saves you time.",
    body=f"""
<h2>The free way: HN's official APIs</h2>
<ul>
<li><b>Algolia HN Search API</b> (<code>hn.algolia.com/api/v1/search</code>): full-text search with filters on tags, points and dates. Free, no key.</li>
<li><b>Firebase API</b> (<code>hacker-news.firebaseio.com/v0</code>): one item at a time by ID, plus top, new, best, ask, show and job lists.</li>
</ul>
{code('curl "https://hn.algolia.com/api/v1/search_by_date?query=postgres&tags=story&numericFilters=points>50"', 'bash')}
<p>The catch: a search returns at most 1,000 hits (50 pages), so big exports have to be split by date range, and you write the pagination and CSV code yourself. More in <a href="../hacker-news-api-vs-scraper/">HN API vs a scraper</a>.</p>

<h2>The no-code way</h2>
{steps([
    f"Open the {a('hacker-news-scraper', S, 'Hacker News Scraper on Apify')}.",
    "Enter a query, content type (story, comment, Ask HN, Show HN, job, poll or front page), a date range, an author, and minimum points or comments.",
    "Run and download CSV, Excel or JSON. Paging past the API's 1,000-result cap is handled for you.",
    "Schedule it daily to watch new mentions of your product or competitors.",
])}
{curl("hacker-news-scraper", {"searchQuery": "AI agents", "contentType": "story", "sortBy": "date", "minPoints": 20, "maxItems": 500})}

<h2>What it costs</h2>
<p>$0.20 per 1,000 items. 5,000 stories and comments cost $1, and Apify's free credit covers about 25,000 items a month.</p>
""",
    faq=[
        ("Is the Hacker News API free?", "Yes. Both the Algolia search API and the Firebase API are free and need no key. The scraper adds date splitting past the 1,000-result cap, filters and CSV export for $0.20 per 1,000 items."),
        ("How do I export Who is Hiring posts?", "Set contentType to job for HN job posts, or comment with a query such as \"remote python\" and a date range to search the hiring threads' comments. Export to CSV and filter in Excel."),
        ("Can I track mentions of my product?", "Yes. Schedule a daily run with your product name as the query, sorted by date, and send new rows to Slack or email."),
    ],
    related=["hacker-news-api-vs-scraper", "company-jobs-api"],
    free_tools=["json-to-excel", "link-extractor"],
)

# 11. HTML to PDF ------------------------------------------------------------------------------------------------------------
S = "html-to-pdf-api"
page(
    slug=S, tool="html-to-pdf",
    title="HTML to PDF API: URLs, HTML and Invoice Templates in Bulk",
    h1="HTML to PDF API: web pages, HTML and invoice templates in bulk",
    description="Turn web pages, HTML or an HTML template plus JSON rows (invoices, certificates, reports) into PDFs. Page size, margins, headers, footers and page numbers. $3 per 1,000 PDFs whatever the page count; failures free.",
    lede="Generating PDFs is easy until you need hundreds: invoices from order data, certificates for every attendee, reports for every client. Here are the free options, and an API that fills a template with your rows and returns one PDF per row.",
    body=f"""
<h2>Free options</h2>
<ul>
<li><b>Your browser</b>: Print › Save as PDF. Fine for one page.</li>
<li><b>Our free <a href="../markdown-to-pdf/">Markdown to PDF</a></b> tool: real text, page numbers and a table of contents, in your browser.</li>
<li><b>Code</b>: headless Chrome (Puppeteer, Playwright <code>page.pdf()</code>) or WeasyPrint. wkhtmltopdf is archived and uses an old WebKit, so modern CSS breaks. See <a href="../pdfshift-alternative/">PDFShift and wkhtmltopdf alternatives</a>.</li>
</ul>

<h2>The API way: a template plus your data</h2>
{steps([
    f"Open the {a('html-to-pdf', S, 'HTML to PDF API on Apify')}.",
    "Either list URLs, paste HTML, or paste a <b>Handlebars template</b> and a <b>data</b> array (one object per document).",
    "Set page size, margins, landscape, header and footer templates and page numbers. <b>fileNameTemplate</b> names each file, e.g. <code>invoice-{{{{number}}}}</code>.",
    "Run it. Each row links to its PDF in your Apify storage.",
])}
{curl("html-to-pdf", {"template": "<h1>Invoice {{number}}</h1><p>{{customer}}</p><p>Total: {{formatNumber total 2}} EUR</p>", "data": [{"number": "2026-001", "customer": "Acme GmbH", "total": 1200}, {"number": "2026-002", "customer": "Globex", "total": 349.5}], "fileNameTemplate": "invoice-{{number}}", "pageFormat": "A4", "pageNumbers": True})}
<p>Template helpers include <code>multiply</code>, <code>sumProduct</code> and <code>formatNumber</code> for invoice lines and totals.</p>

<h2>What it costs</h2>
<p>$3 per 1,000 PDFs, any page count, no start fee. 500 invoices cost $1.50. Failed documents are free. Apify's free credit covers about 1,600 PDFs a month.</p>
""",
    faq=[
        ("How do I generate PDFs from an HTML template?", "Paste a Handlebars template and an array of JSON rows into the HTML to PDF API. It renders one PDF per row with headless Chrome and names each file from your template."),
        ("Can I convert a URL to PDF?", "Yes. List the URLs; cookie banners are hidden and lazy images loaded before printing."),
        ("Does a 30-page PDF cost more?", "No. The price is $3 per 1,000 PDFs whatever the page count."),
        ("Can I add page numbers and headers?", "Yes. Turn on pageNumbers or write your own headerTemplate and footerTemplate."),
    ],
    related=["pdfshift-alternative", "website-screenshots-in-bulk"],
    free_tools=["markdown-to-pdf", "csv-to-json"],
)

# 12. Company jobs ------------------------------------------------------------------------------------------------------------
S = "company-jobs-api"
page(
    slug=S, tool="company-jobs-tracker",
    title="Greenhouse, Lever & Ashby Jobs API: Track Company Hiring",
    h1="Get every open job from the companies you name (Greenhouse, Lever, Ashby and 8 more)",
    description="Pull every open job from named companies straight from their career sites: Greenhouse, Lever, Ashby, SmartRecruiters, Workable and 6 more. Tracks new and closed jobs between runs, salary, remote, plus a free hiring summary. $1 per 1,000 jobs.",
    lede="Sales teams use hiring as a buying signal, recruiters watch competitors, investors watch headcount. The data is public on each company's career site. Here's how to read it free from the ATS APIs, and how to track a whole watchlist with new and closed jobs.",
    body=f"""
<h2>The free way: the ATS job-board APIs</h2>
<p>Most career sites run on an applicant tracking system with a public JSON feed:</p>
{code('''https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true
https://api.lever.co/v0/postings/palantir?mode=json
https://api.ashbyhq.com/posting-api/job-board/notion''', 'text')}
<p>Free and official. The work: finding which ATS each company uses and its board name, mapping 11 different formats, and remembering last week's jobs so you can see which ones are new or closed.</p>

<h2>The API way: a watchlist</h2>
{steps([
    f"Open the {a('company-jobs-tracker', S, 'Company Jobs Tracker on Apify')}.",
    "List companies by name, website, careers page or board link. The ATS is detected for you.",
    "Filter by keywords, locations, remote/hybrid, department, seniority or salary.",
    "Turn on <b>trackChanges</b> with a watchlist name and schedule it weekly: you get new jobs (paid) and closed jobs with days open (free).",
])}
{curl("company-jobs-tracker", {"companies": ["Airbnb", "stripe.com", "https://jobs.lever.co/palantir", "https://jobs.ashbyhq.com/notion"], "keywords": ["engineer", "data"], "locations": ["US", "Canada", "remote"], "trackChanges": True, "watchlistName": "eng-north-america"})}

<h2>What you get</h2>
<p>Title, department, location, remote/hybrid/onsite, employment type, seniority, salary normalized to min/max/currency/period (from the ATS or parsed from the text), posted date, apply link and description. A free summary row per company counts open roles by department and location, remote share, and new and closed jobs this run.</p>

<h2>What it costs</h2>
<p>$1 per 1,000 jobs; summaries and closed-job rows are free. A 40-company watchlist with 2,000 open jobs costs $2 the first time, and weekly runs after that charge only new jobs.</p>

<h2>Limits</h2>
<ul><li>Workday career sites are not supported yet (they block cloud servers).</li><li>LinkedIn and Indeed are not covered: this reads companies' own career sites only.</li></ul>
<p>Comparing job data providers? See <a href="../theirstack-alternative/">TheirStack alternatives</a>.</p>
""",
    faq=[
        ("Is there a free Greenhouse jobs API?", "Yes. Greenhouse's job board API (boards-api.greenhouse.io) is public and free, as are Lever's and Ashby's. The Jobs Tracker reads 11 such systems and adds change tracking for $1 per 1,000 jobs."),
        ("How do I track when a company closes a job?", "Turn on trackChanges with a watchlist name. Each run compares with the last one and returns closed jobs with their first-seen date, closed date and days open, free of charge."),
        ("Which ATS are supported?", "Greenhouse, Lever (US and EU), Ashby, SmartRecruiters, Workable, Recruitee, Personio, BambooHR, Rippling, Teamtailor and Breezy."),
        ("Do I need to know the company's ATS?", "No. Give a name, website or careers page and the ATS and board name are detected."),
    ],
    related=["theirstack-alternative", "government-tenders-api", "find-emails-from-websites"],
    free_tools=["json-to-excel", "csv-to-json"],
)

# 13. Profanity -----------------------------------------------------------------------------------------------------------------
S = "profanity-filter-api"
page(
    slug=S, tool="profanity-filter",
    title="Profanity Filter API: 26 Languages, Leetspeak, No Scunthorpe",
    h1="Profanity filter API that catches sh1t and f u c k, not Scunthorpe",
    description="Find and mask bad words in comments, reviews and chat in 26 languages. Catches leetspeak, spaced, stretched and self-censored spellings without flagging Password or Scunthorpe. Bulk or real-time, PurgoMalum compatible. $0.20 per 1,000 texts.",
    lede="A word list catches the easy cases and fails on the rest: users type sh1t, f.u.c.k and fuuuck, and naive filters block Scunthorpe, Password and class. Here's what free options do well, where they fail, and how to filter comments in 26 languages.",
    body=f"""
<h2>Free options</h2>
<ul>
<li><b>npm <code>bad-words</code> / Python <code>better-profanity</code></b>: simple English lists, fine for a hobby project.</li>
<li><b>PurgoMalum</b>: a free web service, English-focused, no SLA. See <a href="../purgomalum-alternative/">PurgoMalum alternatives</a>.</li>
<li><b>LDNOOBW lists</b> on GitHub: word lists in many languages, which you match yourself.</li>
</ul>
<p>The hard parts are the same for all of them: obfuscated spellings, words that are innocent in English but rude elsewhere (and the reverse), and substrings inside ordinary words.</p>

<h2>The API way</h2>
{steps([
    f"Open the {a('profanity-filter', S, 'Profanity Filter API on Apify')}.",
    "Send texts, or point it at another dataset (for example reviews from our scrapers) and the field to check.",
    "Pick languages or <code>auto</code>, a mode (<code>mask</code>, <code>replace</code>, <code>remove</code> or <code>flag</code>), and standard or strict.",
    "Add your own <b>blockWords</b> and <b>allowWords</b>. For real-time checks, use the instant API endpoint, which also accepts PurgoMalum-style calls.",
])}
{curl("profanity-filter", {"texts": ["What a great product, thanks!", "This is sh1t and the support is f u c k i n g useless"], "languages": ["auto"], "mode": "mask"})}
<p>Each row returns the cleaned text, whether it was flagged, the matched words with their language and position, and the original text.</p>

<h2>What it costs</h2>
<p>$0.20 per 1,000 texts; empty texts are free. 50,000 comments cost $10.</p>

<h2>Limits</h2>
<p>It matches words, not tone: it won't catch an insult made of polite words. Non-English lists come from LDNOOBW, and Chinese, Japanese and Korean are matched as substrings.</p>
""",
    faq=[
        ("What is the Scunthorpe problem?", "Filters that match bad words inside other words block innocent text like Scunthorpe, Password or class. This API matches whole words and was tested on 370,105 English words to remove false hits."),
        ("Does it catch leetspeak?", "Yes: sh1t, f u c k, fuuuck, f*ck and Cyrillic or Greek look-alike letters."),
        ("Which languages are supported?", "26, including English, Spanish, French, German, Portuguese, Italian, Dutch, Russian, Arabic, Hindi, Japanese and Chinese, with auto-detection by script."),
        ("Can I switch from PurgoMalum?", "Yes. The instant API has PurgoMalum-compatible endpoints, so moving is a base-URL change."),
    ],
    related=["purgomalum-alternative", "export-app-store-reviews"],
    free_tools=["csv-to-json", "json-to-excel"],
)

# 14. Postal codes --------------------------------------------------------------------------------------------------------------
S = "zip-code-api"
page(
    slug=S, tool="postal-code-lookup",
    title="ZIP & Postal Code API: Distance, Radius, 120+ Countries",
    h1="ZIP and postal code API: lookup, distance and radius in 124 countries",
    description="Look up ZIP and postal codes in 124 countries: city, state, county and coordinates. Distance between two codes, all codes within a radius, codes for a city and the nearest code to a point. $0.30 per 1,000 results, not-found free.",
    lede="Store locators, delivery zones and sales territories all need the same few things: what's at this ZIP code, how far apart are two codes, and which codes are within 25 km. Here are the free options and their limits, and a bulk API for all of it.",
    body=f"""
<h2>Free options</h2>
<ul>
<li><b>Zippopotam.us</b>: free lookup of a code to its place in about 60 countries. Lookup only: no distance or radius.</li>
<li><b>ZipCodeAPI.com</b>: US and Canada distance and radius; its free tier allows 10 requests per hour.</li>
<li><b>GeoNames</b> postal code files: free downloads (CC BY 4.0) you load and query yourself.</li>
</ul>
<p>More in <a href="../zipcodeapi-alternative/">ZipCodeAPI and Zippopotam alternatives</a>.</p>

<h2>The API way</h2>
{steps([
    f"Open the {a('postal-code-lookup', S, 'ZIP & Postal Code API on Apify')}.",
    "Add codes to look up (<code>US 90210</code>, <code>DE 10115</code>), pairs to measure, centres for a radius search, place names or coordinates. Mix them in one run.",
    "Run it in bulk, or call the instant API endpoint for one lookup at a time.",
])}
{curl("postal-code-lookup", {"postalCodes": ["US 90210", "GB SW1A 1AA", "DE 10115"], "distancePairs": ["US 10001; US 94105"], "radiusCenters": ["US 60601"], "radius": 10, "radiusUnit": "km"})}

<h2>What it costs</h2>
<p>$0.30 per 1,000 results found; codes that aren't found are free. 10,000 lookups cost $3.</p>

<h2>Limits, honestly</h2>
<p>Data comes from GeoNames. For the UK, Canada, Ireland, the Netherlands and Malta only the first part of the code is published openly (e.g. <code>SW1A</code>, <code>M5V</code>), so full codes are matched on that part and the row says so. Coordinates are area centres, good for distance and radius, not for delivery routing.</p>
""",
    faq=[
        ("Is there a free ZIP code API?", "Zippopotam.us is free for lookups in about 60 countries, and ZipCodeAPI.com has a free tier of 10 requests per hour for the US and Canada. The Pandapi API covers 124 countries with distance and radius for $0.30 per 1,000 results."),
        ("How do I find all ZIP codes within a radius?", "Add the centre code to radiusCenters, set radius and unit (km or miles), and run. You get every code in range with its distance."),
        ("Does it support UK postcodes?", "Yes, matched on the outward code (e.g. SW1A), which is what open data publishes. Full address-level UK data needs Royal Mail's paid PAF."),
    ],
    related=["zipcodeapi-alternative", "company-jobs-api"],
    free_tools=["csv-to-json", "json-to-excel"],
)

# 15. MCP server --------------------------------------------------------------------------------------------------------------------
S = "mcp-server-for-web-and-pdf"
page(
    slug=S, tool="pandapi-mcp-server",
    title="MCP Server for Web Pages, PDFs, Reviews and Tenders (Claude, Cursor)",
    h1="One MCP server for web pages, PDFs, screenshots, reviews and tenders",
    description="Give Claude, Cursor or any MCP client 14 data tools: web pages and PDFs to Markdown, screenshots, broken links, contacts, tenders, app reviews, postal codes, HTML to PDF and Hacker News. Results in one call, spend cap per call.",
    lede="Your AI agent needs to read a docs page, a PDF or a competitor's reviews. Most MCP servers do one thing, or load dozens of generic tools that eat your context window. This one gives an agent 14 focused tools with small definitions and answers in one call.",
    body=f"""
<h2>How to connect</h2>
<p>In Claude (web or desktop), Cursor, VS Code or any client that supports remote MCP servers, add this URL and sign in with your Apify account:</p>
{code('https://mcp.apify.com/?tools=blueberry_rainstorm/pandapi-mcp-server', 'text')}
<p>Or use the server's own URL with your Apify token as a bearer header:</p>
{code('''URL:     https://blueberry-rainstorm--pandapi-mcp-server.apify.actor/mcp
Header:  Authorization: Bearer <your Apify token>''', 'text')}
<p>Add <code>?tools=markdown,pdf</code> to the server URL to load only the tools you need. Details on the {a('pandapi-mcp-server', S, 'Pandapi MCP Server page')}.</p>

<h2>The tools</h2>
{table(["Tool", "What the agent can do", "Price per result"], [
    ["web_to_markdown", "Read web pages, sitemaps or whole docs sites as Markdown", "$0.001 per page"],
    ["pdf_extract", "Read PDFs as Markdown, text and tables", "$0.003 per PDF"],
    ["screenshot_website", "See a page on desktop or mobile", "$0.004 per shot"],
    ["check_broken_links", "Check a site for 404s", "$0.0008 per link"],
    ["find_website_contacts", "Find a company's public contact details", "$0.005 per site with contacts"],
    ["search_public_tenders", "Search government tenders", "$0.002 per notice"],
    ["app_store_reviews, google_play_reviews, shopify_app_reviews", "Read app reviews", "$0.0001 to $0.00015 per review"],
    ["company_jobs", "List a company's open jobs", "$0.001 per job"],
    ["postal_code_lookup", "Look up codes, distance, radius", "$0.0003 per result"],
    ["html_to_pdf", "Make a PDF", "$0.003 per PDF"],
    ["search_hacker_news", "Search Hacker News", "$0.0002 per item"],
    ["profanity_filter", "Clean or flag text", "$0.0002 per text"],
])}

<h2>Why it is different</h2>
<ul>
<li><b>Small</b>: when we measured it, 13 tool definitions took 26,927 characters; the same actors loaded through Apify\'s generic MCP connection took 155,221. Less context spent before your first question.</li>
<li><b>Results in one call</b>: the server waits for the run and returns rows, with no second "fetch dataset" step. Long jobs return a run ID to collect later.</li>
<li><b>Spend cap on every call</b> (<code>maxCostUsd</code>, default $1) and small default sizes.</li>
</ul>
<p>The server itself is free; each call costs that tool's own price on your Apify account, and Apify's free plan includes $5 a month.</p>
""",
    faq=[
        ("How do I add the Pandapi MCP server to Claude?", "Add a custom connector with the URL https://mcp.apify.com/?tools=blueberry_rainstorm/pandapi-mcp-server and sign in with Apify. It works in Claude, Cursor, VS Code and other remote MCP clients."),
        ("Is it free?", "The server is free. Each tool call is billed at that API's per-result price on your Apify account, with a spend cap per call. Apify's free plan gives $5 of credit a month."),
        ("Can it read PDFs and websites for my agent?", "Yes. The markdown tool reads pages, sitemaps and docs sites; the pdf tool reads PDFs including tables and scans."),
        ("How is it different from Firecrawl MCP?", "Firecrawl MCP focuses on web scraping and search with a credit plan. This server adds PDFs, screenshots, reviews, tenders, jobs and postal codes, priced per result with no subscription."),
    ],
    related=["website-to-markdown-api", "firecrawl-alternative", "extract-tables-from-pdf-to-excel"],
    free_tools=["html-to-markdown", "pdf-to-markdown"],
)
