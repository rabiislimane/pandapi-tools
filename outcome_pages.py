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
            ("Do I need to know how to code?", "No. You open the ready-made task, paste store links, type your email and add a daily schedule. Everything is buttons."),
            ("Will I get an email when nothing changed?", "No. By default the email comes only when a price, stock or product changed (set \"Send the email\" to \"After every run\" if you want one every day). A day with no changes costs nothing."),
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
            ("Do I need to know how to code?", "No. You open the ready-made task, type your keywords and your email, and add a daily schedule."),
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
            "<b>Create a free Apify account (1 minute).</b> Click <b>Set it up in 3 minutes</b>. Apify opens with our ready-made task attached. Click <b>Continue with Google</b> (or type your email). It's free: $5 of credit every month, no card.",
            "<b>Fill in two things.</b> Replace allbirds.com with your competitors' websites or names, one per line. Then type the email address you signed up with in <b>Email me the report at</b> (Apify only sends to your own account's address).",
            "<b>Click Save &amp; Start.</b> About a minute later the first report is in your inbox: every ad your competitors run now, saved as the starting point. From then on you only hear about new ads.",
            "<b>Make it run every week.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Weekly</b> (or Daily), click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b> (new schedules start switched off). Apify's guide with pictures: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>. Weeks with no new ads send no email.",
            "<b>Optional: Slack.</b> On your task's <b>Integrations</b> tab add <b>Slack</b> and use this message: <code>{{resource.statusMessage}}</code>. It posts the report's first line (\"3 new ads from your competitors (allbirds.com 2, rothys.com 1)\"). Apify's guide: <a href=\"https://docs.apify.com/platform/integrations/slack\">Slack integration</a>.",
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
            ("Do I need to know how to code?", "No. You open the ready-made task, type competitor websites and your email, and add a weekly schedule."),
        ],
    ),
    dict(
        slug="domain-ssl-expiry-alerts",
        actor="domain-intelligence",
        task_id="HbeTglnLcJnVUOlc1",
        task_name="domain-ssl-expiry-alerts",
        updated=("2026-11-26", "26 November 2026"),
        short="Domain and SSL expiry",
        title="Domain and SSL expiry alerts for all your client domains",
        meta="A weekly report on every domain you manage: domain expiry, SSL certificate expiry, SPF and DMARC problems, in plain words. No code, about $0.30 a month for 50 domains.",
        h1="Domain and SSL expiry alerts: never let a client's domain or certificate lapse",
        lede="Paste every domain you look after, yours or your clients'. Each week you get one row per domain with the <b>domain expiry date</b>, the <b>SSL certificate expiry</b>, the registrar, the email provider and <b>email security (SPF, DMARC, DKIM)</b>, and a plain list of problems like <b>\"SSL certificate expires in 6 days\"</b>.",
        price_line="<b>About $0.30 a month</b> for a weekly report on 50 domains. Apify's free plan gives you $5 of credit every month, so this runs free.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real rows from our run on 24 November 2026 on three domains: two well-known ones and one that isn't registered.</p>"
            + table(["Domain", "Domain expires", "SSL expires", "Email security", "Problems found"], [
                ["github.com", "9 Oct 2028 (684 days), MarkMonitor", "27 Jan 2027 (64 days), Sectigo", "Microsoft 365; SPF 10 of 10 lookups; DMARC quarantine; DKIM found", "none"],
                ["bbc.co.uk", "13 Dec 2034 (2,940 days)", "24 Jan 2027 (60 days), GlobalSign", "Broadcom Email Security; SPF 4 lookups; DMARC reject", "No DKIM key found on common selectors"],
                ["pandapi-nope-2026x.com", "not registered (available)", "", "", "none"],
            ])
            + "<p>github.com sits exactly at SPF's limit of 10 DNS lookups: one more include and its SPF fails at receivers. That's the kind of thing the problem list is there to catch.</p>"
            + '<p class="sources">Source: Apify run agdNf1krwlCh4kmBT, dataset hqQLoQRapJczI4WlM, 24 Nov 2026. Expiry dates come from each registry\'s official RDAP service and each site\'s live certificate.</p>'
        ),
        alert_title="What the weekly report tells you",
        alert=[
            "<b>Domain expiry date and days left</b>, registrar and registry locks, straight from the registry (1,200+ extensions).",
            "<b>SSL certificate</b>: issuer, expiry date, days left, and whether it covers the host and is trusted.",
            "<b>Email security</b>: SPF with its DNS-lookup count (over 10 and mail fails), DMARC policy, DKIM keys, MTA-STS.",
            "A plain <b>problem list</b> per domain: domain expires within 30 days, certificate expires within 14 days, no DMARC, too many SPF lookups.",
            "Optional <b>change mode</b>: only domains where something changed (renewed, new certificate, new mail provider, DMARC changed).",
        ],
        steps=[
            "<b>Create a free Apify account (1 minute).</b> Click <b>Set it up in 3 minutes</b>. Apify opens with our ready-made task attached. Click <b>Continue with Google</b> (or type your email). It's free: $5 of credit every month, no card.",
            "<b>Fill in two things.</b> Replace the example domains with yours, one per line (links and email addresses work too). Then type the email address you signed up with in <b>Email me the report at</b> (Apify only sends to your own account's address).",
            "<b>Click Save &amp; Start.</b> About a minute later you have the first report: every domain and certificate that expires soon, soonest first. If one needs attention, it's in your inbox too.",
            "<b>Make it run every week.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Weekly</b>, click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b> (new schedules start switched off). Apify's guide with pictures: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>. Quiet weeks send no email.",
            "<b>Optional: Slack.</b> On your task's <b>Integrations</b> tab add <b>Slack</b> and use this message: <code>{{resource.statusMessage}}</code>. It posts the report's first line (\"1 domain needs attention: 1 domain expires within 30 days\"). Apify's guide: <a href=\"https://docs.apify.com/platform/integrations/slack\">Slack integration</a>.",
        ],
        costs=[
            ["Each domain checked (registered or available)", "$1.50 per 1,000 ($0.0015 each)"],
            ["Invalid input, registry didn't answer", "Free"],
            ["Example: 50 client domains, weekly", "<b>about $0.30 a month</b>"],
            ["Example: 300 domains, weekly", "about $1.95 a month"],
        ],
        offer_what="the domains you manage",
        compare=table(["", "Pandapi expiry report", "UptimeRobot", "Other Apify domain checkers"], [
            ["Price", "<b>about $0.30 a month</b> for 50 domains weekly", "SSL and domain expiry on paid plans only", "$2 to $3 per 1,000 domains, most with a start fee"],
            ["Domain expiry", "✅", "✅", "✅"],
            ["SSL expiry", "✅ same row", "✅", "❌ separate tool"],
            ["SPF lookup count, DMARC, DKIM", "✅", "❌", "presence only, or ❌"],
            ["Plain problem list per domain", "✅", "❌", "❌"],
            ["Uptime checks every minute, SMS alerts", "❌", "✅", "❌"],
        ]) + '<p>UptimeRobot is the better pick if you also need uptime checks every minute and an SMS the moment something breaks. If you want one weekly table of every client domain with expiry dates and email-security problems, this costs cents.</p><p class="sources">UptimeRobot: SSL and domain expiry alerts are listed for paid plans on uptimerobot.com/pricing (checked 26 November 2026). Apify prices from each actor\'s Store page, 24 November 2026.</p>',
        learn=[
            (APIFY + "domain-intelligence", "Full guide and all options on Apify (availability checks, DKIM selectors, change mode)"),
        ],
        faq=[
            ("Where do the expiry dates come from?", "Domain dates come from each registry's official RDAP service (WHOIS where a registry has none). SSL dates come from the certificate each site serves right now."),
            ("How much does it cost?", "$1.50 per 1,000 domains checked. A weekly report on 50 domains is about $0.30 a month, inside Apify's free $5 monthly credit. Domains the registry didn't answer for are free."),
            ("Will it email me 30 days before expiry?", "Yes. Type your Apify account email in \"Email me the report at\". The weekly email comes when a domain expires within 30 days or a certificate within 14 days (you can change both numbers), with one line per domain and the expiry date. A week with nothing to report sends nothing."),
            ("Some domains show no expiry date. Why?", "A few registries (for example .de) don't publish expiry dates. The report says so for those domains."),
            ("Do I need to know how to code?", "No. You open the ready-made task, paste your domains, type your email and add a weekly schedule."),
        ],
    ),
    dict(
        slug="app-review-alerts",
        actor="app-store-reviews-scraper",
        task_id="uHrs9Rjcw3VtIOEUs",
        task_name="app-store-review-alerts",
        alt_setup=("Google Play version", "Y90LfxPgMSuWchgIf", "google-play-reviews-scraper", "google-play-review-alerts"),
        updated=("2026-11-26", "26 November 2026"),
        short="App review alerts",
        title="App Store review monitoring: new reviews of any app daily",
        meta="Get every new App Store or Google Play review of your app or a competitor's, daily, in Slack or a sheet, with a free summary of ratings and complaints. Cents a month.",
        h1="App Store review monitoring: get every new review of any app, every morning",
        lede="Paste your app, or a competitor's, from the <b>App Store</b> or <b>Google Play</b>. Every morning you get <b>only the reviews written since yesterday</b>: stars, title, text, country and app version, plus a free summary (average rating, share of 1 and 2 star reviews, the words people complain about). Catch a bad update the day it ships.",
        price_line="<b>About $0.10 a month</b> to watch 5 apps in 3 countries that get 20 new reviews a day. Apify's free plan gives you $5 of credit every month, so this runs free.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real rows from our run on 20 November 2026 on <b>Notion</b>'s iPhone and iPad app, US App Store, the 10 most recent reviews (5 shown).</p>"
            + table(["Stars", "Review", "Date"], [
                ["★★★☆☆", "<b>iPad App Needs Fixes</b>: \"The sidebar doesn't work properly at all, you can't access the right sidebar... A safari web app works better.\"", "18 Nov 2026"],
                ["★☆☆☆☆", "<b>App crashes instantly every time it opens.</b> \"Newest version broke everything.\"", "18 Nov 2026"],
                ["★★☆☆☆", "<b>Nav</b>: \"The navigation is confusing because of the repetition where it says recent...\"", "16 Nov 2026"],
                ["★☆☆☆☆", "<b>Latest version keeps crashing</b>", "14 Nov 2026"],
                ["★★★★☆", "<b>App won't open</b>: \"I've just run the update on the App Store for my iPad app and it crashes when I try to open the app.\"", "13 Nov 2026"],
            ])
            + "<p><b>Summary from the same run (free):</b> average rating of the 10 recent reviews 2.1 (the app's all-time rating is 4.8); 7 of 10 are 1 or 2 stars; most-used complaint words: \"version\", \"update\", \"latest\". A daily alert would have flagged this update within a day.</p>"
            + '<p class="sources">Source: Apify run dAl4XyUduxobwOcPU, dataset vWsp1Ozki8ROC65os, 20 Nov 2026. Reviewer names are not collected.</p>'
        ),
        alert_title="What the daily alert tells you",
        alert=[
            "<b>Only new reviews</b> since the last run, remembered per alert name, so nothing arrives twice.",
            "<b>Stars, title, text, date, country and app version</b> for each review; on Google Play also the developer's reply.",
            "A free <b>summary</b>: average rating, rating split, share of negative reviews, top complaint words and ratings by app version.",
            "Filters: <b>only 1 and 2 star reviews</b>, keywords (\"crash\", \"refund\"), several countries or languages at once.",
            "Works for <b>competitors' apps</b> too: see what their users hate before you build the same thing.",
        ],
        steps=[
            "<b>Open the ready-made task.</b> Click <b>Set it up in 3 minutes</b> (or the Google Play version), create a free Apify account (no card), replace the example app with your app's store link, pick countries, and click <b>Save &amp; Start</b>. The first run saves today's reviews as the starting point.",
            "<b>Make it run every morning.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Daily</b>, click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b>. Apify's guide: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>.",
            "<b>Get it in Slack or Google Drive.</b> On the task, open <b>Integrations</b> and add <a href=\"https://docs.apify.com/platform/integrations/slack\" rel=\"noopener\">Slack</a> or <a href=\"https://docs.apify.com/platform/integrations/drive\" rel=\"noopener\">Google Drive</a>, so new reviews land in your team channel or a spreadsheet.",
        ],
        costs=[
            ["App Store review", "$0.15 per 1,000"],
            ["Google Play review", "$0.10 per 1,000"],
            ["Summary, apps not found", "Free"],
            ["Example: 5 apps, 3 countries, 20 new reviews a day", "<b>about $0.10 a month</b>"],
            ["Example: one big app, 500 new reviews a day", "about $2.25 a month"],
        ],
        offer_what="your app's store link (and a competitor's)",
        compare=table(["", "Pandapi review alerts", "AppFollow", "Other Apify review scrapers"], [
            ["Price", "<b>cents a month</b>, any number of apps", "free for 2 apps; paid plans from about $29 a month", "$0.10 to $0.15 per 1,000 reviews"],
            ["App Store and Google Play", "✅", "✅", "usually one store per tool"],
            ["Only new reviews since last time", "✅", "✅", "❌ most have no memory"],
            ["Competitor apps", "✅", "paid plans", "✅"],
            ["Rating and complaint summary", "✅ free", "✅ dashboards", "❌"],
            ["Reply to reviews, tags, ASO tools", "❌", "✅", "❌"],
        ]) + '<p>AppFollow is the better pick if your team replies to reviews from one inbox or needs ASO keyword tools. If you want new reviews of your apps and your competitors\' apps in Slack or a sheet, this costs cents.</p><p class="sources">AppFollow prices from third-party listings (Capterra, SoftwareSuggest), checked 26 November 2026; check appfollow.io for current plans.</p>',
        learn=[
            ("../export-app-store-reviews/", "Guide: export App Store reviews to CSV"),
            ("../export-google-play-reviews/", "Guide: export Google Play reviews to CSV"),
            ("../appfollow-alternative/", "AppFollow alternatives compared"),
        ],
        faq=[
            ("Which apps can I watch?", "Any public app on the App Store or Google Play: yours or a competitor's. Paste the store link; add several apps, one per line."),
            ("How much does it cost?", "$0.15 per 1,000 App Store reviews and $0.10 per 1,000 Google Play reviews. 5 apps in 3 countries with 20 new reviews a day is about $0.10 a month, inside Apify's free $5 monthly credit."),
            ("Will I get the same review twice?", "No. The alert remembers the reviews it returned under your alert name and only returns new ones next time."),
            ("Can I get only bad reviews?", "Yes. Set the maximum rating to 2 to get only 1 and 2 star reviews, or add keywords like \"crash\" or \"refund\"."),
            ("Do you collect reviewer names?", "No. Rows have the review, rating, date, country and version, not the reviewer's name."),
            ("Do I need to know how to code?", "No. You open the ready-made task, paste your app's link, click Schedule and add Slack or Google Drive."),
        ],
    ),
    dict(
        slug="hiring-alerts",
        actor="company-jobs-tracker",
        task_id="fYtUjoBZCBfpnO97F",
        task_name="hiring-alerts-target-companies",
        updated=("2026-11-26", "26 November 2026"),
        short="Hiring alerts",
        title="Hiring alerts: new jobs at your target companies",
        meta="Get an alert when the companies you sell to or recruit for post new jobs, live from their career sites, with a free hiring summary. No code, cents a month.",
        h1="Hiring signals: get an alert when your target companies post new jobs",
        lede="Name the companies you sell to, recruit for or want to work at. Each morning you get <b>only the jobs they posted since yesterday</b>: title, department, location, remote or hybrid and <b>salary</b> where published, live from their own career sites. A company hiring 5 salespeople or its first data engineer is a buying signal.",
        price_line="<b>About $0.13 a month</b> to watch 20 companies posting 30 new jobs a week (the first run, which lists every open job, costs about $1 per 1,000 jobs). Apify's free plan gives you $5 of credit every month.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real rows from our run on 19 November 2026 on <b>Airbnb</b>, <b>Notion</b> and <b>Palantir</b>: the newest jobs.</p>"
            + table(["Company", "Job", "Where", "Salary", "Posted"], [
                ["Notion", '<a href="https://jobs.ashbyhq.com/notion/14879c7f-ded7-4e7f-932c-fb4a294afd68">Campaign Lead, Brand</a> (Marketing)', "San Francisco, hybrid", "$210,000 – $245,000", "18 Nov 2026"],
                ["Notion", '<a href="https://jobs.ashbyhq.com/notion/a8143379-6693-4046-b8cf-1528178d0f0f">CX Systems &amp; Automation Lead</a> (Customer Experience)', "San Francisco, hybrid", "$179,000 - $200,000", "18 Nov 2026"],
                ["Airbnb", '<a href="https://careers.airbnb.com/positions/8383877?gh_jid=8383877">Senior Connectivity Partner Manager</a> (Sales)', "United States, remote", "$139,000 — $163,000", "18 Nov 2026"],
                ["Palantir", '<a href="https://jobs.lever.co/palantir/e8bfc01c-620c-4b6a-b3f8-cd275228db06">Information Systems Security Engineer</a>', "Palo Alto, onsite", "$100,000 - $174,000", "18 Nov 2026"],
                ["Airbnb", '<a href="https://careers.airbnb.com/positions/8397762?gh_jid=8397762">Software Engineer, DevAI</a>', "United States, remote", "$162,000 — $190,000", "17 Nov 2026"],
            ])
            + "<p><b>Hiring summary from the same run (free):</b> Airbnb 197 open jobs, 97 posted in the last 30 days, 67% remote, top team Software Engineering (50). Notion 168 open, 60 in the last 30 days, top team Sales (66). Palantir 306 open, 20 in the last 30 days.</p>"
            + '<p class="sources">Source: Apify run 8a5VJYduhTMdgBMWW, dataset FyfJAOkrfN7aDkLhr, 19 Nov 2026 (565 jobs). Job posts are public company listings; no personal data is collected.</p>'
        ),
        alert_title="What the daily alert tells you",
        alert=[
            "<b>New jobs</b> each target company posted since the last run, with a link to apply or read more.",
            "<b>Title, department, location, remote/hybrid/onsite, salary range</b> where the company publishes it.",
            "<b>Closed jobs</b> (free): roles that were filled or pulled.",
            "A free <b>hiring summary</b> per company: open jobs, posted in the last 30 days, top departments, remote share.",
            "Filters: keywords (\"sales\", \"data engineer\"), locations, departments, remote only, only jobs with a salary.",
        ],
        steps=[
            "<b>Open the ready-made task.</b> Click <b>Set it up in 3 minutes</b>, create a free Apify account (no card), replace the example companies with yours (a name or their careers page link, one per line), and click <b>Save &amp; Start</b>. The first run lists every open job as the starting point.",
            "<b>Make it run every morning.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Daily</b>, click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b>. Apify's guide: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>.",
            "<b>Get it in Slack or Google Drive.</b> On the task, open <b>Integrations</b> and add <a href=\"https://docs.apify.com/platform/integrations/slack\" rel=\"noopener\">Slack</a> or <a href=\"https://docs.apify.com/platform/integrations/drive\" rel=\"noopener\">Google Drive</a>, so new jobs land where your team works.",
        ],
        costs=[
            ["Each job returned", "$1 per 1,000 ($0.001 each)"],
            ["Closed jobs, hiring summaries, companies not found", "Free"],
            ["Example: first run on 20 companies with 2,000 open jobs", "about $2 once"],
            ["Example: then 30 new jobs a week", "<b>about $0.13 a month</b>"],
        ],
        offer_what="the companies you want to watch",
        compare=table(["", "Pandapi hiring alerts", "TheirStack", "Other Apify job scrapers"], [
            ["Price", "<b>cents a month</b> after the first run", "free 200 credits; paid about $49 to $169 a month", "$5 to $12 per 1,000 jobs"],
            ["The companies you name, live from their career site", "✅ 11 job-board systems", "its own crawl", "some"],
            ["Only new jobs since last time", "✅", "✅", "some"],
            ["Closed jobs", "✅ free", "❌", "❌"],
            ["Find every company hiring for a role", "❌", "✅", "some"],
            ["Workday, LinkedIn, Indeed", "❌", "✅", "some"],
        ]) + '<p>TheirStack is the better pick when you want to discover companies hiring for a role across millions of firms. If you already know your target accounts and want their new jobs every morning, this costs cents.</p><p class="sources">TheirStack prices from its own comparison pages and third-party reviews, checked 26 November 2026. Apify prices from each actor\'s Store page, 18 November 2026.</p>',
        learn=[
            ("../company-jobs-api/", "Guide: every open job at the companies you name"),
            ("../theirstack-alternative/", "TheirStack alternatives compared"),
        ],
        faq=[
            ("Which career sites work?", "Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Recruitee, BambooHR, Rippling, Teamtailor, Personio and Breezy. Type a company name or paste its careers page. Workday sites aren't supported yet."),
            ("How much does it cost?", "$1 per 1,000 jobs returned; closed jobs and summaries are free. The first run lists every open job, then 20 companies posting 30 new jobs a week cost about $0.13 a month."),
            ("Why is hiring a sales signal?", "A company hiring for a team usually gets budget for that team's tools. New sales, data or security roles are a common trigger for outreach."),
            ("Can I watch only some roles?", "Yes. Add keywords, locations or departments and only matching new jobs are returned."),
            ("Do I need to know how to code?", "No. You open the ready-made task, type company names, click Schedule and add Slack or Google Drive."),
        ],
    ),
    dict(
        slug="website-technology-lookup",
        actor="website-tech-stack-detector",
        task_id="AKqawsQ9kzUwEccd2",
        task_name="website-technology-lookup",
        updated=("2026-11-26", "26 November 2026"),
        short="Website tech lookup",
        title="Website technology lookup in bulk, with change alerts",
        meta="See what any list of websites is built with (Shopify, WordPress, HubSpot, analytics, ad pixels, hosting) and get an alert when a site changes. No code, $1.50 per 1,000 sites.",
        h1="Website technology lookup: see what any list of websites is built with",
        lede="Paste a list of websites, your prospects or competitors. You get one row per site with its <b>CMS, ecommerce platform, analytics, ad pixels, payments, hosting and email provider</b>, from 7,700 technologies, plus its <b>social links</b>. Put it on a weekly schedule and you hear when a prospect <b>switches platform or adds a tool</b>.",
        price_line="<b>$1.50 per 1,000 websites</b>; a weekly watch on 500 prospects where 20 change is <b>about $0.13 a month</b> after the first run. Apify's free plan gives you $5 of credit every month.",
        sample_title="A real sample report",
        sample=lambda: (
            "<p>Real row from our run on 24 November 2026 on <b>allbirds.com</b>.</p>"
            + table(["What", "Found on allbirds.com"], [
                ["Ecommerce", "Shopify"],
                ["Payments", "Apple Pay, PayPal"],
                ["Tag manager", "Google Tag Manager"],
                ["CDN and security", "Cloudflare, HSTS, HTTP/3"],
                ["Email provider (from DNS)", "Microsoft 365"],
                ["Other tools (from DNS records)", "DocuSign, Miro, Cursor"],
                ["Social links", "Facebook, Instagram, X, YouTube, TikTok, Pinterest"],
            ])
            + "<p>15 technologies in total. The tools a company verifies in its DNS (DocuSign, Miro, Cursor here) are often the best hint of what software it already buys.</p>"
            + '<p class="sources">Source: Apify run G0g9p5S8dq8Hpj7yn, dataset kSnEvKBXXlnOWsr2I, 24 Nov 2026.</p>'
        ),
        alert_title="What each run tells you",
        alert=[
            "<b>CMS and ecommerce</b> (WordPress, Shopify, Webflow, WooCommerce...), <b>analytics and ad pixels</b>, <b>payments</b>, <b>live chat</b>, <b>CRM and marketing tools</b>.",
            "<b>Hosting, CDN and email provider</b> from the site and its DNS records.",
            "<b>Social links</b> (LinkedIn, Facebook, Instagram, X, YouTube, TikTok) in the same row.",
            "With monitoring on: <b>only sites that changed</b>, with the technologies added and removed.",
            "Evidence for each detection, so you can trust a lead list before you send it.",
        ],
        steps=[
            "<b>Open the ready-made task.</b> Click <b>Set it up in 3 minutes</b>, create a free Apify account (no card), paste your list of websites, one per line, and click <b>Save &amp; Start</b>. Export the result to Excel or CSV from the run's <b>Overview</b> tab.",
            "<b>Optional: watch them every week.</b> In Apify's left menu click <b>Schedules</b>, then <b>Create new</b>. Choose <b>Weekly</b>, click <b>Add</b> &gt; <b>Task</b> and pick your task, then <b>Save</b> and <b>Enable</b>. Later runs return only sites that changed. Apify's guide: <a href=\"https://docs.apify.com/platform/schedules\">Schedules</a>.",
            "<b>Get it in Slack or Google Drive.</b> On the task, open <b>Integrations</b> and add <a href=\"https://docs.apify.com/platform/integrations/slack\" rel=\"noopener\">Slack</a> or <a href=\"https://docs.apify.com/platform/integrations/drive\" rel=\"noopener\">Google Drive</a>.",
        ],
        costs=[
            ["Site with at least one technology found", "$1.50 per 1,000 ($0.0015 each)"],
            ["Unreachable or blocked sites, unchanged sites in monitoring", "Free"],
            ["Example: a lead list of 2,000 websites", "<b>$3 once</b>"],
            ["Example: weekly watch on 500 prospects, 20 change a week", "<b>about $0.13 a month</b>"],
        ],
        offer_what="your list of websites (up to 20)",
        compare=table(["", "Pandapi tech lookup", "BuiltWith", "Other Apify tech detectors"], [
            ["Price", "<b>$1.50 per 1,000 sites</b>, no subscription", "single lookups free; lists from $295 a month", "$2 to $10 per 1,000"],
            ["Your own list of sites in bulk", "✅", "✅ paid", "✅"],
            ["Alert when a site changes stack", "✅", "✅ paid", "❌"],
            ["Social links and email provider in the same row", "✅", "❌", "❌"],
            ["Find every site using a technology", "❌ (bring your list)", "✅", "❌"],
            ["Years of history", "❌", "✅", "❌"],
        ]) + '<p>BuiltWith is the better pick if you need it to find every site that uses a technology, or years of history. If you already have a list of prospects and want to know what they run, and when that changes, this costs a few dollars at most.</p><p class="sources">BuiltWith plans $295, $495 and $995 a month (builtwith.com/plans, checked 26 November 2026). Apify prices from each actor\'s Store page, 21 November 2026.</p>',
        learn=[
            (APIFY + "website-tech-stack-detector", "Full guide and all options on Apify (confidence, evidence, contacts)"),
        ],
        faq=[
            ("How does it know what a site is built with?", "It reads the site's home page, scripts, headers and cookies and its DNS records, and matches them against 7,700 known technologies."),
            ("How much does it cost?", "$1.50 per 1,000 sites where something is found; unreachable sites are free. A 2,000-site list costs $3, and a weekly watch on 500 prospects is about $0.13 a month."),
            ("Can it find all websites using Shopify?", "No. You bring the list of websites (from your CRM, a directory or a search) and it tells you what each one runs."),
            ("Can I see when a prospect changes platform?", "Yes. Turn on monitoring and schedule it weekly: later runs return only the sites that changed, with what was added and removed."),
            ("Do I need to know how to code?", "No. You open the ready-made task, paste websites, click Start, and download the result as Excel or CSV."),
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
             + (f' <a class="btn secondary" href="https://console.apify.com/create-task-from-example/{p["alt_setup"][1]}" rel="nofollow">{E(p["alt_setup"][0])}</a>' if p.get("alt_setup") else '')
             + f'<span class="setup-note">Opens a ready-made Apify task with the example filled in. Free account, no card. '
             + f'<a href="{task_url(p)}">See the task first</a>.</span></div>')
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
{__import__('sample_pages').links_for(slug)}
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
<p class="byline">Updated {p.get("updated", (UPDATED, UPDATED_TEXT))[1]} · by the Pandapi team</p>
</div></main>
""")
    out.append(foot("../"))
    return "".join(out)


def tile(p, depth="../"):
    return (f'<a class="card tile" href="{depth}{p["slug"]}/"><img src="{depth}assets/icons/api/{p["actor"]}.png" alt="" width="56" height="56" loading="lazy">'
            f'<div><h3>{E(p["h1"].split(":")[0])}</h3><p>{E(p["meta"].split(". ")[0])}.</p></div></a>')
