"""Outcome pages for the Pandapi Tools site (strategy v3, 2026-11-25).

One page per outcome a non-technical buyer pays for ("get an alert when a competitor changes prices"),
not per API. Each page has: an H1 in the buyer's search words, a REAL sample report copied from an
existing run dataset (dataset id noted next to it, never invented), the monthly price in plain money,
a "Set it up in 3 minutes" button that opens a published Apify example task (prefilled input), a
step-by-step no-code setup (account, inputs + email, start, schedule, Slack), the free custom sample report offer, an
honest comparison with the SaaS buyers would otherwise pay for, links to the tutorial/alternative
pages, and a small "for developers" box at the bottom.

Rendered by build.py: `<slug>/index.html`, listed on the home page, the /guides/ hub and sitemap.xml.
Add a page: append to PAGES, add its meta line to META, and publish its Apify task first
(ops/competitors/outcome-*.md has the study for each page).
"""
import html
import json
from urllib.parse import quote

E = html.escape
APIFY = "https://apify.com/blueberry_rainstorm/"
UPDATED = "2026-11-25"
UPDATED_TEXT = "25 November 2026"
EXAMPLES_REPO = "https://github.com/rabroubx-coder/pandapi-examples"
X_PROFILE = "https://x.com/PandapiDev"


def utm(url, actor, slug):
    sep = "&amp;" if "?" in url else "?"
    return f"{url}{sep}utm_source=pandapi-tools&amp;utm_medium=outcome&amp;utm_campaign={actor}&amp;utm_content={slug}"


def table(headers, rows, cls="cmp"):
    head = "".join(f'<th scope="col">{h}</th>' for h in headers)
    body = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def link(url, label):
    return f'<a href="{url}">{label}</a>'


# ---------------------------------------------------------------- pages

