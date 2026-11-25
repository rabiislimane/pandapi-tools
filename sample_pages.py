"""Free sample reports (proof pages) for the two hero monitors, 2026-11-25 (thread "Win first paying customers").

Each page shows REAL rows from one small Apify run on public data (run id and dataset id printed on the
page, compact copy in samples_data/<key>.json made from the run's dataset; never invented). Price pages
watch 3 public Shopify stores in one niche with monitoring on, so the Black Friday / Cyber Monday re-runs
(same monitorKey sample-<key>-bf2026) can add the real changes as an update section.

Rendered by build.py: samples/index.html (hub) and samples/<slug>/index.html, listed in sitemap.xml and
linked from the matching outcome page (outcome_pages.page_html calls links_for()).
Add a report: run the actor, save the compact JSON in samples_data/, append to REPORTS.
"""
import html
import json
import os

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
APIFY = "https://apify.com/blueberry_rainstorm/"
UPDATED = "2026-11-25"
EXAMPLES_REPO = "https://github.com/rabroubx-coder/pandapi-examples"
X_PROFILE = "https://x.com/PandapiDev"

REPORTS = [
    dict(key="coffee", slug="coffee-roasters-black-friday-prices", outcome="competitor-price-monitoring",
         actor="shopify-products-price-monitor", niche="specialty coffee roasters",
         h1="Black Friday 2026 price watch: 3 specialty coffee roasters",
         meta="Real snapshot of Death Wish Coffee, Onyx Coffee Lab and Stumptown before Black Friday 2026: prices, discounts, stock and new products, from their public Shopify stores."),
    dict(key="apparel", slug="sustainable-shoes-apparel-black-friday-prices", outcome="competitor-price-monitoring",
         actor="shopify-products-price-monitor", niche="sustainable shoe and apparel brands",
         h1="Black Friday 2026 price watch: Allbirds, Rothy's and Tentree",
         meta="Real snapshot of Allbirds, Rothy's and Tentree before Black Friday 2026: how much of each catalog is on sale, the deepest discounts and new products."),
    dict(key="beauty", slug="beauty-fashion-black-friday-prices", outcome="competitor-price-monitoring",
         actor="shopify-products-price-monitor", niche="beauty and fashion brands",
         h1="Black Friday 2026 price watch: Kylie Cosmetics, ColourPop and SKIMS",
         meta="Real snapshot of Kylie Cosmetics, ColourPop and SKIMS before Black Friday 2026: share on sale, average discount, out-of-stock share and new products."),
    dict(key="cleaning", slug="janitorial-cleaning-government-tenders", outcome="government-tender-alerts",
         actor="public-tenders-feed", niche="janitorial and cleaning contractors",
         h1="Janitorial and cleaning government tenders open this week",
         meta="43 real janitorial, custodial and cleaning tenders published in one week on SAM.gov, UK Find a Tender, TED and CanadaBuys, with deadlines and values."),
    dict(key="cyber", slug="cybersecurity-government-tenders", outcome="government-tender-alerts",
         actor="public-tenders-feed", niche="cybersecurity firms",
         h1="Cybersecurity government tenders published this week",
         meta="Real cybersecurity and penetration testing tenders published in one week across SAM.gov, TED, CanadaBuys and the UK, with deadlines and estimated values."),
]
BY_SLUG = {r["slug"]: r for r in REPORTS}


def data(r):
    with open(os.path.join(HERE, "samples_data", r["key"] + ".json")) as f:
        return json.load(f)


def money(v):
    if v is None:
        return "not published"
    if v >= 1_000_000:
        return f"about ${v / 1_000_000:.1f}M"
    if v >= 1000:
        return f"about ${v / 1000:,.0f}k"
    return f"${v:,.2f}".replace(".00", "")


def pct(v):
    return "0%" if not v else f"{round(v * 100)}%"


def table(headers, rows):
    head = "".join(f'<th scope="col">{h}</th>' for h in headers)
    body = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="cmp"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def utm(url, r):
    sep = "&amp;" if "?" in url else "?"
    return f"{url}{sep}utm_source=pandapi-tools&amp;utm_medium=sample&amp;utm_campaign={r['actor']}&amp;utm_content={r['slug']}"


