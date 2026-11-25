# SEO guide pages

Built 2026-11-21 by the thread "Build SEO pages that win users". 34 pages live at the site root, plus a hub at `/guides/`.

## Files
- `seo_pages.py`: renderer, the `API` table of the 15 paid tools (price lines), helpers (`a()`, `curl()`, `python()`, `table()`, `steps()`, `cta()`), the `/guides/` hub.
- `seo_content_tools.py`: one page per paid API (`kind: "api"`), 15 pages.
- `seo_content_compare.py`: comparison and "X alternative" pages (`kind: "compare"`), 19 pages.
- `seo_meta.py`: the short meta description (max 158 chars) per page slug. Required for every new page.
- `assets/guides.css`, `assets/icons/api/<actor>.png` (128 px copies of design/icons/png).
- `build.py` imports these, writes `<slug>/index.html` and `guides/index.html`, adds every page to `sitemap.xml` with `<lastmod>`, and shows `HOME_GUIDES` on the home page.

Build: `SITE_URL=https://rabiislimane.github.io/pandapi-tools python3 build.py`

## Add a page
1. Check the topic isn't already listed below (one page per search intent; no near-duplicates).
2. Append `page(slug=..., tool=<actor slug from API>, title=..., h1=..., description=..., lede=..., body=f"""...""", faq=[(q, a)], related=[guide slugs], free_tools=[tool slugs])` to the right content file.
3. Add the slug's meta description to `seo_meta.py`.
4. Build, then check: no broken relative links, JSON-LD parses, no horizontal scroll at 390 px, 0 console errors.

## Rules
- Keyword research from free sources only (Google autocomplete via suggestqueries.google.com, Apify Store API, People also ask).
- Each page: the free/DIY way first, then the API how-to with a real input that matches the actor's input schema, the price maths, honest limits, FAQ.
- Comparison pages: competitor facts only from their own pricing page/docs or the Apify Store API, with a "Sources, checked <date>" line, and a section on where the competitor is the better choice.
- Every link to a paid API goes through `a()` / `cta()`, which adds `utm_source=pandapi-tools&utm_medium=seo&utm_campaign=<actor>&utm_content=<page slug>`.
- Slugs must not clash with tool folders (build.py asserts it).

## Pages (slug: target query)
API pages: website-to-markdown-api (website to markdown api / for llm), extract-tables-from-pdf-to-excel (extract tables from pdf to excel), government-tenders-api (government tenders api), export-app-store-reviews (export app store reviews), export-google-play-reviews (export google play reviews), shopify-app-reviews-export (shopify app store reviews scraper), find-emails-from-websites (find email from website), website-screenshots-in-bulk (screenshot multiple urls), broken-link-checker-api (find broken links on website), hacker-news-api-export (hacker news scraper), html-to-pdf-api (html to pdf api), company-jobs-api (greenhouse jobs api), profanity-filter-api (profanity filter api), zip-code-api (zip code api radius), mcp-server-for-web-and-pdf (mcp server web scraping pdf).

Compare pages: firecrawl-alternative, jina-reader-alternative, camelot-vs-tabula, best-free-pdf-to-excel-converters, bank-statement-pdf-to-excel, convertio-alternative, tableconvert-alternative, hunter-io-alternative, screenshotone-alternative, screaming-frog-alternative, pdfshift-alternative, appfollow-alternative, google-play-scraper-alternative, sam-gov-api-alternative, theirstack-alternative, purgomalum-alternative, zipcodeapi-alternative, hacker-news-api-vs-scraper, firecrawl-mcp-alternative.

Next topics with demand (not built yet): "pdf to markdown api", "url to markdown python", "app store review sentiment analysis", "who is hiring hacker news", "zip codes within radius", "best mcp servers for claude", "lever jobs api", "ted tenders api", "contracts finder api", "html to pdf n8n".

## Outcome pages (2026-11-25, strategy v3)
`outcome_pages.py`: one page per outcome for non-technical buyers (competitor-price-monitoring, government-tender-alerts, see-competitors-google-ads). Each has a real sample report from a named run dataset, the monthly price, a "Set it up in 3 minutes" button to a published Apify example task (`console.apify.com/create-task-from-example/<task id>`), a 3-step no-code recipe, the free sample report offer, an honest SaaS comparison and a small developer box. Listed on the home page and at `/guides/#alerts`. Test: `node test/outcome-pages.js` (1280 and 390 px, console errors, links, JSON-LD). Studies: ops/competitors/outcome-*.md.
