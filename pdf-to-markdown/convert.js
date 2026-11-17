/* PDF to Markdown core. extractPages() uses pdf.js (browser or Node); pagesToMarkdown() is pure and unit-tested. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api; else root.PandapiPdf = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /** Read text items from a PDF with pdf.js. Returns { pages: [{ width, height, items: [{ str, x, y, size, w }] }], info }. */
  function extractPages(pdfjsLib, data, onProgress) {
    return pdfjsLib.getDocument({ data: data, isEvalSupported: false, disableFontFace: true }).promise.then(function (doc) {
      var pages = [], n = doc.numPages;
      var info = doc.getMetadata().then(function (m) { return (m && m.info) || {}; }, function () { return {}; });
      function next(i) {
        if (i > n) return info.then(function (inf) { return { pages: pages, info: inf, numPages: n }; });
        return doc.getPage(i).then(function (page) {
          var vp = page.getViewport({ scale: 1 });
          return page.getTextContent().then(function (tc) {
            var items = [];
            tc.items.forEach(function (it) {
              if (!it.str || !it.transform) return;
              var t = it.transform, size = Math.hypot(t[2], t[3]) || it.height || 0;
              if (!size) return;
              // Skip text that runs sideways relative to the page (margin stamps, watermarks).
              var sideways = Math.abs(t[1]) > Math.abs(t[0]) + 0.01;
              if (vp.rotation % 180 !== 0) sideways = !sideways;
              if (sideways) return;
              // Normalise to a top-left origin for rotated pages too.
              var pt = vp.convertToViewportPoint(t[4], t[5]);
              items.push({ str: it.str, x: pt[0], y: pt[1], size: Math.round(size * 10) / 10, w: it.width || 0 });
            });
            pages.push({ width: vp.width, height: vp.height, items: items });
            page.cleanup();
            if (onProgress) onProgress(i, n);
            return next(i + 1);
          });
        });
      }
      return next(1).then(function (r) { doc.destroy(); return r; });
    });
  }

  function median(a) { if (!a.length) return 0; var s = a.slice().sort(function (x, y) { return x - y; }); return s[Math.floor(s.length / 2)]; }

  /** Group a page's items into lines (top to bottom, left to right), splitting wide gaps into segments. */
  function pageLines(page) {
    var items = page.items.filter(function (i) { return i.str.trim() || i.str === ' '; }).slice()
      .sort(function (a, b) { return a.y - b.y || a.x - b.x; });
    var rows = [];
    items.forEach(function (it) {
      var row = null;
      for (var k = rows.length - 1; k >= 0 && k >= rows.length - 3; k--) {
        if (Math.abs(rows[k].y - it.y) <= Math.max(2, Math.min(rows[k].size, it.size) * 0.45)) { row = rows[k]; break; }
      }
      if (!row) { row = { y: it.y, size: it.size, items: [] }; rows.push(row); }
      row.items.push(it);
      row.size = Math.max(row.size, it.size);
    });
    var segs = [];
    rows.forEach(function (row) {
      row.items.sort(function (a, b) { return a.x - b.x; });
      var cur = null;
      row.items.forEach(function (it) {
        var gap = cur ? it.x - cur.right : 0;
        if (!cur || gap > Math.max(row.size * 2.2, 18)) {
          cur = { y: row.y, x: it.x, right: it.x + it.w, size: it.size, text: it.str, sizes: {} };
          cur.sizes[it.size] = it.str.length;
          segs.push(cur);
          return;
        }
        cur.sizes[it.size] = (cur.sizes[it.size] || 0) + it.str.length;
        var needSpace = gap > row.size * 0.12 && !/\s$/.test(cur.text) && !/^\s/.test(it.str);
        cur.text += (needSpace ? ' ' : '') + it.str;
        cur.right = Math.max(cur.right, it.x + it.w);
      });
    });
    segs.forEach(function (s) {
      s.text = s.text.replace(/\s+/g, ' ').trim();
      // The size that covers most characters (a bold lead-in or a big first letter doesn't make the line a heading).
      var best = -1; Object.keys(s.sizes).forEach(function (z) { if (s.sizes[z] > best) { best = s.sizes[z]; s.size = +z; } });
      delete s.sizes;
    });
    segs = segs.filter(function (s) { return s.text; });
    // Two-column pages: many long text segments starting past the middle, left ones ending before it.
    var mid = page.width * 0.45;
    var right = segs.filter(function (s) { return s.x > mid; });
    var left = segs.filter(function (s) { return s.x <= mid; });
    var twoCol = right.length >= 8 && left.length >= 8 &&
      median(right.map(function (s) { return s.text.length; })) > 25 &&
      left.filter(function (s) { return s.right > mid + 10; }).length < left.length * 0.15;
    if (twoCol) {
      var colX = Math.min.apply(null, right.map(function (s) { return s.x; }));
      segs.forEach(function (s) { s.col = s.x >= colX - 2 ? 1 : 0; });
      segs.sort(function (a, b) { var ca = a.x >= colX - 2 ? 1 : 0, cb = b.x >= colX - 2 ? 1 : 0; return ca - cb || a.y - b.y || a.x - b.x; });
    } else {
      // Join segments of one row back into one line (tables, tab stops) with a wide separator.
      var merged = [];
      segs.forEach(function (s) {
        var last = merged[merged.length - 1];
        if (last && Math.abs(last.y - s.y) < 0.5) { last.text += '   ' + s.text; last.right = s.right; last.size = Math.max(last.size, s.size); last.cells = (last.cells || 1) + 1; }
        else merged.push(Object.assign({}, s));
      });
      segs = merged;
    }
    return { lines: segs, twoCol: twoCol, height: page.height };
  }

  function normalizeForRepeat(t) { return t.toLowerCase().replace(/\d+/g, '#').replace(/\s+/g, ' ').trim(); }
  var PAGE_NUM = /^(page\s*)?#(\s*(of|\/)\s*#)?$|^[-–—]\s*#\s*[-–—]$|^#\s*\/\s*#$/i;

  /**
   * pagesToMarkdown(pages, opts) -> { markdown, stats }
   * opts: { pageMarkers: false, keepHeadersFooters: false }
   */
  function pagesToMarkdown(pages, opts) {
    opts = opts || {};
    var laid = pages.map(pageLines);
    // Body font size = the size that covers the most characters.
    var bySize = {};
    laid.forEach(function (p) { p.lines.forEach(function (l) { bySize[l.size] = (bySize[l.size] || 0) + l.text.length; }); });
    var body = 0, best = -1;
    Object.keys(bySize).forEach(function (s) { if (bySize[s] > best) { best = bySize[s]; body = +s; } });
    if (!body) body = 10;

    // Repeated headers and footers (top/bottom 9% of the page, on at least half the pages, min 3 pages) and page numbers.
    var removed = 0;
    if (!opts.keepHeadersFooters) {
      var counts = {};
      laid.forEach(function (p) {
        var seen = {};
        p.lines.forEach(function (l) {
          if (l.y < p.height * 0.09 || l.y > p.height * 0.91) { var k = normalizeForRepeat(l.text); if (!seen[k]) { seen[k] = 1; counts[k] = (counts[k] || 0) + 1; } }
        });
      });
      var minPages = Math.max(2, Math.ceil(laid.length * 0.5));
      laid.forEach(function (p) {
        p.lines = p.lines.filter(function (l) {
          var edge = l.y < p.height * 0.09 || l.y > p.height * 0.91;
          if (!edge) return true;
          var k = normalizeForRepeat(l.text);
          if ((laid.length >= 2 && counts[k] >= minPages) || PAGE_NUM.test(k)) { removed++; return false; }
          return true;
        });
      });
    }

    // Heading levels from the distinct sizes that are clearly larger than body text.
    // A heading size is clearly bigger than body text and rare (headings are short); at most 4 levels.
    var headSizes = Object.keys(bySize).map(Number).filter(function (s) { return s >= body * 1.18 && bySize[s] < bySize[body] * 0.25; })
      .sort(function (a, b) { return b - a; }).slice(0, 4);
    function headingLevel(size) { var i = headSizes.indexOf(size); return i < 0 ? 0 : i + 1; }
    var LEADERS = /^(.*?\S)\s*(?:\.\s?){3,}\s*(\d+|[ivxlc]+)$/i;
    // If the biggest size is used a lot (a styled body), don't treat it as headings.
    var out = [], kinds = [], para = null, headings = 0, listItems = 0;
    function push(t, kind) { out.push(t); kinds.push(kind || 'p'); }
    function flush() { if (para) { push(para.text, para.list ? 'li' : 'p'); para = null; } }
    var BULLET = /^([•◦▪▫●○■□►▶‣⁃∙·\-\*–])\s+(.*)$/;
    var NUMBERED = /^(\(?(\d{1,3}|[a-z])[.)])\s+(.*)$/i;

    laid.forEach(function (p, pi) {
      if (opts.pageMarkers) { flush(); push('<!-- page ' + (pi + 1) + ' -->', 'marker'); }
      var fullRight = [0, 1].map(function (c) {
        var rights = p.lines.filter(function (l) { return l.size === body && (l.col || 0) === c; }).map(function (l) { return l.right; }).sort(function (a, b) { return a - b; });
        return rights.length ? rights[Math.floor(rights.length * 0.9)] : p.width;
      });
      var prev = null;
      p.lines.forEach(function (l) {
        var text = l.text;
        var lead = LEADERS.exec(text);
        if (lead) {
          // A contents entry; if it wraps, the leaders sit on the last line, so join it to the open list item.
          if (para && para.list && prev && l.y - prev.y < l.size * 1.75) { para.text += ' ' + lead[1] + ' (p. ' + lead[2] + ')'; flush(); }
          else { flush(); push('- ' + lead[1] + ' (p. ' + lead[2] + ')', 'li'); }
          prev = { y: l.y, size: l.size, x: l.x, row: true }; return;
        }
        var level = headingLevel(l.size);
        if (level && text.length <= 120 && !/[,;]$/.test(text)) {
          // Multi-line headings of the same size are joined.
          var lastOut = out[out.length - 1];
          if (!para && prev && prev.heading === level && lastOut && /^#+ /.test(lastOut) && l.y - prev.y < l.size * 1.8) {
            out[out.length - 1] = lastOut + ' ' + text;
          } else { flush(); push(new Array(level + 1).join('#') + ' ' + text, 'h'); headings++; }
          prev = { y: l.y, heading: level, size: l.size, x: l.x }; return;
        }
        var b = BULLET.exec(text), n = !b && NUMBERED.exec(text);
        if (b || n) {
          flush(); listItems++;
          para = { text: b ? '- ' + b[2] : n[1].replace(/^\(/, '').replace(/\)$/, '.').replace(/\)/, '.') + ' ' + n[3], list: true, x: l.x };
          prev = { y: l.y, size: l.size, x: l.x }; return;
        }
        if (l.cells && l.cells >= 2) {
          // Row of a table or tab-aligned text: keep it on its own line.
          flush(); push(text.replace(/ {3,}/g, ' | '), 'row'); prev = { y: l.y, size: l.size, x: l.x, row: true }; return;
        }
        var gap = prev ? l.y - prev.y : 0;
        var continues = para && prev && !prev.heading && !prev.row && gap > 0 && gap < l.size * 1.75 &&
          (para.list ? l.x > para.x + 2 : Math.abs(l.x - prev.x) < l.size * 3) &&
          !(prev.right < fullRight[prev.col || 0] * 0.8 && /[.!?:]$/.test(prev.text || ''));
        if (continues) {
          if (/[A-Za-zÀ-ÿ]-$/.test(para.text) && /^[a-zà-ÿ]/.test(text)) para.text = /^[^\s]*-/.test(text) ? para.text + text : para.text.slice(0, -1) + text;
          else para.text += ' ' + text;
        } else {
          flush();
          para = { text: text.replace(/^([#>+])/, '\\$1'), list: false, x: l.x };
        }
        prev = { y: l.y, size: l.size, x: l.x, right: l.right, text: text, col: l.col };
      });
      flush();
    });
    flush();
    var md = out.map(function (t, i) { return (i === 0 ? '' : ((kinds[i] === 'li' && kinds[i - 1] === 'li') || (kinds[i] === 'row' && kinds[i - 1] === 'row') ? '\n' : '\n\n')) + t; }).join('').replace(/\n{3,}/g, '\n\n').trim() + '\n';
    var chars = laid.reduce(function (n, p) { return n + p.lines.reduce(function (m, l) { return m + l.text.length; }, 0); }, 0);
    return {
      markdown: md,
      stats: { pages: pages.length, headings: headings, listItems: listItems, removedLines: removed, bodySize: body,
        chars: chars, likelyScanned: pages.length > 0 && chars / pages.length < 25 }
    };
  }

  return { extractPages: extractPages, pagesToMarkdown: pagesToMarkdown, pageLines: pageLines };
});
