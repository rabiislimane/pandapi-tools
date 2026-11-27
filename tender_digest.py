"""Free weekly public data digest: government IT tenders this week (strategy v3, unit D, 2026-11-27).

Data: digest/data/it-tenders.json, written by `node digest/fetch.mjs` (official open-data feeds: SAM.gov,
TED, Find a Tender, Contracts Finder, CanadaBuys, World Bank; no API keys, no Apify credit, no personal data).
A GitHub Actions workflow (.github/workflows/tender-digest.yml) runs both steps every Monday and commits
the result, so the page refreshes itself for $0.

Renders <SLUG>/index.html, <SLUG>/feed.xml (RSS) and <SLUG>/tenders.csv.
build.py calls render_all() so a full rebuild keeps the page; `python3 tender_digest.py` renders only
these files and updates the page's <lastmod> in sitemap.xml (what the weekly job runs).
"""
import csv
import html
import io
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from email.utils import format_datetime

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "digest", "data", "it-tenders.json")
SLUG = "government-it-tenders"
APIFY = "https://apify.com/blueberry_rainstorm/"
ALERT_PAGE = "../government-tender-alerts/"
SETUP = "https://console.apify.com/create-task-from-example/hdv8OVr0yH8q0Oqhg"
SRC_LINKS = {
    "sam": ("SAM.gov", "https://sam.gov/"),
    "ted": ("TED", "https://ted.europa.eu/"),
    "uk-fts": ("Find a Tender", "https://www.find-tender.service.gov.uk/"),
    "uk-cf": ("Contracts Finder", "https://www.contractsfinder.service.gov.uk/"),
    "canadabuys": ("CanadaBuys", "https://canadabuys.canada.ca/"),
    "worldbank": ("World Bank", "https://projects.worldbank.org/en/projects-operations/procurement"),
}
TITLE = "Government IT tenders this week: US, UK, EU and Canada (free list)"
H1 = "Government IT tenders this week: software, cloud and IT services from the US, UK, EU and Canada"


def load():
    if not os.path.exists(DATA):
        return None
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def _date(iso):
    if not iso:
        return None
    if "T" not in iso:
        iso += "T00:00:00Z"
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def nice(iso):
    d = _date(iso)
    return f"{d.day} {d.strftime('%b %Y')}" if d else ""


def money(n):
    if not n:
        return ""
    if n >= 1e6:
        return f"about ${n / 1e6:.1f}M".replace(".0M", "M")
    if n >= 1e3:
        return f"about ${round(n / 1e3):,}k"
    return f"about ${round(n):,}"


def meta_for(d):
    n = len(d["notices"])
    countries = len({r["country"] for r in d["notices"] if r["country"]})
    return (f"{n} open government IT tenders posted in the last 7 days: software, cloud, cybersecurity and IT services from "
            f"SAM.gov, TED, UK and Canada, {countries} countries, soonest deadline first. Free weekly list, RSS and CSV.")


def rows_html(d):
    out = []
    for r in d["notices"]:
        src = SRC_LINKS.get(r["source"], (r["sourceName"] or r["source"], None))[0]
        dl = nice(r["deadline"]) or "see notice"
        left = f'<br><span class="muted">{r["daysLeft"]} days left</span>' if r.get("daysLeft") is not None else ""
        out.append(
            f'<tr><th scope="row">{dl}{left}</th>'
            f'<td><a href="{E(r["url"] or "")}" rel="nofollow noopener">{E((r["title"] or "Untitled notice")[:160])}</a></td>'
            f'<td>{E((r["buyerName"] or "")[:80])}</td>'
            f'<td>{E(r["countryName"] or r["country"] or "")}</td>'
            f'<td>{money(r.get("valueUsd"))}</td>'
            f'<td>{E(src)}</td></tr>')
    return ('<div class="table-scroll"><table class="cmp"><thead><tr><th scope="col">Deadline</th><th scope="col">Tender</th>'
            '<th scope="col">Buyer</th><th scope="col">Country</th><th scope="col">Value (USD)</th><th scope="col">Source</th></tr></thead>'
            f'<tbody>{"".join(out)}</tbody></table></div>')


FAQ = [
    ("Where do these tenders come from?", "From the official open-data feeds of SAM.gov (US federal), TED (EU and EEA), Find a Tender and Contracts Finder (UK), CanadaBuys and World Bank procurement. Each title links to the official notice."),
    ("How often is the list updated?", "Every Monday morning (UTC). It lists open tenders first published in the 7 days before, soonest deadline first."),
    ("Which tenders count as IT?", "Notices whose text matches software, cloud, IT services, cybersecurity or data centre, and that also have the word in the title or an IT classification code (CPV 48, 72 or 302, IT NAICS or PSC codes, UNSPSC 43 or 81)."),
    ("Can I get tenders for my own keywords every day?", "Yes. The daily tender alert uses the same six sources with your own keywords, countries and minimum value, and sends only new notices by email or Slack. It costs about $0.30 a month for 5 new tenders a day."),
    ("Is this list complete?", "No. It shows up to 40 matches per source per week, from national and EU-level portals only. Many regional and state portals are not covered, and some portals publish values in local currency only."),
]