PAGES = [
    dict(
        slug="competitor-price-monitoring",
        actor="shopify-products-price-monitor",
        task_id="Zhd4WMwiEeWgKkVXT",
        task_name="competitor-price-alerts",
        short="Competitor price alerts",
        title="Competitor price monitoring for Shopify stores: daily alerts",
        meta="Get an alert when a competitor store changes a price, adds a product or runs out of stock. Shopify and WooCommerce, no code, about $0.30 a month.",
        h1="Competitor price monitoring: get an alert when a competitor changes prices",
        lede="Paste a competitor's Shopify or WooCommerce store. Every morning you get a short list of what changed: <b>price drops and increases</b> (old price, new price, % change), <b>new products</b>, <b>removed products</b> and <b>out of stock or back in stock</b>. Unchanged products cost nothing.",
        price_line="<b>About $0.30 a month</b> to watch 3 competitor stores of 100 products every day. Apify's free plan gives you $5 of credit every month, so this runs free.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real rows from our run on 24 November 2026 on <b>Death Wish Coffee</b> (deathwishcoffee.com), a Shopify store, limited to its 3 newest products for the demo. The first run saves this baseline; you'd normally watch the whole catalog.</p>"
            + table(["Product", "Price", "On sale", "In stock", "Published"], [
                ['<a href="https://www.deathwishcoffee.com/products/triple-threat-chocolate-bark-bundle">Triple Threat Chocolate Bark Bundle</a>', "$45.00", "No", "Yes", "18 Nov 2026"],
                ['<a href="https://www.deathwishcoffee.com/products/brewed-for-battle-klean-kanteen-bundle">Valhalla Java Brewed for Battle Klean Kanteen Bundle</a>', "$50.99", "No", "Yes", "17 Nov 2026"],
                ['<a href="https://www.deathwishcoffee.com/products/valhalla-java-dark-chocolate-bark">Valhalla Java Dark Chocolate Bark</a>', "$15.00", "No", "Yes", "11 Nov 2026"],
            ])
            + "<p><b>Store summary from the same run (free):</b> the store reports 155 products; prices in this sample run from $15 to $50.99 (median $45); 0% on sale; 0% out of stock; top product types Chocolate (2) and Bundle (1).</p>"
            + '<p class="sources">Source: Apify run YnwsOzPcmLKFfdzez, dataset IdTUVVed9yyaFq6in, 24 Nov 2026. Nothing on this page is made up.</p>'
        ),
        alert_title="What the daily alert tells you",
        alert=[
            "<b>Price drop</b> or <b>price increase</b>: product, variant, old price, new price and the % change.",
            "<b>New product</b>: the full product row (title, price, stock, link, image), the day it appears.",
            "<b>Removed product</b>: a product that's no longer in the store.",
            "<b>Out of stock</b> and <b>back in stock</b>, per variant (size, colour).",
            "<b>New variant</b>: a new size or colour on an existing product.",
            "A free <b>summary</b> per store: number of each change and the biggest price drops, so the email reads like \"3 prices dropped, 1 product out of stock\".",
        ],
        steps=[
            "<b>Create a free Apify account (1 minute).</b> Click <b>Set it up in 3 minutes</b>. Apify opens with our ready-made task already attached. Click <b>Continue with Google</b> (or type your email). It's free: $5 of credit every month, no card.<br><img class=\"shot\" src=\"../assets/setup/signup-price-alerts.webp\" alt=\"Apify sign-up screen showing: Start with Get alerts when a competitor changes prices\" width=\"560\" height=\"620\" loading=\"lazy\">",
            "<b>Fill in two things.</b> The task opens with an example filled in. Replace the example store with your competitors' store links, one per line (up to 10). Then type the email address you signed up with in <b>Email me the report at</b> (Apify only sends to your own account's address).",
            "<b>Click Save &amp; Start.</b> About a minute later the first report is in your inbox. It lists the products it saved as the starting point; from then on you only hear about changes: price drops, price increases, out of stock, back in stock, new and removed products.",
            "<b>Make it run every morning.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Daily</b> and a time, click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b> (new schedules start switched off). Apify's guide with pictures: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>.",
            "<b>Optional: Slack.</b> On your task's <b>Integrations</b> tab add <b>Slack</b> and use this message: <code>{{resource.statusMessage}}</code>. It posts the report's first line (\"Allbirds: 3 prices dropped, 1 item out of stock\"). Apify's guide: <a href=\"https://docs.apify.com/platform/integrations/slack\">Slack integration</a>.",
        ],
        costs=[
            ["Product rows (first run, and any full run)", "$0.50 per 1,000 products"],
            ["Change rows (each daily alert)", "$1 per 1,000 changes"],
            ["Unchanged products, store summary", "Free"],
            ["Example: 3 stores x 100 products, daily, about 5 changes a day", "<b>about $0.30 a month</b>"],
            ["Example: 10 stores, 30 changes a day", "about $0.90 a month after the first run"],
        ],
        offer_what="your competitor's store link",
        compare=table(["", "Pandapi price alerts", "Prisync", "Price2Spy"], [
            ["Price", "<b>about $0.30 a month</b> for 3 stores x 100 products", "from $99 a month (100 products)", "about $40 to $158 a month by plan"],
            ["Setup", "paste store links, whole catalog watched", "add each product URL", "add each product URL"],
            ["New products from a competitor", "✅ seen the day they appear", "only products you added", "only products you added"],
            ["Price, stock, new and removed alerts", "✅", "✅", "✅"],
            ["Any website, Amazon, big retailers", "❌ Shopify and WooCommerce stores only", "✅", "✅"],
            ["Dashboard, repricing, MAP monitoring", "❌ (email, Slack, Google Drive)", "✅", "✅"],
        ]) + '<p>Prisync and Price2Spy are the better pick if you need Amazon or big retailers, repricing rules or a dashboard for a team. If your competitors are Shopify or WooCommerce stores and you want the changes in your inbox, this costs a few cents.</p><p class="sources">Prices: Prisync plans listed at $99, $199 and $399 a month; Price2Spy figures differ between sources, so check their pricing page. Checked 24 November 2026.</p>',
        learn=[
            (APIFY + "shopify-products-price-monitor", "Full guide and all options on Apify (best sellers, collections, WooCommerce)"),
        ],
        faq=[
            ("Which stores can I watch?", "Any public Shopify or WooCommerce store. Paste the store's home page link; the platform is detected for you. Most direct-to-consumer brands run on Shopify."),
            ("How much does it cost?", "About $0.30 a month for 3 stores of 100 products checked daily. You pay $0.50 per 1,000 products on the first run and $1 per 1,000 changes after that. Apify's free plan includes $5 of credit every month."),
            ("Do I need to know how to code?", "No. You open the ready-made task, paste store links, click Schedule and add the email integration. Everything is buttons."),
            ("Will I get an email when nothing changed?", "The run still finishes and you can choose to be emailed only when it succeeds. A day with no changes returns an empty list and costs nothing."),
            ("Can I see the price history?", "Yes. Each change row carries the product's price history (every price change the monitor has seen, up to 200) plus the lowest and highest price seen. Download any run as Excel or CSV to open it in Google Sheets."),
            ("Is this allowed?", "The tool reads the public product catalog every Shopify and WooCommerce store publishes for browsers and search engines, at a polite rate, without logging in."),
        ],
    ),
    dict(
        slug="government-tender-alerts",
        actor="public-tenders-feed",
        task_id="hdv8OVr0yH8q0Oqhg",
        task_name="daily-government-tender-alerts",
        short="Tender alerts",
        title="Government tender alerts on your keywords: US, EU, UK, Canada",
        meta="Daily government tender alerts on your keywords from SAM.gov, TED, Contracts Finder, Find a Tender, CanadaBuys and the World Bank. No code, under $1 a month.",
        h1="Government tender alerts: new tenders on your keywords every morning",
        lede="Tell us your keywords once. Every morning you get the <b>new public tenders</b> that match, from <b>SAM.gov</b> (US), <b>TED</b> (EU), <b>Contracts Finder</b> and <b>Find a Tender</b> (UK), <b>CanadaBuys</b> and the <b>World Bank</b>, in one list with buyer, deadline, days left and value. You never get the same notice twice.",
        price_line="<b>About $0.60 a month</b> for a daily alert that finds about 10 new tenders a day. Apify's free plan gives you $5 of credit every month, so this runs free.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real rows from our run on 19 November 2026 across all six portals (notices from the last 7 days). We picked the software and IT notices, the way an alert on \"software\", \"cloud\" and \"IT services\" would.</p>"
            + table(["Tender", "Buyer", "Where", "Deadline", "Value"], [
                ['<a href="https://sam.gov/opp/68cdbc02972e4a4699f4f486d18dddb2/view">GeoJobe Software with Training and Support</a>', "NOAA, Dept of Commerce", "US · SAM.gov", "2 Dec 2026", "not published"],
                ['<a href="https://www.find-tender.service.gov.uk/Notice/109754-2026">Invest NI: Global Spirits Database</a>', "Invest Northern Ireland", "UK · Find a Tender", "17 Dec 2026", "£170,000 (about $223,864)"],
                ['<a href="https://www.find-tender.service.gov.uk/Notice/109643-2026">Statistical Process Control (SPC) Data Management Software System</a>', "NHS Blood and Transplant, Bristol", "UK · Find a Tender", "see notice", "not published"],
                ['<a href="https://ted.europa.eu/en/notice/-/detail/807268-2026">Microsoft 365 A3 subscription licences for 1,700 staff and 68,000 students</a> (title in Polish)', "Uniwersytet Szczeciński", "Poland · TED", "18 Dec 2026", "not published"],
                ['<a href="https://ted.europa.eu/en/notice/-/detail/807273-2026">Renewal of office and server software licences for 3 years</a> (title in Slovenian)', "Radiotelevizija Slovenija", "Slovenia · TED", "22 Dec 2026", "not published"],
                ['<a href="https://projects.worldbank.org/en/projects-operations/procurement-detail/OP00482050">Integrated Security Monitoring and Cloud Licensing Solution</a>', "MSME Development Agency", "Egypt · World Bank", "1 Dec 2026", "not published"],
            ])
            + "<p>Every row also has the notice type, days left, published date, CPV/NAICS codes, the buyer's city and a description. The same run returned 300 notices in total, 50 from each portal.</p>"
            + '<p class="sources">Source: Apify run fsMMdAf5AutLai7At, dataset cM9iRYSlW5VYi7JI7, 19 Nov 2026. The Polish and Slovenian titles are shown in English here; the alert gives the original title.</p>'
        ),
        alert_title="What the daily alert tells you",
        alert=[
            "<b>Only new notices</b>: alert mode remembers every notice it sent you under your alert name.",
            "<b>Title, buyer, country and portal</b>, with a link to the official notice.",
            "<b>Deadline and days left</b>; tenders that already closed are hidden.",
            "<b>Value</b> in the original currency and converted to US dollars and euros, where the buyer published it.",
            "Filters you can add: <b>exclude words</b>, <b>countries</b>, <b>CPV or NAICS codes</b>, <b>minimum value</b>, tenders only or pre-notices too.",
        ],
        steps=[
            "<b>Create a free Apify account (1 minute).</b> Click <b>Set it up in 3 minutes</b>. Apify opens with our ready-made task already attached. Click <b>Continue with Google</b> (or type your email). It's free: $5 of credit every month, no card.<br><img class=\"shot\" src=\"../assets/setup/signup-tender-alerts.webp\" alt=\"Apify sign-up screen showing: Start with Daily government tender alerts on your keywords\" width=\"560\" height=\"620\" loading=\"lazy\">",
            "<b>Fill in two things.</b> The task opens with an example filled in. Put your own words in <b>Keywords</b> (for example \"cleaning services\" or \"cybersecurity\") and give the alert a name. Then type the email address you signed up with in <b>Email me the report at</b> (Apify only sends to your own account's address).",
            "<b>Click Save &amp; Start.</b> About a minute later the first report is in your inbox. It lists the matching tenders, soonest deadline first, with buyer, value and link; from then on you only get tenders you haven't seen.",
            "<b>Make it run every morning.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Daily</b> and a time, click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b> (new schedules start switched off). Apify's guide with pictures: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>.",
            "<b>Optional: Slack.</b> On your task's <b>Integrations</b> tab add <b>Slack</b> and use this message: <code>{{resource.statusMessage}}</code>. It posts the report's first line (\"4 new tenders on your keywords (US 3, GB 1)\"). Apify's guide: <a href=\"https://docs.apify.com/platform/integrations/slack\">Slack integration</a>.",
        ],
        costs=[
            ["Each notice returned", "$2 per 1,000 ($0.002 each)"],
            ["Notices filtered out, or already sent", "Free"],
            ["Example: daily alert, about 10 new notices a day", "<b>about $0.60 a month</b>"],
            ["Example: broad alert, about 40 new notices a day", "about $2.40 a month"],
        ],
        offer_what="your keywords and countries",
        compare=table(["", "Pandapi tender alerts", "US bid alert services", "GovSpend, GovWin"], [
            ["Price", "<b>about $0.60 a month</b>", "$49 to $199 a month and up", "custom quote (GovWin $5k to $25k a year)"],
            ["US federal (SAM.gov)", "✅", "✅", "✅"],
            ["EU (TED), UK, Canada, World Bank", "✅ all in one list", "❌", "❌"],
            ["US state and local bids", "❌", "some", "✅"],
            ["Only new notices, daily email", "✅", "✅", "✅"],
            ["Bid management, contract history", "❌", "some", "✅"],
        ]) + '<p>GovSpend and GovWin are the better pick if you sell to US state and local government or need contract history and buyer intelligence. If you bid on federal, European, UK, Canadian or World Bank work and want a daily list on your keywords, this costs cents.</p><p class="sources">US alert services compared: GovContractFinder ($49 to $99 a month), SamSearch (from $199 a month), BidPrime (sources differ). Checked 13 and 24 November 2026.</p>',
        learn=[
            ("../government-tenders-api/", "Guide: government tenders from 6 portals in one feed"),
            ("../sam-gov-api-alternative/", "SAM.gov alternatives compared"),
            ("../ted-tenders-api/", "TED tenders: the free way and the daily feed"),
            ("../contracts-finder-api/", "UK Contracts Finder: the free way and the daily feed"),
        ],
        faq=[
            ("Which portals are covered?", "SAM.gov (US federal), TED (EU and EEA), Contracts Finder and Find a Tender (UK), CanadaBuys and World Bank procurement. All official, public sources."),
            ("How much does it cost?", "$2 per 1,000 notices returned and nothing for notices filtered out. A daily alert with about 10 new tenders costs about $0.60 a month, inside Apify's free $5 monthly credit."),
            ("Will I get the same tender twice?", "No. Alert mode remembers what it sent under your alert name and returns only new notices on the next run."),
            ("Do I need to know how to code?", "No. You open the ready-made task, type your keywords, click Schedule and add the email integration."),
            ("Can I filter by country or category code?", "Yes: countries (ISO codes like US, GB, DE), CPV codes for Europe, NAICS codes for the US, a minimum value, and words to exclude."),
            ("Does it include US state and local tenders?", "Not yet. In the US it covers federal notices from SAM.gov."),
        ],
    ),
    dict(
        slug="see-competitors-google-ads",
        actor="google-ads-transparency-scraper",
        task_id="6Xf915hfsjdfEU7BO",
        task_name="competitor-google-ads-alerts",
        short="Competitor Google ads",
        title="See competitors' Google ads, with new ad alerts",
        meta="See every Google ad a competitor runs, with ad copy and run dates, and get a weekly alert when they start or stop an ad. No code, a few cents a month.",
        h1="See your competitors' Google ads, and get told when they launch new ones",
        lede="Type a competitor's website. You get <b>every ad they run on Google</b> (Search, YouTube, Shopping, Maps and Play) from Google's own Ads Transparency Center, with the <b>ad copy</b>, format and <b>first and last shown dates</b>. Put it on a weekly schedule and you get <b>only the ads that started or stopped</b>, so you see a new campaign the week it launches.",
        price_line="<b>About $0.40 for the first look</b> at 3 competitors, then <b>a few cents a month</b> for weekly new-ad alerts. Apify's free plan gives you $5 of credit every month, so this runs free.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real rows from our run on 24 November 2026 on <b>allbirds.com</b>, limited to 3 ads for the demo (Google says Allbirds has 700 to 800 ads).</p>"
            + table(["Ad", "Format", "First shown", "Last shown", "Running"], [
                ['<a href="https://adstransparency.google.com/advertiser/AR01371945870127267841/creative/CR13057829271475585025">Allbirds® Comfortable Shoes - Shoes Made To Move</a>: "Made from TENCEL™ Lyocell (tree fiber) to stay breathable, moisture-wicking, and cool." Sitelinks: Men\'s Sale, Men\'s Shoes, Women\'s Shoes', "Text (Search), www.allbirds.co.uk", "4 Oct 2026", "24 Nov 2026", "Yes, 51 days"],
                ['<a href="https://adstransparency.google.com/advertiser/AR01371945870127267841/creative/CR02046636767917899777">Image ad</a> (preview link to Google)', "Image", "2 Jun 2025", "24 Nov 2026", "Yes, 508 days"],
            ])
            + "<p><b>Advertiser summary from the same run (free):</b> Allbirds Inc, about 700 to 800 ads reported by Google; of the ads read, all are running now and 1 started in the last 30 days, a local Black Friday \"Early Access: up to 50% off\" ad. Longest running: the image ad above, 508 days.</p>"
            + '<p class="sources">Source: Apify run UtQIR3h3qwlEaVvZV, dataset AhYsNaM8fja4TEOf6, 24 Nov 2026. We left the Black Friday ad out of the table because its text was read from an image and came out partly garbled; the alert includes it with a link to the original.</p>'
        ),
        alert_title="What the weekly alert tells you",
        alert=[
            "<b>New ads</b> a competitor started since last week, with headline, description, display URL and sitelinks where Google keeps them as text.",
            "<b>Stopped ads</b>: ads that were running last week and aren't now.",
            "<b>Format and where it runs</b>: text, image or video, with a link to the ad on Google's Transparency Center.",
            "<b>First and last shown dates</b> and days running, so you can tell a test from a long-running winner.",
            "A free <b>summary</b> per competitor: ads running now, started in the last 30 days, longest running.",
        ],
        steps=[
            "<b>Open the ready-made task.</b> Click <b>Set it up in 3 minutes</b>, sign in to Apify (free, no card), replace allbirds.com with your competitors' websites or names (one per line) and click <b>Save &amp; Start</b>. The first run lists every ad and saves them.",
            "<b>Schedule it.</b> On the task, click <b>Schedule</b> and pick <b>Weekly</b> (or daily in a busy season). Each later run returns only ads that started or stopped.",
            "<b>Get it in Slack or Google Drive.</b> On the task, open <b>Integrations</b> and add <a href=\"https://docs.apify.com/platform/integrations/slack\" rel=\"noopener\">Slack</a> or <a href=\"https://docs.apify.com/platform/integrations/drive\" rel=\"noopener\">Google Drive</a>, so each run's ads arrive where you already look.",
        ],
        costs=[
            ["Each ad returned", "$1.20 per 1,000 ($0.0012 each)"],
            ["Advertiser summary, unchanged ads", "Free"],
            ["Example: first look at 3 competitors, 100 ads each", "<b>about $0.36</b>"],
            ["Example: weekly alert, about 10 new or stopped ads a week", "<b>about $0.05 a month</b>"],
        ],
        offer_what="your competitors' websites",
        compare=table(["", "Pandapi competitor ads", "SpyFu", "Other Apify ad scrapers"], [
            ["Price", "<b>cents a month</b>", "from $39 a month", "$1.90 to $5 per 1,000 ads"],
            ["Source", "Google Ads Transparency Center (every ad Google shows)", "its own crawl of Google results", "Google Ads Transparency Center"],
            ["Search, YouTube, Shopping, Maps and Play ads", "✅", "Search mainly", "✅"],
            ["New ads since last time", "✅", "history view", "some (new only)"],
            ["Ads that stopped", "✅", "❌", "❌"],
            ["Keywords, estimated spend, rankings", "❌", "✅", "❌"],
        ]) + '<p>SpyFu is the better pick if you need the keywords a competitor bids on, estimated spend or years of history. If you want to see their actual ads and know when new ones launch, this costs cents.</p><p class="sources">SpyFu plans: $39 Basic, $89 to $119 Pro, $187 to $249 Team a month depending on the source and billing; check spyfu.com. Apify prices from each actor\'s Store page, 21 November 2026.</p>',
        learn=[
            (APIFY + "google-ads-transparency-scraper", "Full guide and all options on Apify (countries, formats, dates, OCR)"),
        ],
        faq=[
            ("Where do the ads come from?", "From Google's public Ads Transparency Center, which lists every ad an advertiser has shown on Google Search, YouTube, Shopping, Maps and Play in the past."),
            ("How much does it cost?", "$1.20 per 1,000 ads. A first look at 3 competitors with 100 ads each is about $0.36, and a weekly alert after that is a few cents a month. Apify's free plan includes $5 of credit every month."),
            ("Does it show the ad text?", "Yes, for text ads: headline, description, display URL and sitelinks where Google keeps them as text, or read from the ad image. Image and video ads come with a preview link."),
            ("Can I see ads in one country only?", "Yes. Set Region to a country (for example United Kingdom) to see only ads shown there."),
            ("Does it show keywords or ad spend?", "No. Google's Transparency Center doesn't publish keywords or spend, so no tool built on it can show them."),
            ("Do I need to know how to code?", "No. You open the ready-made task, type competitor websites, click Schedule and add the email integration."),
        ],
    ),
]

