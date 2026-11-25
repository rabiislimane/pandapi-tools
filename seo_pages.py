"""SEO guide pages for the Pandapi Tools site (rendered by build.py).

Two kinds of pages, one folder each at the site root (so they share the tool pages' "../" depth):
  kind "api"     one page per paid Pandapi API: the buyer's job, a real how-to, price maths, FAQ
  kind "compare" "X alternative" / "X vs Y" pages against the top competitors, honest both ways

Add a page: append a dict to PAGES in seo_content_tools.py or seo_content_compare.py
(see SEO-PAGES.md for the fields and rules), then run `SITE_URL=... python3 build.py`.
Every link to a paid API goes through api_url(), which adds the utm tags the marketing
thread reads: utm_source=pandapi-tools, utm_medium=seo, utm_campaign=<actor>, utm_content=<page>.
"""
import html
import json

E = html.escape
APIFY = "https://apify.com/blueberry_rainstorm/"
UPDATED = "2026-11-21"
UPDATED_TEXT = "21 November 2026"

# The paid APIs (Apify actors). price = what a buyer pays; example = the price maths line.
API = {
    "web-page-to-markdown": dict(name="Website to Markdown API", price="$1 per 1,000 pages", unit="page",
        example="a 500-page docs site costs $0.50", free="about 5,000 pages a month"),
    "pdf-to-text-markdown": dict(name="PDF to Excel, Markdown & Text API", price="$3 per 1,000 PDFs (OCR pages $5 per 1,000)", unit="PDF",
        example="300 bank statements cost $0.90", free="about 1,600 PDFs a month"),
    "public-tenders-feed": dict(name="Government Tenders API", price="$2 per 1,000 notices", unit="notice",
        example="a daily alert with 40 new notices costs $0.08 a day", free="about 2,500 notices a month"),
    "app-store-reviews-scraper": dict(name="App Store Reviews Scraper", price="$0.15 per 1,000 reviews", unit="review",
        example="10,000 reviews cost $1.50", free="over 30,000 reviews a month"),
    "google-play-reviews-scraper": dict(name="Google Play Reviews Scraper", price="$0.10 per 1,000 reviews", unit="review",
        example="10,000 reviews cost $1.00", free="about 50,000 reviews a month"),
    "shopify-app-store-reviews": dict(name="Shopify App Store Reviews Scraper", price="$0.10 per 1,000 reviews + $0.002 per app", unit="review",
        example="5,000 reviews of 3 apps cost about $0.51", free="tens of thousands of reviews a month"),
    "website-contact-finder": dict(name="Website Contact Finder", price="$5 per 1,000 websites with contacts (no contacts = free)", unit="website",
        example="a list of 400 company sites where 300 have contacts costs $1.50", free="about 1,000 websites a month"),
    "website-screenshot": dict(name="Website Screenshot API", price="$4 per 1,000 screenshots", unit="screenshot",
        example="250 sites on desktop and mobile (500 shots) cost $2", free="about 1,250 screenshots a month"),
    "broken-link-checker": dict(name="Broken Link Checker", price="$0.80 per 1,000 links checked", unit="link",
        example="a site with 3,000 links costs $2.40", free="about 6,000 links a month"),
    "hacker-news-scraper": dict(name="Hacker News Scraper", price="$0.20 per 1,000 items", unit="item",
        example="5,000 stories and comments cost $1", free="about 25,000 items a month"),
    "html-to-pdf": dict(name="HTML to PDF API", price="$3 per 1,000 PDFs (any page count)", unit="PDF",
        example="500 invoices cost $1.50", free="about 1,600 PDFs a month"),
    "company-jobs-tracker": dict(name="Company Jobs Tracker", price="$1 per 1,000 jobs (summaries and closed jobs free)", unit="job",
        example="a 40-company watchlist with 2,000 open jobs costs $2, and later runs charge only new jobs", free="about 5,000 jobs a month"),
    "profanity-filter": dict(name="Profanity Filter API", price="$0.20 per 1,000 texts", unit="text",
        example="50,000 comments cost $10", free="about 25,000 texts a month"),
    "postal-code-lookup": dict(name="ZIP & Postal Code API", price="$0.30 per 1,000 results (not found = free)", unit="result",
        example="10,000 ZIP lookups cost $3", free="about 16,000 results a month"),
    "shopify-products-price-monitor": dict(name="Competitor Price Monitor", price="$0.50 per 1,000 products on the first run, then $1 per 1,000 changes (unchanged products free)", unit="product",
        example="3 competitor stores of 100 products checked daily cost about $0.30 a month", free="several competitor stores checked every day",
        cta_line="<b>Competitor Price Monitor</b>: watching 3 competitor stores of 100 products every day costs about $0.30 a month. Unchanged products are free, and Apify's free plan gives you $5 of credit every month."),
    "pandapi-mcp-server": dict(name="Pandapi MCP Server", price="free server; each tool call costs that API's own price", unit="call",
        example="converting 20 pages to Markdown from Claude costs $0.02", free="the same $5 of monthly credit"),
}


