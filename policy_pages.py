"""Policy and trust pages for the Pandapi Tools site (2026-11-25).

Plain-language pages for non-technical buyers: privacy, terms, billing and refunds, cookies,
report emails (how they work and how to stop them) and contact/about. Rendered by build.py as
`<slug>/index.html`, linked from every page's footer (build.foot) and listed in sitemap.xml.
`privacy.html` (the old address) becomes a redirect to `privacy/`.

Facts used here, keep them true when anything changes:
- Free tools run in the browser; no cookies, no localStorage, no analytics, no third-party scripts (CSP connect-src 'self').
- Host: GitHub Pages. Google Search Console gives us search totals only.
- Paid APIs are Apify Actors under blueberry_rainstorm; Apify bills, stores runs and handles refunds.
  Apify Store terms 9.4: a price increase takes effect 14 days after it's set, at most once a month.
- Report emails: "Email me the report at" on the price monitor and tender alerts; sent by Apify's own
  Send Email actor (apify/send-mail) in the customer's account, only to the account's own address;
  footer says how to stop (apify-actors/storeproducts/src/email.js, tenders/src/email.js).
"""
import html

E = html.escape
UPDATED = "2026-11-25"
UPDATED_TEXT = "25 November 2026"
APIFY_PROFILE = "https://apify.com/blueberry_rainstorm"
EXAMPLES_ISSUES = "https://github.com/rabroubx-coder/pandapi-examples/issues"
X_PROFILE = "https://x.com/PandapiDev"
APIFY_PRIVACY = "https://docs.apify.com/legal/privacy-policy"
APIFY_TERMS = "https://docs.apify.com/legal/general-terms-and-conditions"
APIFY_ACTOR_CONTRACT = "https://docs.apify.com/legal/standard-actor-contract"
GITHUB_PRIVACY = "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"
RAPIDAPI_TERMS = "https://rapidapi.com/terms"


def a(url, label):
    return f'<a href="{url}">{label}</a>'


