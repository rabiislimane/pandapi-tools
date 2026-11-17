# Pandapi Tools

Free tools that run in your browser. Nothing you convert is uploaded or stored.

**Live site: https://rabiislimane.github.io/pandapi-tools/**

| Tool | What it does |
|---|---|
| [HTML to Markdown](https://rabiislimane.github.io/pandapi-tools/html-to-markdown/) | Paste HTML or part of a web page and get clean GitHub-flavored Markdown. "Main content only" drops menus, footers and cookie banners. Batch files to a .zip. |
| [PDF to Markdown](https://rabiislimane.github.io/pandapi-tools/pdf-to-markdown/) | Turn PDFs into Markdown with headings, lists and tables, right in the browser. |
| [JSON to Excel](https://rabiislimane.github.io/pandapi-tools/json-to-excel/) | Flatten JSON (nested objects and arrays) into an .xlsx spreadsheet. |

Need the same thing at scale, through an API? See the [Pandapi data APIs on Apify](https://apify.com/blueberry_rainstorm).

## How it works

A static site with no build step at runtime and no server. Each tool lives in its own folder (`convert.js` holds the conversion, `app.js` the page logic). `build.py` regenerates the HTML pages so the header, footer and SEO tags stay identical:

```bash
SITE_URL=https://rabiislimane.github.io/pandapi-tools python3 build.py
```

Third-party libraries in `vendor/` keep their own licenses (see `vendor/LICENSES.md`). Everything else is MIT.