BY_SLUG = {p["slug"]: p for p in PAGES}


def setup_url(p):
    return f"https://console.apify.com/create-task-from-example/{p['task_id']}"


def task_url(p):
    return utm(f"{APIFY}{p['actor']}/examples/{p['task_name']}", p["actor"], p["slug"])


def offer_links(p):
    title = quote(f"Free sample report: {p['short']}")
    body = quote(f"What should we check? ({p['offer_what']}):\n\n\nWhere should we send the report? (an email address or your X handle):\n")
    gh = f"{EXAMPLES_REPO}/issues/new?title={title}&amp;body={body}&amp;labels=sample-report"
    return gh, X_PROFILE


def page_html(p, head, foot, site_url):
    slug, actor = p["slug"], p["actor"]
    path = slug + "/"
    url = f"{site_url}/{path}" if site_url else ""
    ld = [
        {"@context": "https://schema.org", "@type": "Service", "name": p["h1"], "description": p["meta"],
         "provider": {"@type": "Organization", "name": "Pandapi"}, "areaServed": "Worldwide",
         **({"url": url, "image": f"{site_url}/assets/icons/api/{actor}.png"} if site_url else {})},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]
    if site_url:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Pandapi Tools", "item": f"{site_url}/"},
            {"@type": "ListItem", "position": 2, "name": "Alerts", "item": f"{site_url}/guides/#alerts"},
            {"@type": "ListItem", "position": 3, "name": p["h1"], "item": url}]})
    extra = '<link rel="stylesheet" href="../assets/guides.css">\n' + "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    gh, xp = offer_links(p)
    setup = (f'<div class="card cta setup"><img src="../assets/icons/api/{actor}.png" alt="" width="56" height="56">'
             f'<p>{p["price_line"]}</p>'
             f'<a class="btn" href="{setup_url(p)}" rel="nofollow">Set it up in 3 minutes</a>'
             f'<span class="setup-note">Opens a ready-made Apify task with the example filled in. Free account, no card. '
             f'<a href="{task_url(p)}">See the task first</a>.</span></div>')
    others = [q for q in PAGES if q["slug"] != slug]
    out = [head(p["title"], p["meta"], path, f"api/{actor}.png", extra)]
    out.append(f"""<main><div class="wrap article outcome">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../">Pandapi Tools</a> › <a href="../guides/#alerts">Alerts</a> › <span>{E(p['short'])}</span></nav>
<div class="hero"><img src="../assets/icons/api/{actor}.png" alt="" width="64" height="64"><h1>{E(p['h1'])}</h1></div>
<p class="lede">{p['lede']}</p>
{setup}
<section class="content prose">
<h2>{p['sample_title']}</h2>
{p['sample']()}
<h2>{p['alert_title']}</h2>
<ul>{''.join(f'<li>{x}</li>' for x in p['alert'])}</ul>
<h2>Set it up in 3 minutes, no code</h2>
<ol class="steps">{''.join(f'<li>{s}</li>' for s in p['steps'])}</ol>
<p><a class="btn" href="{setup_url(p)}" rel="nofollow">Set it up in 3 minutes</a></p>
<h2>What it costs</h2>
{table(["What", "Price"], p['costs'])}
<p>No subscription and no start fee. Apify's free plan gives you $5 of credit every month, and you can set a maximum cost per run so a run never spends more than you allow.</p>
<div class="card offer">
<h2>Get a free sample report first</h2>
<p>Not sure it's worth it? Send us {E(p['offer_what'])} and we'll run it once and send you the report, free. We do up to 5 free reports a week.</p>
<p><a class="btn" href="{gh}" rel="nofollow">Ask on GitHub</a> <a class="btn secondary" href="{xp}" rel="nofollow">Message us on X</a></p>
</div>
<h2>How it compares</h2>
{p['compare']}
<h2>Questions</h2>
{''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in p['faq'])}
<h2>Learn more</h2>
<ul>{''.join(f'<li><a href="{utm(u, actor, slug) if u.startswith("http") else u}">{E(label)}</a></li>' for u, label in p['learn'])}</ul>
</section>
<section class="content"><h2>Other alerts you can set up</h2><div class="grid">{''.join(tile(q) for q in others)}</div></section>
<aside class="card devbox" aria-label="For developers">
<h2>For developers</h2>
<p>The same engine is an Apify Actor with an HTTP API, webhooks and Python/JavaScript clients: <a href="{utm(APIFY + actor + '/api', actor, slug)}">API docs</a>. It's also in the <a href="{utm(APIFY + 'pandapi-mcp-server', actor, slug)}">Pandapi MCP server</a> for Claude and Cursor, and in the <a href="https://www.npmjs.com/package/n8n-nodes-pandapi">n8n node</a>.</p>
</aside>
<p class="byline">Updated {UPDATED_TEXT} · by the Pandapi team</p>
</div></main>
""")
    out.append(foot("../"))
    return "".join(out)


def tile(p, depth="../"):
    return (f'<a class="card tile" href="{depth}{p["slug"]}/"><img src="{depth}assets/icons/api/{p["actor"]}.png" alt="" width="56" height="56" loading="lazy">'
            f'<div><h3>{E(p["h1"].split(":")[0])}</h3><p>{E(p["meta"].split(". ")[0])}.</p></div></a>')