def api_url(actor, page, path=""):
    return f"{APIFY}{actor}{path}?utm_source=pandapi-tools&amp;utm_medium=seo&amp;utm_campaign={actor}&amp;utm_content={page}"


def a(actor, page, label, path=""):
    return f'<a href="{api_url(actor, page, path)}">{label}</a>'


def code(text, lang=""):
    cls = f' class="language-{lang}"' if lang else ""
    return f'<pre><code{cls}>{E(text.strip(chr(10)))}</code></pre>'


def curl(actor, run_input):
    body = json.dumps(run_input, indent=2, ensure_ascii=False)
    return code(f"""curl -X POST "https://api.apify.com/v2/acts/blueberry_rainstorm~{actor}/run-sync-get-dataset-items?token=$APIFY_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{body}'""", "bash")


def python(actor, run_input, loop):
    body = json.dumps(run_input, indent=4, ensure_ascii=False).replace("true", "True").replace("false", "False").replace("null", "None")
    return code(f"""# pip install apify-client
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("blueberry_rainstorm/{actor}").call(run_input={body})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
{loop}""", "python")


def table(headers, rows, cls="cmp"):
    head = "".join(f"<th scope=\"col\">{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join((f"<th scope=\"row\">{c}</th>" if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def steps(items):
    return "<ol class=\"steps\">" + "".join(f"<li>{s}</li>" for s in items) + "</ol>"


def cta(actor, page, line=None, button=None):
    t = API[actor]
    line = line or t.get("cta_line") or f"<b>{t['name']}</b>: {t['price']}. Apify's free plan gives you $5 of credit every month, which covers {t['free']}. No start fee; failed items are free."
    button = button or f"Try {t['name']}"
    return (f'<div class="card cta"><img src="../assets/icons/api/{actor}.png" alt="" width="56" height="56" loading="lazy">'
            f'<p>{line}</p><a class="btn" href="{api_url(actor, page)}">{E(button)}</a></div>')


def page_html(p, head, foot, free_tools, all_pages, site_url):
    slug = p["slug"]
    path = slug + "/"
    actor = p["tool"]
    crumb_kind = "API guides" if p["kind"] == "api" else "Comparisons"
    url = f"{site_url}/{path}" if site_url else ""
    ld = [
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": p["h1"], "description": p["description"],
         "datePublished": p.get("published", UPDATED), "dateModified": max(p.get("published", UPDATED), UPDATED),
         "author": {"@type": "Organization", "name": "Pandapi"}, "publisher": {"@type": "Organization", "name": "Pandapi"},
         **({"mainEntityOfPage": url, "image": f"{site_url}/assets/icons/api/{actor}.png"} if site_url else {})},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(ans)}} for q, ans in p["faq"]]},
    ]
    if site_url:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Pandapi Tools", "item": f"{site_url}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{site_url}/guides/"},
            {"@type": "ListItem", "position": 3, "name": p["h1"], "item": url}]})
    extra = '<link rel="stylesheet" href="../assets/guides.css">\n' + "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    by_slug = {q["slug"]: q for q in all_pages}
    related = [by_slug[s] for s in p.get("related", []) if s in by_slug]
    tools = [free_tools[s] for s in p.get("free_tools", []) if s in free_tools]
    from seo_meta import META
    out = [head(p["title"], META.get(slug, p["description"]), path, f"api/{actor}.png", extra)]
    out.append(f"""<main><div class="wrap article">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../">Pandapi Tools</a> › <a href="../guides/">Guides</a> › <span>{crumb_kind}</span></nav>
<div class="hero"><img src="../assets/icons/api/{actor}.png" alt="" width="64" height="64"><h1>{E(p['h1'])}</h1></div>
<p class="lede">{p['lede']}</p>
<p class="byline">Updated {p.get('updated_text', UPDATED_TEXT)} · by the Pandapi team{' · We make one of the tools compared here, so we list where the others are better too.' if p['kind'] == 'compare' else ''}</p>
{cta(actor, slug)}
<section class="content prose">
{p['body']}
<h2>Questions</h2>
{''.join(f'<details><summary>{E(q)}</summary><p>{ans}</p></details>' for q, ans in p['faq'])}
</section>
{cta(actor, slug, p.get('cta_line'), p.get('cta_button'))}
""")
    if related:
        out.append('<section class="content"><h2>Related guides</h2><div class="grid">'
                   + "".join(guide_tile(r) for r in related) + "</div></section>")
    if tools:
        out.append('<section class="content"><h2>Free tools for the same job</h2><div class="grid">'
                   + "".join(tool_tile(t) for t in tools) + "</div></section>")
    out.append("</div></main>\n")
    out.append(foot("../"))
    return "".join(out)