def page_html(d, head, foot, site_url):
    path = SLUG + "/"
    gen = _date(d["generatedAt"])
    n = len(d["notices"])
    by_country = Counter(r["countryName"] or r["country"] for r in d["notices"] if (r["countryName"] or r["country"]))
    top = ", ".join(f"{c} {k}" for c, k in by_country.most_common(6))
    ok = [s for s in d["sources"].values() if s.get("ok")]
    failed = [s["name"] for s in d["sources"].values() if not s.get("ok")]
    ld = [
        {"@context": "https://schema.org", "@type": "Dataset", "name": H1, "description": meta_for(d),
         "temporalCoverage": f"{d['postedSince']}/{gen.date().isoformat()}", "isAccessibleForFree": True,
         "creator": {"@type": "Organization", "name": "Pandapi"}, "license": "https://creativecommons.org/publicdomain/zero/1.0/",
         **({"url": f"{site_url}/{path}", "distribution": [
             {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f"{site_url}/{path}tenders.csv"},
             {"@type": "DataDownload", "encodingFormat": "application/rss+xml", "contentUrl": f"{site_url}/{path}feed.xml"}]} if site_url else {})},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ]
    extra = ('<link rel="stylesheet" href="../assets/guides.css">\n'
             f'<link rel="alternate" type="application/rss+xml" title="Government IT tenders this week" href="{(site_url + "/" + path) if site_url else ""}feed.xml">\n'
             + "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld))
    utm = "utm_source=pandapi-tools&amp;utm_medium=digest&amp;utm_campaign=public-tenders-feed&amp;utm_content=" + SLUG
    sources_line = " · ".join(
        f'<a href="{SRC_LINKS[k][1]}" rel="noopener">{SRC_LINKS[k][0]}</a> {v["kept"]}' for k, v in d["sources"].items() if v.get("ok") and k in SRC_LINKS)
    return (head(TITLE, meta_for(d), path, "api/public-tenders-feed.png", extra) + f"""<main><div class="wrap article outcome">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../">Pandapi Tools</a> › <a href="../guides/#alerts">Alerts</a> › <span>IT tenders this week</span></nav>
<div class="hero"><img src="../assets/icons/api/public-tenders-feed.png" alt="" width="64" height="64"><h1>{E(H1)}</h1></div>
<p class="lede"><b>{n} open IT tenders</b> first published between {nice(d['postedSince'])} and {nice(d['generatedAt'])}: software, cloud, cybersecurity and IT services, from six official portals in one list, <b>soonest deadline first</b>. Free, updated every Monday. Most notices: {E(top)}.</p>
<div class="card cta setup"><img src="../assets/icons/api/public-tenders-feed.png" alt="" width="56" height="56">
<p><b>Want only the tenders that fit your company, every morning?</b> The daily alert watches the same portals for your own keywords and countries and emails you only new notices. About $0.30 a month.</p>
<a class="btn" href="{SETUP}" rel="nofollow">Set it up in 3 minutes</a>
<span class="setup-note"><a href="{ALERT_PAGE}">How the daily tender alert works</a> · <a href="feed.xml">RSS feed</a> · <a href="tenders.csv">Download CSV</a></span></div>
<section class="content prose">
<h2>This week's list</h2>
<p class="sources">Updated {nice(d['generatedAt'])}. Notices per source: {sources_line}.{(' Not reachable this week: ' + E(', '.join(failed)) + '.') if failed else ''} Values are converted to US dollars at the European Central Bank rate of {E(d.get('currencyRatesDate') or '')}; blank means the notice gives no value.</p>
{rows_html(d)}
<h2>How this list is made</h2>
<ul>
<li>Every Monday a free scheduled job reads the official open-data feeds of {', '.join(v[0] for v in SRC_LINKS.values())}. No login, no API key.</li>
<li>It keeps <b>open tenders</b> (not awards) first published in the last 7 days whose text matches <b>{E(', '.join(d['keywords']))}</b>, and that have the word in the title or an IT classification code.</li>
<li>No personal data: contact names, emails and phone numbers in the notices are left out. Open each notice for the buyer's contact details.</li>
<li>The same code runs the <a href="{APIFY}public-tenders-feed?{utm}">Government Tenders API</a> on Apify, where you choose your own keywords, countries, codes and minimum value.</li>
</ul>
<h2>Get your own tender alert</h2>
<ol class="steps">
<li><b>Open the ready-made task</b> with <b>Set it up in 3 minutes</b> and create a free Apify account (no card).</li>
<li><b>Type your keywords</b> (for example "cybersecurity", "ERP", "managed services") and the email address you signed up with in <b>Email me the report at</b>, then click <b>Save &amp; Start</b>.</li>
<li><b>Schedule it daily</b> in Apify's <b>Schedules</b> page. Each morning you get only tenders you haven't seen.</li>
</ol>
<p><a class="btn" href="{SETUP}" rel="nofollow">Set it up in 3 minutes</a></p>
<h2>Questions</h2>
{''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in FAQ)}
<h2>Learn more</h2>
<ul>
<li><a href="{ALERT_PAGE}">Government tender alerts on your keywords</a></li>
<li><a href="../samples/cybersecurity-government-tenders/">Sample report: cybersecurity tenders</a></li>
<li><a href="../govwin-alternative/">GovWin alternatives for small bid teams</a></li>
<li><a href="../sam-gov-api-alternative/">SAM.gov alternatives compared</a></li>
</ul>
</section>
<aside class="card devbox" aria-label="For developers">
<h2>For developers</h2>
<p>Use the <a href="feed.xml">RSS feed</a> or <a href="tenders.csv">CSV</a> as they are, or call the <a href="{APIFY}public-tenders-feed/api?{utm}">Government Tenders API</a> (HTTP API, webhooks, Python and JavaScript clients). It's also in the <a href="{APIFY}pandapi-mcp-server?{utm}">Pandapi MCP server</a> and the <a href="https://www.npmjs.com/package/n8n-nodes-pandapi">n8n node</a>.</p>
</aside>
<p class="byline">Updated {nice(d['generatedAt'])} · by the Pandapi team</p>
</div></main>
""" + foot("../"))


def feed_xml(d, site_url):
    base = f"{site_url}/{SLUG}/" if site_url else f"{SLUG}/"
    gen = _date(d["generatedAt"])
    items = []
    for r in d["notices"]:
        pub = _date(r["publishedAt"]) or gen
        desc = " · ".join(x for x in [r["buyerName"], r["countryName"], f"deadline {nice(r['deadline'])}" if r["deadline"] else None,
                                       money(r.get("valueUsd")), SRC_LINKS.get(r["source"], (r["sourceName"],))[0]] if x)
        items.append(f"<item><title>{E(r['title'] or 'Untitled notice')}</title><link>{E(r['url'] or base)}</link>"
                     f"<guid isPermaLink=\"false\">{E(r['id'])}</guid><pubDate>{format_datetime(pub.astimezone(timezone.utc), usegmt=True)}</pubDate>"
                     f"<description>{E(desc)}</description></item>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>Government IT tenders this week (Pandapi)</title><link>{E(base)}</link>"
            f"<description>{E(meta_for(d))}</description><language>en</language>"
            f"<lastBuildDate>{format_datetime(gen.astimezone(timezone.utc), usegmt=True)}</lastBuildDate><ttl>1440</ttl>"
            + "".join(items) + "</channel></rss>\n")


def tenders_csv(d):
    cols = ["deadline", "daysLeft", "title", "buyerName", "country", "countryName", "valueAmount", "valueCurrency", "valueUsd", "publishedAt", "sourceName", "url", "id"]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for r in d["notices"]:
        w.writerow(["" if r.get(c) is None else (round(r[c]) if c == "valueUsd" else r[c]) for c in cols])
    return buf.getvalue()


def render_all(head, foot, site_url, write):
    """Write the page, RSS and CSV if the data file exists. Returns (path, lastmod) for the sitemap, or None."""
    d = load()
    if not d:
        return None
    write(f"{SLUG}/index.html", page_html(d, head, foot, site_url))
    write(f"{SLUG}/feed.xml", feed_xml(d, site_url))
    write(f"{SLUG}/tenders.csv", tenders_csv(d))
    return SLUG + "/", d["generatedAt"][:10]


if __name__ == "__main__":
    import build  # head/foot/SITE_URL; build.py only writes files under its __main__ guard

    res = render_all(build.head, build.foot, build.SITE_URL, build.write)
    if res and build.SITE_URL:
        sm = os.path.join(HERE, "sitemap.xml")
        with open(sm, encoding="utf-8") as f:
            s = f.read()
        loc = f"<loc>{build.SITE_URL}/{res[0]}</loc>"
        if loc in s:
            s = re.sub(re.escape(loc) + r"<lastmod>[0-9-]+</lastmod>", loc + f"<lastmod>{res[1]}</lastmod>", s)
            with open(sm, "w", encoding="utf-8") as f:
                f.write(s)
    print("tender digest:", res)