def offer(r):
    from urllib.parse import quote
    what = "up to 3 competitor store links" if r["key"] in ("coffee", "apparel", "beauty") else "your keywords and countries"
    title = quote("Free sample report: " + ("competitor prices" if what.startswith("up") else "government tenders"))
    body = quote(f"What should we check? ({what}):\n\n\nWhere should we send the report? (an email address or your X handle):\n")
    return what, f"{EXAMPLES_REPO}/issues/new?title={title}&amp;body={body}&amp;labels=sample-report"


def price_body(r, d):
    rows = []
    for s in d["stores"]:
        rows.append([f'<a href="https://{E(s["store"])}" rel="nofollow">{E(s["name"])}</a>',
                     f'{s["productsRead"]:,}' + ("" if s["complete"] else f' of {s["reported"]:,}'),
                     f'${s["priceMedian"]:g}', pct(s["onSale"]),
                     "none" if not s["avgDiscount"] else f'{s["avgDiscount"]:g}%', pct(s["outOfStock"])])
    out = ["<h2>Before Black Friday: the snapshot (25 November 2026)</h2>",
           table(["Store", "Products read", "Median price", "On sale", "Average discount", "Out of stock"], rows),
           '<p class="note">"Products read" is capped at 250 per store for this demo; a real watch reads the whole catalog. '
           "Shares count products; the average discount is across products on sale.</p>"]
    for s in d["stores"]:
        out.append(f'<h3>{E(s["name"])}</h3>')
        if s["discounts"]:
            out.append("<p><b>Deepest discounts right now:</b></p>" + table(["Product", "Price", "Was", "Off"], [
                [f'<a href="{E(x["url"])}" rel="nofollow">{E(x["title"])}</a>', f'${x["price"]:g}', f'${x["compareAt"]:g}', f'{x["pct"]:g}%'] for x in s["discounts"]]))
        else:
            out.append("<p>No product is marked down today. That makes this store the one to watch: the first markdown will show up as a change.</p>")
        if s["newest"]:
            out.append("<p><b>Newest products:</b> " + "; ".join(
                f'<a href="{E(n["url"])}" rel="nofollow">{E(n["title"])}</a> (${n["price"]:g}, {n["published"]})' for n in s["newest"]) + ".</p>")
    out.append("<h2>What happens next</h2><p>Monitoring is on for these 3 stores. We run the same watch again after the Black Friday deals go live "
               "(Friday 27 November) and after Cyber Monday (30 November), and add every real change here: price drops and increases with the old "
               "price, new price and % change, new products, removed products, and items that sold out. That's exactly the short list you'd get "
               "by email every morning for your own competitors.</p>")
    return "".join(out)


def tender_body(r, d):
    rows = [[f'<a href="{E(n["url"])}" rel="nofollow">{E(n["title"])}</a>', E(n["country"] or ""), E(n["buyer"] or ""),
             (f'{n["deadline"]} ({n["daysLeft"]} days left)' if n["deadline"] and n["daysLeft"] is not None else (n["deadline"] or "not published")),
             money(n["valueUsd"])] for n in d["notices"]]
    if r["key"] == "cyber":
        intro = (f'<p>Our run found {d["total"]} notices that mention these words anywhere in the notice. Below are the {len(rows)} that say it in the '
                 "<b>title</b>: the ones a cybersecurity firm would actually bid on. You can keep the broad match or switch to title-only.</p>")
    else:
        intro = f'<p>{len(rows)} notices published between 19 and 25 November 2026, soonest deadline first. Every link opens the official notice.</p>'
    return (f"<h2>The report: {E(d['headline'])}</h2>" + intro +
            table(["Tender", "Country", "Buyer", "Deadline", "Value"], rows) +
            "<h2>What a daily alert looks like</h2><p>Scheduled every morning with \"Only new notices\" on, you get only the tenders you haven't seen yet, "
            "one line each with the buyer, deadline, days left, value and link, soonest deadline first. Days with nothing new send nothing.</p>")