def guide_tile(p, depth="../"):
    return (f'<a class="card tile" href="{depth}{p["slug"]}/"><img src="{depth}assets/icons/api/{p["tool"]}.png" alt="" width="56" height="56" loading="lazy">'
            f'<div><h3>{E(p["h1"])}</h3><p>{E(_short(p))}</p></div></a>')


def _short(p):
    from seo_meta import META
    text = META.get(p["slug"]) or p["description"]
    first = text.split(". ")[0].rstrip(".")
    return first + "."



def tool_tile(t, depth="../"):
    return (f'<a class="card tile" href="{depth}{t["slug"]}/"><img src="{depth}assets/icons/{t["icon"]}" alt="" width="56" height="56" loading="lazy">'
            f'<div><h3>{E(t["name"])} (free)</h3><p>{E(t["description"].split(". ")[0])}.</p></div></a>')


def hub_html(head, foot, all_pages, site_url, outcomes=None):
    desc = "Guides to Pandapi's data APIs: how to export app reviews, extract PDF tables to Excel, turn websites into Markdown for RAG, track government tenders and more, plus honest comparisons with Firecrawl, Hunter, ScreenshotOne and others."
    extra = '<link rel="stylesheet" href="../assets/guides.css">'
    apis = [p for p in all_pages if p["kind"] == "api"]
    cmps = [p for p in all_pages if p["kind"] == "compare"]
    return (head("Data API guides and comparisons · Pandapi", desc, "guides/", "api/web-page-to-markdown.png", extra)
            + f"""<main><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../">Pandapi Tools</a> › <span>Guides</span></nav>
<h1>Guides: get the data you need, then automate it</h1>
<p class="lede">Each guide starts with the free way to do the job, then shows how to do it in bulk or on a schedule with a Pandapi API. You pay per result, failed items are free, and Apify's free plan gives you $5 of credit every month to try them.</p>
{('<h2 id="alerts">Alerts you can set up in 3 minutes, no code</h2><div class="grid">' + ''.join(outcomes.tile(p) for p in outcomes.PAGES) + '</div>') if outcomes else ''}
<h2>How to do the job</h2>
<div class="grid">{''.join(guide_tile(p) for p in apis)}</div>
<h2>Comparisons and alternatives</h2>
<div class="grid">{''.join(guide_tile(p) for p in cmps)}</div>
</div></main>
""" + foot("../"))


def strip_tags(s):
    import re
    return html.unescape(re.sub(r"<[^>]+>", "", s))
