/* CSV / TSV / Excel (.xlsx) to JSON core. Pure functions; works in the browser (window.PandapiCsvJson) and in Node (module.exports).
   Excel files are read with fflate's unzip (vendor/fflate.js) and a small XML reader, so no spreadsheet library is needed. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api; else root.PandapiCsvJson = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var DELIMS = [',', ';', '\t', '|'];

  /* ---------- Text decoding ---------- */

  /** Decode file bytes: UTF-8 (with or without BOM), UTF-16 with BOM, else Windows-1252 (old Excel CSV exports). */
  function decodeBytes(bytes) {
    if (bytes.length >= 2 && bytes[0] === 0xFF && bytes[1] === 0xFE) return { text: new TextDecoder('utf-16le').decode(bytes.subarray(2)), encoding: 'UTF-16' };
    if (bytes.length >= 2 && bytes[0] === 0xFE && bytes[1] === 0xFF) return { text: new TextDecoder('utf-16be').decode(bytes.subarray(2)), encoding: 'UTF-16' };
    try {
      var t = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
      return { text: t.replace(/^﻿/, ''), encoding: 'UTF-8' };
    } catch (e) {
      return { text: new TextDecoder('windows-1252').decode(bytes), encoding: 'Windows-1252' };
    }
  }

  /* ---------- CSV ---------- */

  /** Pick the delimiter that splits the first lines into the most consistent number of columns (quotes respected). */
  function detectDelimiter(text) {
    var sample = String(text).slice(0, 20000);
    var best = ',', bestScore = -1;
    DELIMS.forEach(function (d) {
      var rows = parseCSV(sample, { delimiter: d, maxRows: 30 }).rows;
      if (rows.length > 1 && sample.length >= 20000) rows.pop(); // last sampled row may be cut
      var counts = rows.filter(function (r) { return !(r.length === 1 && r[0] === ''); }).map(function (r) { return r.length; });
      if (!counts.length) return;
      var first = counts[0];
      if (first < 2) return;
      var same = counts.filter(function (c) { return c === first; }).length / counts.length;
      var score = same * 100 + Math.min(first, 50) + (d === '|' ? -5 : 0);
      if (score > bestScore) { bestScore = score; best = d; }
    });
    return best;
  }

  /** RFC 4180 parser: quoted fields, doubled quotes, separators and line breaks inside quotes, CRLF/LF/CR. */
  function parseCSV(text, opts) {
    opts = opts || {};
    text = String(text || '').replace(/^﻿/, '');
    var d = opts.delimiter && opts.delimiter !== 'auto' ? (opts.delimiter === 'tab' ? '\t' : opts.delimiter) : detectDelimiter(text);
    var maxRows = opts.maxRows || Infinity;
    var rows = [], row = [], field = '', i = 0, n = text.length, quoted = false, warnings = [];
    while (i < n) {
      var c = text[i];
      if (quoted) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i += 2; continue; }
          quoted = false; i++; continue;
        }
        field += c; i++; continue;
      }
      if (c === '"' && field === '') { quoted = true; i++; continue; }
      if (c === d) { row.push(field); field = ''; i++; continue; }
      if (c === '\r' || c === '\n') {
        row.push(field); rows.push(row); row = []; field = '';
        if (c === '\r' && text[i + 1] === '\n') i++;
        i++;
        if (rows.length >= maxRows) return { rows: rows, delimiter: d, warnings: warnings };
        continue;
      }
      field += c; i++;
    }
    if (quoted) warnings.push('A quoted field was never closed; the rest of the file was read as one value.');
    if (field !== '' || row.length) { row.push(field); rows.push(row); }
    return { rows: rows, delimiter: d, warnings: warnings };
  }

  /* ---------- XLSX ---------- */

  var ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };
  function xmlText(s) {
    return String(s)
      .replace(/&(#x[0-9a-fA-F]+|#\d+|amp|lt|gt|quot|apos);/g, function (m, e) {
        if (e[0] === '#') return String.fromCodePoint(e[1] === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
        return ENT[e];
      })
      .replace(/_x([0-9A-Fa-f]{4})_/g, function (m, h) { return String.fromCharCode(parseInt(h, 16)); });
  }
  function attr(tag, name) {
    var m = new RegExp('\\s' + name + '="([^"]*)"').exec(tag);
    return m ? xmlText(m[1]) : null;
  }
  // Text of every <t> in a string item, skipping phonetic runs (<rPh>).
  function siText(xml) {
    xml = xml.replace(/<(?:\w+:)?rPh\b[\s\S]*?<\/(?:\w+:)?rPh>/g, '');
    var out = '', re = /<(?:\w+:)?t\b[^>]*?(?:\/>|>([\s\S]*?)<\/(?:\w+:)?t>)/g, m;
    while ((m = re.exec(xml))) out += m[1] ? xmlText(m[1]) : '';
    return out;
  }

  var BUILTIN_DATE = {};
  [14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 45, 46, 47, 50, 51, 52, 53, 54, 55, 56, 57, 58].forEach(function (id) { BUILTIN_DATE[id] = true; });
  var BUILTIN_TIME = { 18: 1, 19: 1, 20: 1, 21: 1, 45: 1, 46: 1, 47: 1 };

  /** 'date', 'time', 'datetime' or null for a number format code. */
  function fmtKind(code) {
    var c = String(code).replace(/"[^"]*"/g, '').replace(/\\./g, '').replace(/\[(?!h\]|hh\]|m\]|mm\]|s\]|ss\])[^\]]*\]/gi, '').replace(/_.|\*./g, '');
    if (!/[dmyhs]/i.test(c) || /general/i.test(c)) return null;
    var hasDate = /[dy]/i.test(c) || (/m/i.test(c) && !/[hs]/i.test(c));
    var hasTime = /[hs]/i.test(c);
    return hasDate && hasTime ? 'datetime' : hasDate ? 'date' : 'time';
  }

  function pad(n, w) { n = String(n); while (n.length < (w || 2)) n = '0' + n; return n; }

  /** Excel serial number to ISO text. kind: date | time | datetime. */
  function serialToISO(serial, kind, date1904) {
    var v = Number(serial);
    if (!isFinite(v)) return serial;
    var days = date1904 ? v + 1462 : (v < 60 ? v + 1 : v);
    var ms = Math.round((days - 25569) * 86400000);
    var dt = new Date(ms);
    var date = dt.getUTCFullYear() + '-' + pad(dt.getUTCMonth() + 1) + '-' + pad(dt.getUTCDate());
    var secs = dt.getUTCSeconds() + (dt.getUTCMilliseconds() >= 500 ? 1 : 0);
    var time = pad(dt.getUTCHours()) + ':' + pad(dt.getUTCMinutes()) + ':' + pad(secs === 60 ? 59 : secs);
    if (kind === 'time' || (v < 1 && v >= 0 && kind !== 'date')) {
      if (kind === 'time' && v >= 1) { var h = Math.floor(v * 24); return pad(h) + time.slice(2); }
      return time;
    }
    if (kind === 'date' || (v === Math.floor(v) && kind !== 'time')) return kind === 'datetime' && v !== Math.floor(v) ? date + 'T' + time : (kind === 'datetime' ? date + 'T' + time : date);
    return date + 'T' + time;
  }

  // Numbers as Excel shows them: 15 significant digits, so 0.1+0.2 is 0.3, not 0.30000000000000004.
  function tidyNumber(s) {
    var v = Number(s);
    if (!isFinite(v)) return s;
    return Number(v.toPrecision(15));
  }

  function colIndex(ref) {
    var m = /^([A-Z]+)/.exec(ref || ''); if (!m) return -1;
    var n = 0; for (var i = 0; i < m[1].length; i++) n = n * 26 + (m[1].charCodeAt(i) - 64);
    return n - 1;
  }

  function strFrom(files, path) {
    var f = files[path];
    if (!f) { var k = Object.keys(files).filter(function (x) { return x.toLowerCase() === path.toLowerCase(); })[0]; f = k && files[k]; }
    return f ? new TextDecoder('utf-8').decode(f) : null;
  }

  /** Read an .xlsx / .xlsm file. bytes: Uint8Array. unzip: fflate.unzipSync. Returns { sheets: [{ name, rows }], date1904 }.
      Cells come back typed: numbers, booleans, strings, ISO dates; errors (#N/A...) as null; empty cells as ''. */
  function readXlsx(bytes, unzip) {
    if (!(bytes[0] === 0x50 && bytes[1] === 0x4B)) {
      if (bytes[0] === 0xD0 && bytes[1] === 0xCF) throw new Error('This is an old .xls file (Excel 97-2003). Open it in Excel or LibreOffice and save it as .xlsx or .csv, then drop it here again.');
      throw new Error('This file is not an .xlsx workbook.');
    }
    var files;
    try { files = unzip(bytes); } catch (e) { throw new Error('The workbook could not be opened (the file looks damaged).'); }
    var wb = strFrom(files, 'xl/workbook.xml');
    if (!wb) throw new Error('This zip file is not an Excel workbook (no xl/workbook.xml). Encrypted or password-protected workbooks can’t be read.');
    var date1904 = /date1904="(1|true)"/.test(wb);
    var rels = strFrom(files, 'xl/_rels/workbook.xml.rels') || '';
    var target = {};
    (rels.match(/<(?:\w+:)?Relationship\b[^>]*>/g) || []).forEach(function (r) { target[attr(r, 'Id')] = attr(r, 'Target'); });

    var shared = [];
    var ss = strFrom(files, 'xl/sharedStrings.xml');
    if (ss) (ss.match(/<(?:\w+:)?si\b[\s\S]*?<\/(?:\w+:)?si>|<(?:\w+:)?si\s*\/>/g) || []).forEach(function (si) { shared.push(siText(si)); });

    var kinds = [];
    var st = strFrom(files, 'xl/styles.xml');
    if (st) {
      var custom = {};
      (st.match(/<(?:\w+:)?numFmt\b[^>]*>/g) || []).forEach(function (t) { custom[attr(t, 'numFmtId')] = attr(t, 'formatCode'); });
      var xfs = /<(?:\w+:)?cellXfs\b[^>]*>([\s\S]*?)<\/(?:\w+:)?cellXfs>/.exec(st);
      if (xfs) (xfs[1].match(/<(?:\w+:)?xf\b[^>]*>/g) || []).forEach(function (t) {
        var id = parseInt(attr(t, 'numFmtId') || '0', 10);
        var k = null;
        if (custom[id] != null) k = fmtKind(custom[id]);
        else if (BUILTIN_DATE[id]) k = BUILTIN_TIME[id] ? 'time' : (id === 22 ? 'datetime' : 'date');
        kinds.push(k);
      });
    }

    var sheets = [];
    (wb.match(/<(?:\w+:)?sheet\b[^>]*>/g) || []).forEach(function (tag) {
      var name = attr(tag, 'name') || ('Sheet' + (sheets.length + 1));
      var rid = attr(tag, 'r:id') || attr(tag, 'id');
      var t = target[rid] || ('worksheets/sheet' + (sheets.length + 1) + '.xml');
      var p = t.charAt(0) === '/' ? t.slice(1) : 'xl/' + t.replace(/^\.\//, '');
      var xml = strFrom(files, p);
      if (xml == null) return; // chart sheets, macros sheets
      var hidden = /state="(hidden|veryHidden)"/.test(tag);
      sheets.push({ name: name, hidden: hidden, rows: readSheet(xml, shared, kinds, date1904) });
    });
    if (!sheets.length) throw new Error('No worksheets were found in this workbook.');
    return { sheets: sheets, date1904: date1904 };
  }

  function readSheet(xml, shared, kinds, date1904) {
    var rows = [];
    var data = /<(?:\w+:)?sheetData\b[^>]*>([\s\S]*?)<\/(?:\w+:)?sheetData>/.exec(xml);
    if (!data) return rows;
    var rowRe = /<(?:\w+:)?row\b([^>]*)>([\s\S]*?)<\/(?:\w+:)?row>|<(?:\w+:)?row\b([^>]*)\/>/g, rm, nextRow = 0;
    while ((rm = rowRe.exec(data[1]))) {
      var rAttr = attr(rm[1] || rm[3] || '', 'r');
      var ri = rAttr ? parseInt(rAttr, 10) - 1 : nextRow;
      nextRow = ri + 1;
      var cells = [];
      var body = rm[2] || '';
      var cellRe = /<(?:\w+:)?c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/(?:\w+:)?c>)/g, cm, nextCol = 0;
      while ((cm = cellRe.exec(body))) {
        var a = ' ' + cm[1];
        var ref = attr(a, 'r');
        var ci = ref ? colIndex(ref) : nextCol;
        nextCol = ci + 1;
        var t = attr(a, 't') || 'n';
        var s = parseInt(attr(a, 's') || '0', 10);
        var inner = cm[2] || '';
        var vm = /<(?:\w+:)?v\b[^>]*>([\s\S]*?)<\/(?:\w+:)?v>/.exec(inner);
        var raw = vm ? xmlText(vm[1]) : null;
        var val = '';
        if (t === 's') val = raw != null ? (shared[parseInt(raw, 10)] != null ? shared[parseInt(raw, 10)] : '') : '';
        else if (t === 'inlineStr') { var is = /<(?:\w+:)?is\b[^>]*>([\s\S]*?)<\/(?:\w+:)?is>/.exec(inner); val = is ? siText(is[1]) : ''; }
        else if (t === 'str') val = raw != null ? raw : '';
        else if (t === 'b') val = raw === '1' || raw === 'true';
        else if (t === 'e') val = null;
        else if (t === 'd') val = raw != null ? raw.replace(/Z$/, '').replace(/T00:00:00(\.000)?$/, '') : '';
        else if (raw != null && raw !== '') {
          var k = kinds[s];
          val = k ? serialToISO(raw, k, date1904) : tidyNumber(raw);
        }
        while (cells.length < ci) cells.push('');
        cells[ci] = val;
      }
      while (rows.length < ri) rows.push([]);
      rows[ri] = cells;
    }
    // drop trailing empty rows
    while (rows.length && rows[rows.length - 1].every(function (v) { return v === '' || v == null; })) rows.pop();
    return rows;
  }

  /* ---------- Rows to JSON ---------- */

  function isEmptyRow(r) { return !r || r.every(function (v) { return v === '' || v == null || (typeof v === 'string' && !v.trim()); }); }

  /** Make header names: trimmed, blank -> column_N, duplicates -> name_2. */
  function headerNames(row, width) {
    var seen = Object.create(null), out = [];
    for (var i = 0; i < width; i++) {
      var h = row[i] == null ? '' : String(row[i]).replace(/\s+/g, ' ').trim();
      if (!h) h = 'column_' + (i + 1);
      var base = h, k = 2;
      while (seen[h]) h = base + '_' + (k++);
      seen[h] = true; out.push(h);
    }
    return out;
  }

  var NUM_RE = /^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?$/;
  /** Smart typing of a text cell. Keeps leading zeros, long IDs, phone numbers and '+1' as text. */
  function typeValue(s, opts) {
    if (typeof s !== 'string') return s;
    var t = opts.trim ? s.trim() : s;
    if (opts.types === 'text') return t;
    var x = s.trim();
    if (x === '') return t;
    if (NUM_RE.test(x)) {
      var digits = x.replace(/^-/, '').replace(/[eE].*$/, '').replace('.', '').replace(/^0+/, '');
      if (digits.length <= 15) return Number(x);
      return t;
    }
    if (opts.decimalComma && /^-?(0|[1-9]\d{0,2}(\.\d{3})*|[1-9]\d*),\d+$/.test(x)) return Number(x.replace(/\./g, '').replace(',', '.'));
    if (/^(true|false)$/i.test(x)) return x.toLowerCase() === 'true';
    if (/^(null|NULL)$/.test(x)) return null;
    return t;
  }

  function emptyValue(v) { return v === '' || v == null || (typeof v === 'string' && v.trim() === ''); }

  /** Split a header into a path for nested output: "user.name", "user/name", "tags[0]", "tags.0". */
  function headerPath(h, sep) {
    var parts = [];
    String(h).split(sep === '/' ? '/' : (sep === 'both' ? /[./]/ : '.')).forEach(function (p) {
      var re = /([^\[\]]+)|\[(\d+)\]/g, m;
      while ((m = re.exec(p))) parts.push(m[2] != null ? Number(m[2]) : (/^\d+$/.test(m[1]) && parts.length ? Number(m[1]) : m[1]));
    });
    return parts.length ? parts : [h];
  }

  // Own-property write that is safe for any key, including "__proto__" (no prototype pollution, key kept as written).
  function put(o, k, v) { Object.defineProperty(o, k, { value: v, enumerable: true, writable: true, configurable: true }); }
  function own(o, k) { return Object.prototype.hasOwnProperty.call(o, k) ? o[k] : undefined; }
  function setPath(obj, path, value) {
    var o = obj;
    for (var i = 0; i < path.length - 1; i++) {
      var k = path[i], next = own(o, k);
      if (next == null || typeof next !== 'object') { next = typeof path[i + 1] === 'number' ? [] : {}; put(o, k, next); }
      o = next;
    }
    put(o, path[path.length - 1], value);
  }

  /** rows (array of arrays) -> { records, columns, stats }.
      opts: header (bool), types ('smart'|'text'), empty ('string'|'null'|'omit'), nested ('off'|'.'|'/'|'both'),
            trim (bool), skipEmptyRows (bool), transpose (bool), decimalComma (bool), limit (number) */
  function toRecords(rows, opts) {
    opts = Object.assign({ header: true, types: 'smart', empty: 'string', nested: 'off', trim: true, skipEmptyRows: true }, opts || {});
    rows = rows || [];
    if (opts.transpose) rows = transpose(rows);
    var width = rows.reduce(function (m, r) { return Math.max(m, r ? r.length : 0); }, 0);
    var start = 0;
    if (opts.skipEmptyRows) while (start < rows.length && isEmptyRow(rows[start])) start++;
    var columns = opts.header && rows.length ? headerNames(rows[start] || [], width) : headerNames([], width);
    // drop trailing columns that are blank in the header and empty everywhere
    var body = rows.slice(opts.header ? start + 1 : start);
    if (opts.skipEmptyRows) body = body.filter(function (r) { return !isEmptyRow(r); });
    var used = columns.map(function (c, i) { return !/^column_\d+$/.test(c) || body.some(function (r) { return r && !emptyValue(r[i]); }); });
    while (columns.length && !used[columns.length - 1]) { columns.pop(); used.pop(); }
    var paths = opts.nested && opts.nested !== 'off' ? columns.map(function (c) { return headerPath(c, opts.nested); }) : null;
    var types = columns.map(function () { return {}; });
    var empties = columns.map(function () { return 0; });
    var records = [];
    var limit = opts.limit || Infinity;
    for (var r = 0; r < body.length && records.length < limit; r++) {
      var row = body[r] || [], rec = {};
      for (var c = 0; c < columns.length; c++) {
        var v = row[c];
        if (v === undefined) v = '';
        if (typeof v === 'string') v = typeValue(v, opts);
        else if (typeof v === 'number' && opts.types === 'text') v = String(v);
        else if (typeof v === 'boolean' && opts.types === 'text') v = String(v);
        if (emptyValue(v)) {
          empties[c]++;
          if (opts.empty === 'omit') continue;
          v = opts.empty === 'null' ? null : '';
        } else {
          var ty = v === null ? 'null' : typeof v === 'string' && /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$/.test(v) ? 'date' : typeof v;
          types[c][ty] = (types[c][ty] || 0) + 1;
        }
        if (paths) setPath(rec, paths[c], v); else put(rec, columns[c], v);
      }
      records.push(rec);
    }
    var stats = columns.map(function (name, i) {
      var t = Object.keys(types[i]);
      return { name: name, type: t.length === 0 ? 'empty' : t.length === 1 ? t[0] : 'mixed', empty: empties[i] };
    });
    return { records: records, columns: columns, stats: stats, total: body.length };
  }

  function transpose(rows) {
    var w = rows.reduce(function (m, r) { return Math.max(m, r ? r.length : 0); }, 0), out = [];
    for (var c = 0; c < w; c++) out.push(rows.map(function (r) { return r && r[c] !== undefined ? r[c] : ''; }));
    return out;
  }

  /** Shape records. shape: 'array' | 'jsonl' | 'keyed' | 'arrays' | 'columns'. keyColumn for 'keyed' (default: first column). */
  function shape(res, shapeName, keyColumn) {
    var recs = res.records, cols = res.columns;
    if (shapeName === 'arrays') return [cols].concat(recs.map(function (r) { return cols.map(function (c) { var x = own(r, c); return x === undefined ? null : x; }); }));
    if (shapeName === 'columns') {
      var o = {}; cols.forEach(function (c) { put(o, c, recs.map(function (r) { var x = own(r, c); return x === undefined ? null : x; })); }); return o;
    }
    if (shapeName === 'keyed') {
      var key = keyColumn && cols.indexOf(keyColumn) >= 0 ? keyColumn : cols[0];
      var out = {}, groups = Object.create(null);
      recs.forEach(function (r, i) {
        var kv = own(r, key);
        var k = kv == null || kv === '' ? 'row_' + (i + 1) : String(kv);
        var rest = {}; Object.keys(r).forEach(function (f) { if (f !== key) put(rest, f, r[f]); });
        if (Object.prototype.hasOwnProperty.call(out, k)) {
          if (!groups[k]) { groups[k] = [out[k]]; put(out, k, groups[k]); }
          groups[k].push(rest);
        } else put(out, k, rest);
      });
      return out;
    }
    return recs;
  }

  /** Text output. indent: 2 | 4 | 'tab' | 0. jsonl writes one compact record per line. */
  function stringify(value, shapeName, indent) {
    if (shapeName === 'jsonl') return (Array.isArray(value) ? value : [value]).map(function (r) { return JSON.stringify(r); }).join('\n') + '\n';
    var ind = indent === 'tab' ? '\t' : Number(indent) || 0;
    return JSON.stringify(value, null, ind) + (ind ? '\n' : '');
  }

  /** One call for a whole text input. Returns { json, result, delimiter, warnings }. */
  function convertText(text, opts) {
    opts = opts || {};
    var parsed = parseCSV(text, { delimiter: opts.delimiter || 'auto' });
    var res = toRecords(parsed.rows, opts);
    var shaped = shape(res, opts.shape || 'array', opts.keyColumn);
    return { json: stringify(shaped, opts.shape || 'array', opts.indent == null ? 2 : opts.indent), result: res, delimiter: parsed.delimiter, warnings: parsed.warnings };
  }

  /** Convert a workbook: one sheet by name, or all sheets as { "Sheet name": [...] }. */
  function convertWorkbook(book, opts) {
    opts = opts || {};
    var shapeName = opts.shape || 'array';
    var visible = book.sheets.filter(function (s) { return !s.hidden || opts.includeHidden; });
    if (!visible.length) visible = book.sheets;
    if (opts.sheet && opts.sheet !== '*') {
      var s = book.sheets.filter(function (x) { return x.name === opts.sheet; })[0] || visible[0];
      var res = toRecords(s.rows, opts);
      return { json: stringify(shape(res, shapeName, opts.keyColumn), shapeName, opts.indent == null ? 2 : opts.indent), result: res, sheet: s.name };
    }
    var all = {}, results = {}, lines = [];
    visible.forEach(function (sh) {
      var r = toRecords(sh.rows, opts);
      results[sh.name] = r;
      var v = shape(r, shapeName, opts.keyColumn);
      if (shapeName === 'jsonl') v.forEach(function (rec) { var o = { sheet: sh.name }; Object.keys(rec).forEach(function (k) { put(o, k, rec[k]); }); lines.push(JSON.stringify(o)); });
      else put(all, sh.name, v);
    });
    var json = shapeName === 'jsonl' ? lines.join('\n') + '\n' : stringify(all, 'array', opts.indent == null ? 2 : opts.indent);
    return { json: json, results: results, sheet: '*' };
  }

  return {
    decodeBytes: decodeBytes, detectDelimiter: detectDelimiter, parseCSV: parseCSV,
    readXlsx: readXlsx, fmtKind: fmtKind, serialToISO: serialToISO,
    typeValue: typeValue, headerPath: headerPath, toRecords: toRecords, shape: shape, stringify: stringify,
    convertText: convertText, convertWorkbook: convertWorkbook
  };
});