def page_html(r, head, foot, site_url):
    d = data(r)
    path = f"samples/{r['slug']}/"
    what, gh = offer(r)
    setup = f"../../{r['outcome']}/"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": r["h1"], "description": r["meta"], "datePublished": d["date"],
          "dateModified": UPDATED, "author": {"@type": "Organization", "name": "Pandapi"}}
    if site_url:
        ld["url"] = f"{site_url}/{path}"
    extra = '<link rel="stylesheet" href="../../assets/guides.css">\n' + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    body = price_body(r, d) if d["kind"] == "price" else tender_body(r, d)
    price = ("About $0.30 a month to watch 3 competitor stores every day, inside Apify's free $5 monthly credit." if d["kind"] == "price"
             else "About $0.30 a month for a daily alert on your keywords, inside Apify's free $5 monthly credit.")
    return "".join([head(r["h1"], r["meta"], path, f"api/{r['actor']}.png", extra), f"""<main><div class="wrap article outcome">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../../">Pandapi Tools</a> › <a href="../">Sample reports</a> › <span>{E(r['niche'].capitalize())}</span></nav>
<div class="hero"><img src="../../assets/icons/api/{r['actor']}.png" alt="" width="64" height="64"><h1>{E(r['h1'])}</h1></div>
<p class="lede">A real report for {E(r['niche'])}, made with the same tool you can schedule for yourself. Public data only, run on {d['date']}.</p>
<div class="card cta setup"><img src="../../assets/icons/api/{r['actor']}.png" alt="" width="56" height="56"><p><b>Want this for your own {'competitors' if d['kind'] == 'price' else 'keywords'}?</b> {price}</p>
<a class="btn" href="{setup}">Set it up in 5 minutes</a></div>
<section class="content prose">
{body}
<div class="card offer">
<h2>Get a free report like this for your business</h2>
<p>Send us {E(what)} and we'll run it once and send you the report, free. We do up to 5 free reports a week.</p>
<p><a class="btn" href="{gh}" rel="nofollow">Ask on GitHub</a> <a class="btn secondary" href="{X_PROFILE}" rel="nofollow">Message us on X</a></p>
</div>
<p class="note">Source: each store's or portal's public data, read by <a href="{utm(APIFY + r['actor'], r)}">{E(r['actor'].replace('-', ' ').title())}</a>, run {E(d['run'])} (dataset {E(d['dataset'])}) on {d['date']}. Pandapi is not affiliated with the stores or buyers named here.</p>
<p><a href="../">More sample reports</a> · <a href="{setup}">How the alert works and what it costs</a></p>
</section>
<p class="byline">Updated {UPDATED} · by the Pandapi team</p>
</div></main>
""", foot("../../")])


def hub_html(head, foot, site_url):
    cards = "".join(f'<a class="card tile" href="{r["slug"]}/"><img src="../assets/icons/api/{r["actor"]}.png" alt="" width="56" height="56" loading="lazy">'
                    f'<div><h3>{E(r["h1"])}</h3><p>{E(r["meta"].split(": ")[0])}.</p></div></a>' for r in REPORTS)
    meta = "Real sample reports from Pandapi's competitor price alerts and government tender alerts: Black Friday price watches and this week's tenders."
    return "".join([head("Free sample reports: competitor prices and government tenders", meta, "samples/", "api/shopify-products-price-monitor.png",
                         '<link rel="stylesheet" href="../assets/guides.css">'), f"""<main><div class="wrap article">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../">Pandapi Tools</a> › <span>Sample reports</span></nav>
<h1>Free sample reports</h1>
<p class="lede">Real reports made with our alerts on public data, so you can see exactly what you'd get before you set anything up.
Want one for your own competitors or keywords? <a href="{EXAMPLES_REPO}/issues/new?labels=sample-report&amp;title=Free%20sample%20report">Ask here</a>, it's free.</p>
<section class="content"><div class="grid">{cards}</div></section>
<p><a href="../competitor-price-monitoring/">Competitor price alerts</a> · <a href="../government-tender-alerts/">Government tender alerts</a></p>
</div></main>
""", foot("../")])


def links_for(outcome_slug, depth="../"):
    rs = [r for r in REPORTS if r["outcome"] == outcome_slug]
    if not rs:
        return ""
    return ("<p><b>More real reports:</b> " + " · ".join(f'<a href="{depth}samples/{r["slug"]}/">{E(r["h1"])}</a>' for r in rs) + "</p>")
