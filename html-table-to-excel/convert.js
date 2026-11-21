/* HTML table to Excel / CSV core. Needs a DOM (browser DOMParser); exposes window.PandapiTables.
   Uses PandapiJson (../json-to-excel/convert.js) for CSV and the .xlsx sheet writer. */
(function (root) {
  'use strict';

  var FOOTNOTE_RE = /\[(?:\d{1,3}|[a-z]|[ivx]{1,4}|note \d+|citation needed|nb \d+)\]/gi;

  function clean(s) { return String(s).replace(/[   ]/g, ' ').replace(/[ \t\r\f\v]+/g, ' ').replace(/ ?\n ?/g, '\n').replace(/\n{2,}/g, '\n').trim(); }

  /** Visible text of a cell. opts: { footnotes: 'remove'|'keep', lineBreaks: 'space'|'keep' } */
  function cellText(td, opts) {
    var c = td.cloneNode(true);
    c.querySelectorAll('script, style, noscript, template, [hidden], [aria-hidden="true"], .sortkey, .mw-ref, .reference, .noprint').forEach(function (n) {
      // aria-hidden and .sortkey hold sort keys on Wikipedia; .reference are footnote links.
      if (n.matches('.reference, .mw-ref') && opts.footnotes === 'keep') return;
      n.remove();
    });
    c.querySelectorAll('[style]').forEach(function (n) { if (/display\s*:\s*none/i.test(n.getAttribute('style'))) n.remove(); });
    c.querySelectorAll('br').forEach(function (br) { br.replaceWith('\n'); });
    c.querySelectorAll('p, div, li, tr').forEach(function (b) { b.append('\n'); });
    c.querySelectorAll('img').forEach(function (img) { var alt = img.getAttribute('alt'); if (alt && !c.textContent.trim()) img.replaceWith(alt); });
    var t = clean(c.textContent);
    if (opts.footnotes !== 'keep') t = clean(t.replace(FOOTNOTE_RE, ''));
    if (opts.lineBreaks !== 'keep') t = t.replace(/\n/g, ' ');
    return t;
  }

  function firstLink(td) {
    var a = td.querySelector('a[href]');
    if (!a) return '';
    var h = a.getAttribute('href').trim();
    if (!h || /^(#|javascript:|mailto:$)/i.test(h)) return '';
    return h;
  }

  /** Expand one <table> into a full grid (rowspan/colspan filled). Returns { cells: [[text]], links: [[href]], headRows, sections }. */
  function toGrid(table, opts) {
    var rows = Array.prototype.slice.call(table.rows); // only this table's rows, not nested tables
    var grid = [], links = [], spans = [];             // spans[c] = { left, text, link } carried down by rowspan
    var headRows = 0, stillHead = true;
    var fill = opts.mergedCells !== 'blank';
    rows.forEach(function (tr, r) {
      var line = [], lline = [], c = 0;
      function carry() {
        while (spans[c] && spans[c].left > 0) {
          line[c] = fill ? spans[c].text : ''; lline[c] = fill ? spans[c].link : '';
          spans[c].left--; c++;
        }
      }
      var cells = Array.prototype.slice.call(tr.cells);
      cells.forEach(function (td) {
        carry();
        var cs = Math.max(1, Math.min(1000, parseInt(td.getAttribute('colspan'), 10) || 1));
        var rsAttr = parseInt(td.getAttribute('rowspan'), 10);
        var rs = rsAttr === 0 ? rows.length - r : Math.max(1, Math.min(65534, rsAttr || 1));
        var text = cellText(td, opts), link = firstLink(td);
        for (var k = 0; k < cs; k++) {
          line[c + k] = k === 0 || fill ? text : '';
          lline[c + k] = k === 0 || fill ? link : '';
          if (rs > 1) spans[c + k] = { left: rs - 1, text: text, link: link };
        }
        c += cs;
      });
      carry();
      // Carry any remaining spans to the right of the last cell.
      for (var j = c; j < spans.length; j++) if (spans[j] && spans[j].left > 0) { line[j] = fill ? spans[j].text : ''; lline[j] = fill ? spans[j].link : ''; spans[j].left--; }
      var isHead = cells.length > 0 && (tr.parentNode && tr.parentNode.nodeName === 'THEAD' || cells.every(function (td) { return td.nodeName === 'TH'; }));
      if (stillHead && isHead) headRows++; else stillHead = false;
      grid.push(line); links.push(lline);
    });
    var width = grid.reduce(function (m, l) { return Math.max(m, l.length); }, 0);
    grid.forEach(function (l, i) { for (var x = 0; x < width; x++) { if (l[x] == null) l[x] = ''; if (links[i][x] == null) links[i][x] = ''; } });
    // Drop rows that are completely empty (spacer rows).
    var keep = grid.map(function (l) { return l.some(function (v) { return v !== ''; }); });
    var g2 = [], l2 = [], head2 = 0;
    grid.forEach(function (l, i) { if (keep[i]) { g2.push(l); l2.push(links[i]); if (i < headRows) head2++; } });
    return { cells: g2, links: l2, headRows: head2, width: width };
  }

  function tableName(table, i) {
    var cap = table.querySelector(':scope > caption');
    if (cap && cap.textContent.trim()) return clean(cap.textContent.replace(FOOTNOTE_RE, '')).slice(0, 80);
    // Nearest heading before the table in document order.
    var heads = table.ownerDocument.querySelectorAll('h1, h2, h3, h4, h5, h6');
    var best = null;
    for (var k = 0; k < heads.length; k++) {
      if (heads[k].compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING) best = heads[k]; else break;
    }
    var label = table.getAttribute('aria-label') || table.getAttribute('summary') || table.getAttribute('title');
    if (label) return clean(label).slice(0, 80);
    if (best && best.textContent.trim()) return clean(best.textContent.replace(/\[edit\]/gi, '').replace(FOOTNOTE_RE, '')).slice(0, 80);
    return 'Table ' + (i + 1);
  }

  function uniqueNames(names) {
    var seen = {};
    return names.map(function (n, i) {
      var base = n || ('Column ' + (i + 1)), name = base, k = 2;
      while (seen[name.toLowerCase()]) name = base + ' (' + (k++) + ')';
      seen[name.toLowerCase()] = true;
      return name;
    });
  }

  /** Header names from the top header rows; stacked header rows become "Group / Sub". */
  function headerNames(cells, n) {
    var width = cells.length ? cells[0].length : 0, out = [];
    for (var c = 0; c < width; c++) {
      var parts = [];
      for (var r = 0; r < n; r++) { var v = cells[r][c]; if (v && parts[parts.length - 1] !== v) parts.push(v); }
      out.push(parts.join(' / '));
    }
    return out;
  }

  function looksLikeHeader(row, next) {
    if (!row || !next) return false;
    var textCells = row.filter(function (v) { return v !== ''; });
    if (!textCells.length) return false;
    var numeric = function (v) { return /^[-+−(]?[$€£¥]?\s?[\d.,\s]+%?\)?$/.test(v) && /\d/.test(v); };
    return textCells.every(function (v) { return !numeric(v); }) && next.some(numeric);
  }

  /**
   * Number clean-up so Excel gets real numbers: "1,234.5" -> "1234.5", "(1,234)" -> "-1234", "−5" -> "-5",
   * optional currency and % stripping. IDs with leading zeros stay text (PandapiJson.looksNumeric decides later).
   */
  function normalizeNumber(v, opts) {
    var s = String(v).trim();
    if (!s || !/\d/.test(s) || s.length > 40) return v;
    var t = s.replace(/[−‒–]/g, '-');
    var neg = false;
    if (/^\(.*\)$/.test(t)) { neg = true; t = t.slice(1, -1).trim(); }
    if (opts.stripSymbols) {
      t = t.replace(/^([-+]?)\s*(?:[$€£¥₹]|US\$|CA\$|A\$|USD|EUR|GBP|CAD)\s?/i, '$1').replace(/\s?(?:[$€£¥₹%]|USD|EUR|GBP|CAD)$/i, '');
    }
    if (/^[-+]?\d{1,3}(,\d{3})+(\.\d+)?$/.test(t)) t = t.replace(/,/g, '');
    else if (/^[-+]?\d{1,3}([   ]\d{3})+(\.\d+)?$/.test(t)) t = t.replace(/[   ]/g, '');
    t = t.replace(/^\+/, '');
    if (!/^-?\d+(\.\d+)?$/.test(t)) return v;
    if (neg) t = t[0] === '-' ? t.slice(1) : '-' + t;
    return t;
  }

  /**
   * Find every table in an HTML string.
   * opts: { footnotes, lineBreaks, mergedCells: 'repeat'|'blank', header: 'auto'|'yes'|'no', numbers: true, stripSymbols, links: false }
   * Returns [{ index, name, rows: [obj], columns: [name], rowCount, colCount, small }]
   */
  function extract(html, opts) {
    opts = opts || {};
    var doc = new DOMParser().parseFromString(String(html || ''), 'text/html');
    var tables = Array.prototype.slice.call(doc.querySelectorAll('table'));
    var out = [];
    tables.forEach(function (table, i) {
      var g = toGrid(table, opts);
      if (!g.cells.length || !g.width) return;
      var cells = g.cells, links = g.links, nHead = g.headRows;
      if (opts.header === 'no') nHead = 0;
      else if (opts.header === 'yes') nHead = Math.max(1, nHead);
      else if (!nHead && looksLikeHeader(cells[0], cells[1])) nHead = 1;
      if (nHead >= cells.length) nHead = cells.length > 1 ? 1 : 0;
      var names = nHead ? headerNames(cells, nHead) : cells[0].map(function (_, c) { return 'Column ' + (c + 1); });
      var body = cells.slice(nHead), bodyLinks = links.slice(nHead);
      // Optional link columns: one "<name> link" column after each column that has links.
      var linkCols = [];
      if (opts.links) for (var c = 0; c < g.width; c++) if (bodyLinks.some(function (l) { return l[c]; })) linkCols.push(c);
      var colsRaw = [], src = [];
      for (var c2 = 0; c2 < g.width; c2++) {
        colsRaw.push(names[c2]); src.push({ c: c2, link: false });
        if (linkCols.indexOf(c2) >= 0) { colsRaw.push((names[c2] || 'Column ' + (c2 + 1)) + ' link'); src.push({ c: c2, link: true }); }
      }
      var columns = uniqueNames(colsRaw);
      var rows = body.map(function (line, r) {
        var o = {};
        src.forEach(function (s, k) {
          var v = s.link ? bodyLinks[r][s.c] : line[s.c];
          if (!s.link && opts.numbers !== false) v = normalizeNumber(v, opts);
          o[columns[k]] = v;
        });
        return o;
      });
      out.push({ index: i, name: tableName(table, i), rows: rows, columns: columns, rowCount: rows.length, colCount: columns.length,
        small: rows.length < 2 || g.width < 2, nested: !!table.parentElement && !!table.parentElement.closest('table') });
    });
    return out;
  }

  /** Multi-sheet .xlsx from several tables. Returns { files, droppedRows, droppedCols, truncatedCells }. */
  function workbook(tables, opts) {
    var J = root.PandapiJson, files = null, sheets = [], used = {}, stats = { droppedRows: 0, droppedCols: 0, truncatedCells: 0 };
    tables.forEach(function (t, i) {
      var base = String(t.name || 'Table ' + (i + 1)).replace(/[\\\/?*\[\]:]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 28) || 'Table ' + (i + 1);
      var name = base, k = 2;
      while (used[name.toLowerCase()]) name = base.slice(0, 26) + ' ' + (k++);
      used[name.toLowerCase()] = true;
      var p = J.xlsxParts(t.rows, t.columns, { numericText: opts.numbers !== false, sheetName: name });
      stats.droppedRows += p.droppedRows; stats.droppedCols += p.droppedCols; stats.truncatedCells += p.truncatedCells;
      if (!files) files = p.files;
      var wb = p.files['xl/workbook.xml'];
      sheets.push({ name: /<sheet name="([^"]*)"/.exec(wb)[1], xml: p.files['xl/worksheets/sheet1.xml'], filter: /<definedName[^>]*>([^<]*)<\/definedName>/.exec(wb) });
    });
    if (!files) return null;
    var ws = 'application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml';
    files['[Content_Types].xml'] = files['[Content_Types].xml'].replace(/<Override PartName="\/xl\/worksheets\/sheet1\.xml"[^>]*\/>/,
      sheets.map(function (_, i) { return '<Override PartName="/xl/worksheets/sheet' + (i + 1) + '.xml" ContentType="' + ws + '"/>'; }).join(''));
    files['xl/_rels/workbook.xml.rels'] = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
      sheets.map(function (_, i) { return '<Relationship Id="rId' + (i + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + (i + 1) + '.xml"/>'; }).join('') +
      '<Relationship Id="rId' + (sheets.length + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>';
    var defs = sheets.map(function (s, i) { return s.filter ? s.filter[0].replace(/localSheetId="\d+"/, 'localSheetId="' + i + '"') : ''; }).join('');
    files['xl/workbook.xml'] = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' +
      sheets.map(function (s, i) { return '<sheet name="' + s.name + '" sheetId="' + (i + 1) + '" r:id="rId' + (i + 1) + '"/>'; }).join('') + '</sheets>' +
      (defs ? '<definedNames>' + defs + '</definedNames>' : '') + '</workbook>';
    delete files['xl/worksheets/sheet1.xml'];
    sheets.forEach(function (s, i) { files['xl/worksheets/sheet' + (i + 1) + '.xml'] = s.xml; });
    stats.files = files;
    stats.sheetNames = sheets.map(function (s) { return s.name; });
    return stats;
  }

  /** Tab-separated text for pasting into Excel or Google Sheets. */
  function toTSV(t) {
    var esc = function (v) { v = v == null ? '' : String(v); return /[\t\n"]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    return [t.columns.map(esc).join('\t')].concat(t.rows.map(function (r) { return t.columns.map(function (c) { return esc(r[c]); }).join('\t'); })).join('\n') + '\n';
  }

  root.PandapiTables = { extract: extract, workbook: workbook, toTSV: toTSV, normalizeNumber: normalizeNumber, cellText: cellText };
})(typeof self !== 'undefined' ? self : this);