PAGES = [
    dict(
        slug="privacy",
        short="Privacy",
        title="Privacy policy · Pandapi Tools",
        h1="Privacy policy",
        meta="What Pandapi collects (almost nothing), what the free tools do with your files (nothing leaves your device) and how our paid APIs on Apify handle your data.",
        body=f"""
<div class="card"><p><b>The short version.</b> The free tools on this site run in your browser, so your files and text never leave your device. We use no cookies, no analytics and no ads. Our paid APIs run inside your own Apify account, and Apify does not give us your inputs or results. We don't sell or share personal data, and we don't send marketing emails.</p></div>

<h2>Who we are</h2>
<p>Pandapi is a small independent developer brand. We make the free tools on this site and a set of paid data APIs published on Apify under {a(APIFY_PROFILE, "apify.com/blueberry_rainstorm")}. In this policy "we" and "us" means Pandapi. See {a("../contact/", "Contact and about")} for how to reach us.</p>

<h2>The free tools on this website</h2>
<ul>
<li>Every tool (HTML to Markdown, PDF to Markdown, JSON to Excel and the rest) does its work with code running <b>in your browser</b>. The text you paste and the files you drop are processed on your device. They are never uploaded to us or to anyone else.</li>
<li>We don't ask for an account, a name or an email address.</li>
<li>The pages load no analytics, no ads, no tracking pixels and no third-party scripts. The site's security rules block pages from sending data to other servers.</li>
<li>We don't set cookies or save anything in your browser's storage. See the {a("../cookies/", "cookie notice")}.</li>
</ul>

<h2>What our web host sees</h2>
<p>This site is a set of static files hosted by GitHub Pages. Like every web host, GitHub receives your IP address and the page you asked for, and may keep it in its logs for security. GitHub does not share these logs with us. GitHub's own {a(GITHUB_PRIVACY, "privacy statement")} covers that data.</p>
<p>We use Google Search Console, which shows us totals such as how many people found a page through Google search and which search words they used. It doesn't tell us who you are.</p>

<h2>Links to other sites</h2>
<p>Links from this site to our APIs on Apify carry a short tag (for example <code>utm_source=pandapi-tools</code>) so that Apify's statistics can show which page sent a visitor. Once you are on another site, such as Apify, GitHub or X, that site's privacy policy applies.</p>

<h2>Our paid APIs on Apify</h2>
<ul>
<li>You run our APIs in <b>your own Apify account</b>. Apify handles your account, payment and the storage of your runs and results, under the {a(APIFY_PRIVACY, "Apify privacy policy")}. We never see your card or bank details.</li>
<li>Apify does not give us your inputs, results or logs. We see general numbers Apify shows to every API developer, such as how many runs and paid results our APIs had.</li>
<li>There are two exceptions, both in your hands. If you turn on <b>Share run data with developers</b> in your Apify settings, or put a run link in an issue you send us, Apify lets us open that run so we can help you.</li>
<li>Some APIs listed on RapidAPI work the same way: RapidAPI handles your account and keys, and requests pass through to Apify.</li>
</ul>

<h2>Personal data in the results you collect</h2>
<p>Some of our APIs return public information that can include personal data, for example business email addresses found on a website, or reviewer names in app reviews. When you collect that data, you decide what to do with it, so you are responsible for using it lawfully. That includes data protection laws such as the GDPR and anti-spam laws such as CAN-SPAM. Please read our {a("../terms/", "terms")} before collecting personal data.</p>

<h2>When you contact us</h2>
<p>If you write to us through an Apify issue, a GitHub issue or a message on X, we use what you send only to answer you and to fix the problem. <b>GitHub issues are public</b>, so don't put private details in them. We keep messages only as long as needed to help you, and we don't add you to any list.</p>

<h2>Report emails</h2>
<p>Two of our APIs can email you a short report after each run. Those emails are sent by Apify, inside your account, only to your own Apify account address. We don't receive or store your email address. See {a("../report-emails/", "Report emails")} for how they work and how to stop them.</p>

<h2>Children</h2>
<p>This site and our APIs are made for adults at work. They are not aimed at children under 16.</p>

<h2>Your choices and rights</h2>
<p>We hold almost no personal data about you. If you want to know what we have, or want it deleted, {a("../contact/", "contact us")} and we'll answer. For data in your Apify account (your profile, runs, results and invoices), Apify is the right place to ask, and you can delete runs and results yourself in Apify Console.</p>

<h2>Changes to this policy</h2>
<p>If we change how we handle data, we'll update this page and the date at the top.</p>
""",
    ),
    dict(
        slug="terms",
        short="Terms",
        title="Terms of service · Pandapi Tools",
        h1="Terms of service",
        meta="The plain-language rules for using Pandapi's free browser tools and paid data APIs: fair use, your data, no warranty, and how Apify's terms apply.",
        body=f"""
<div class="card"><p><b>The short version.</b> The free tools are free to use for anything, including work. Check the results before you rely on them. Use our APIs lawfully and don't use them to spam people or harm websites. Paid APIs are sold through Apify, so Apify's terms apply too.</p></div>

<h2>What these terms cover</h2>
<p>These terms cover this website, its free tools, and Pandapi's paid data APIs (on Apify, and some on RapidAPI). By using them you agree to these terms. If you don't agree, please don't use them.</p>

<h2>Paid APIs are also covered by Apify's terms</h2>
<p>When you run our APIs on Apify, Apify's {a(APIFY_TERMS, "General Terms and Conditions")} and its {a(APIFY_ACTOR_CONTRACT, "Standard Actor Contract")} (the standard agreement between you and an API developer on Apify) also apply. On RapidAPI, the {a(RAPIDAPI_TERMS, "RapidAPI terms")} apply too. If those terms and this page disagree about payment or your Apify account, the platform's terms win.</p>

<h2>The free tools</h2>
<ul>
<li>You can use them free of charge, for personal or business work, with no account and no usage limit.</li>
<li>Conversions are done by software and can miss things: a table split across pages, a scanned PDF with no text, an unusual file. Check the result before you send, publish or rely on it.</li>
<li>We may change, improve or remove a tool at any time.</li>
</ul>

<h2>Use our tools and APIs fairly</h2>
<p>You agree not to use them to:</p>
<ul>
<li>break any law, including data protection, privacy, copyright and anti-spam laws;</li>
<li>send spam, or contact people whose data you collected without a lawful reason to do so;</li>
<li>collect data behind a login or paywall you aren't allowed to access, or get around a site's security;</li>
<li>overload or disrupt a website, for example by sending far more requests than a person would;</li>
<li>harass, track or build profiles of private individuals.</li>
</ul>
<p>Respect the terms of the websites you collect data from. You are responsible for the data you collect and how you use it.</p>

<h2>Your content and results</h2>
<p>What you put in, and the results you get out, are yours. We don't claim any rights over them. For the free tools we never even see them.</p>

<h2>Our content</h2>
<p>The site's text, design, icons and code belong to Pandapi. The tools include open-source libraries, which keep their own licences. You may link to any page and quote short parts with a link back.</p>

<h2>Prices and payment</h2>
<p>Each paid API shows its price on its Apify page. Apify charges you and handles invoices and refunds. See {a("../refunds/", "Billing and refunds")}.</p>

<h2>No guarantee</h2>
<p>We work hard to keep the tools and APIs accurate and running, but we provide them "as is". We can't promise they will always be available, error-free, or right for your purpose. Websites change, and an API may stop working for a while until we fix it.</p>

<h2>Limits on our responsibility</h2>
<p>As far as the law allows, we are not responsible for indirect losses, such as lost profits, lost data or lost business, that come from using or not being able to use the tools or APIs. For the paid APIs, our total responsibility is limited to what you paid for them in the 3 months before the problem. Nothing here limits rights you have under consumer law that can't be limited.</p>

<h2>Stopping use</h2>
<p>You can stop at any time: close the page, or switch off your Apify tasks and schedules. If someone breaks these terms, for example by using our APIs for spam, we may report it to Apify, which can block their access.</p>

<h2>Changes to these terms</h2>
<p>We may update these terms. The date at the top shows the latest version. If a change is important, we'll say so on the API pages as well.</p>

<h2>Questions</h2>
<p>See {a("../contact/", "Contact and about")}.</p>
""",
    ),
    dict(
        slug="refunds",
        short="Billing and refunds",
        title="Billing and refunds · Pandapi Tools",
        h1="Billing and refunds",
        meta="How you pay for Pandapi APIs (through Apify, per result), how to keep costs low, and how to get a refund if a run charged you for results it didn't deliver.",
        body=f"""
<div class="card"><p><b>The short version.</b> The tools on this site are free. Our paid APIs are billed by Apify, per result, with no subscription to us. Apify's free plan gives you $5 of credit every month. If a bug on our side charged you for bad results, tell us with the run link and we'll help you get your money back.</p></div>

<h2>The free tools</h2>
<p>Everything on this site is free. We never ask for payment details here.</p>

<h2>How paid APIs are billed</h2>
<ul>
<li>Our APIs run on Apify. <b>Apify takes the payment</b>, sends your invoices and keeps your card details. We never see them.</li>
<li>Most of our APIs are <b>pay per result</b>: you pay a small price per item you get (for example per review, per product or per page), plus Apify's small platform cost. The exact price is on each API's Apify page.</li>
<li>There is <b>no subscription to Pandapi</b>. You pay only for the runs you start or schedule.</li>
<li>Apify's free plan includes $5 of credit every month, with no card needed. Many of our alerts cost well under $1 a month, so they run free.</li>
</ul>

<h2>Keep costs under control</h2>
<ul>
<li>Try a small run first, with 1 to 3 items.</li>
<li>Set a <b>maximum cost per run</b> in the run options. Apify stops the run when it reaches that amount.</li>
<li>Set a monthly usage limit in your Apify billing settings.</li>
<li>Scheduled runs keep running until you switch the schedule off. Check your <b>Schedules</b> page if you no longer need them.</li>
</ul>

<h2>Price changes</h2>
<p>Under Apify's rules, a price increase can happen at most once a month and only takes effect 14 days after it's announced on the API's page. Price cuts apply right away.</p>

<h2>Refunds</h2>
<p>Because Apify takes the payment, refunds are made by Apify. Here's what to do:</p>
<ol>
<li><b>If a run charged you for results it didn't deliver</b> (empty, broken or clearly wrong because of a bug in our API), open an issue on the API's <b>Issues</b> tab in Apify, with the run link. We'll check the run, fix the bug, and confirm the problem so Apify can refund the charge.</li>
<li><b>For any other billing question</b> (a plan, an invoice, a payment that failed, a charge you don't recognise), contact Apify support from Apify Console. Apify's {a(APIFY_TERMS, "terms")} set the refund rules for your Apify plan.</li>
</ol>
<p>A run that worked as described but returned fewer results than you hoped (for example a store with only a few products) isn't a bug, so it usually isn't refunded. We're still happy to look at any case: just write to us.</p>

<h2>Cancelling</h2>
<p>There is nothing to cancel with us. To stop paying, switch off your schedules and stop starting runs. To change or cancel an Apify plan, use the Billing page in Apify Console.</p>

<h2>RapidAPI</h2>
<p>Some of our APIs are also listed on RapidAPI. If you use them there, RapidAPI's plans, billing and refund rules apply.</p>
""",
    ),
    dict(
        slug="cookies",
        short="Cookies",
        title="Cookie notice · Pandapi Tools",
        h1="Cookie notice",
        meta="Pandapi Tools sets no cookies, uses no analytics and stores nothing in your browser, which is why there is no cookie banner.",
        body=f"""
<div class="card"><p><b>This site uses no cookies.</b> That's why you don't see a cookie banner.</p></div>

<h2>What we don't use</h2>
<ul>
<li>No cookies of any kind, not even "necessary" ones.</li>
<li>No analytics (no Google Analytics or similar), no ads and no tracking pixels.</li>
<li>No browser storage: the tools don't save your files or settings in your browser.</li>
<li>No third-party scripts, fonts or embeds that could set cookies.</li>
</ul>

<h2>Other sites</h2>
<p>When you click a link to another site, such as Apify, GitHub or X, that site may use cookies under its own policy. For example, the {a(APIFY_PRIVACY, "Apify privacy policy")} explains Apify's cookies.</p>

<h2>If this changes</h2>
<p>If we ever add something that uses cookies, we'll update this page first, and ask for your consent where the law requires it.</p>
<p>More in our {a("../privacy/", "privacy policy")}.</p>
""",
    ),
    dict(
        slug="report-emails",
        short="Report emails",
        title="Report emails: how they work and how to stop them · Pandapi",
        h1="Report emails: how they work and how to stop them",
        meta="How Pandapi report emails work (sent by Apify to your own account address, only when something changed) and how to stop them in two clicks.",
        body=f"""
<div class="card"><p><b>The short version.</b> Report emails only go to the email address of your own Apify account, and only if you typed it into your task. To stop them, empty the <b>Email me the report at</b> field in your Apify task and click <b>Save</b>.</p></div>

<h2>Which emails are these?</h2>
<p>Two of our APIs can send a short report by email after each run:</p>
<ul>
<li><a href="../competitor-price-monitoring/">Competitor price alerts</a> (the Shopify &amp; WooCommerce price monitor): price drops and increases, stock changes, new and removed products.</li>
<li><a href="../government-tender-alerts/">Government tender alerts</a>: new tenders that match your words, with their deadlines.</li>
</ul>
<p>The email is plain text: a one-line headline, one line per change, and a link to the full results.</p>

<h2>Who sends them, and to whom</h2>
<ul>
<li>They're sent by <b>Apify's own Send Email tool, inside your Apify account</b>. We don't run an email service and we don't have a mailing list.</li>
<li>Apify only lets this tool send to <b>the email address of the account that runs it</b>. So the report can only reach you, the account owner. Nobody can use our APIs to send these emails to someone else.</li>
<li>We don't receive or store your email address.</li>
<li>By default, you only get an email when something changed. Days with no changes send nothing, unless you chose <b>After every run</b>.</li>
<li>Each email is a tiny run in your Apify account and costs well under a cent.</li>
</ul>

<h2>How to stop the emails</h2>
<ol>
<li>Sign in at <a href="https://console.apify.com">console.apify.com</a>.</li>
<li>In the left menu, click <b>Saved tasks</b> and open your task (for example "competitor-price-alerts").</li>
<li>Empty the <b>Email me the report at</b> field.</li>
<li>Click <b>Save</b>. The next runs won't send an email.</li>
</ol>
<p>Every report email ends with these same steps, so you always have them at hand.</p>

<h2>How to stop the runs too</h2>
<p>The emails come from runs that you scheduled. To stop everything, open <b>Schedules</b> in the Apify left menu and switch your schedule off, or delete it. No runs means no emails and no charges.</p>

<h2>Get emails less often, or only when it matters</h2>
<ul>
<li>Set <b>Send the email</b> to "only when something changed" (the default).</li>
<li>Change your schedule from daily to weekly in <b>Schedules</b>.</li>
</ul>

<h2>Other emails you might get</h2>
<p>Apify itself sends account emails, such as invoices, usage warnings and failed-run notices. Those come from Apify, not from us. You can choose which ones you get under <b>Settings</b>, <b>Notifications</b> in Apify Console.</p>

<h2>Got an email you didn't expect?</h2>
<p>If a report email reached you and you never set one up, someone with access to your Apify account added it. Follow the steps above to stop it, check who has access to your account, and {a("../contact/", "tell us")} if you need help.</p>
""",
    ),
    dict(
        slug="contact",
        short="Contact",
        title="Contact and about · Pandapi Tools",
        h1="Contact and about",
        meta="Who makes Pandapi Tools and the Pandapi data APIs, and the quickest way to get help, report a bug or ask for a free sample report.",
        body=f"""
<h2>About Pandapi</h2>
<p>Pandapi is a small independent developer brand. We build two things:</p>
<ul>
<li><b>Free tools that run in your browser</b>, on this site: converters for HTML, PDF, Word, Markdown, JSON, CSV and Excel, plus link and email extractors. No sign-up and no upload.</li>
<li><b>Data APIs and alerts</b> on Apify, at {a(APIFY_PROFILE, "apify.com/blueberry_rainstorm")}: competitor price alerts, government tender alerts, app review exports, website contact finder and more. You pay per result through Apify.</li>
</ul>
<p>We study the best-known tools for each job before building ours, and we publish honest comparisons in our <a href="../guides/">guides</a>, including when another tool is the better choice.</p>

<h2>How to reach us</h2>
<ul>
<li><b>A problem with one of our APIs:</b> open an issue on the API's <b>Issues</b> tab on Apify. Add the run link so we can see what happened. This is the fastest way.</li>
<li><b>Questions, ideas or a free sample report:</b> open an issue at {a(EXAMPLES_ISSUES, "github.com/rabroubx-coder/pandapi-examples")}. GitHub issues are public, so don't include private details.</li>
<li><b>A private message:</b> send a direct message to {a(X_PROFILE, "@PandapiDev on X")}.</li>
</ul>
<p>We read messages every day and aim to reply within 2 working days.</p>

<h2>Policies</h2>
<ul>
<li><a href="../privacy/">Privacy policy</a></li>
<li><a href="../terms/">Terms of service</a></li>
<li><a href="../refunds/">Billing and refunds</a></li>
<li><a href="../cookies/">Cookie notice</a></li>
<li><a href="../report-emails/">Report emails: how they work and how to stop them</a></li>
</ul>
""",
    ),
]

BY_SLUG = {p["slug"]: p for p in PAGES}
FOOTER = [(p["slug"], p["short"]) for p in PAGES]


def page_html(p, head, foot, site_url):
    path = p["slug"] + "/"
    others = " · ".join(f'<a href="../{q["slug"]}/">{E(q["short"])}</a>' for q in PAGES if q is not p)
    return (head(p["title"], p["meta"], path, "tool-html-to-markdown.png")
            + f"""<main><div class="wrap"><section class="content policy" style="margin-top:0">
<h1>{E(p['h1'])}</h1>
<p class="updated">Last updated {UPDATED_TEXT}</p>
{p['body']}
<p class="updated" style="margin-top:32px">Other policies: {others}</p>
</section></div></main>
""" + foot("../"))


def redirect_html(to, site_url):
    """Small page at an old address that sends visitors (and search engines) to the new one."""
    canon = f'<link rel="canonical" href="{site_url}/{to}">' if site_url else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moved · Pandapi Tools</title>
<meta name="robots" content="noindex">
{canon}
<meta http-equiv="refresh" content="0; url={to}">
</head>
<body>
<p>This page moved to <a href="{to}">{to}</a>.</p>
</body>
</html>
"""
