/* JSON to Excel / CSV core. Pure functions; works in the browser (window.PandapiJson) and in Node (module.exports). */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api; else root.PandapiJson = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var MAX_ROWS = 1048575;          // Excel rows minus the header
  var MAX_COLS = 16384;
  var MAX_CELL = 32767;
  var WRAPPER_KEYS = ['items', 'data', 'results', 'records', 'rows', 'entries', 'list', 'value', 'hits', 'docs', 'notices'];

  function isPlainObject(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }

  /** Parse JSON, JSON Lines / NDJSON, or concatenated objects. Returns { data, format }. Throws with a readable message. */
  function parseText(text) {
    text = String(text || '').replace(/^﻿/, '').trim();
    if (!text) throw new Error('The input is empty.');
    try { return { data: JSON.parse(text), format: 'JSON' }; } catch (first) {
      var lines = text.split(/\r?\n/).map(function (l) { return l.trim(); }).filter(Boolean);
      if (lines.length > 1) {
        var out = [], bad = -1;
        for (var i = 0; i < lines.length; i++) {
          var l = lines[i].replace(/,$/, '');
          try { out.push(JSON.parse(l)); } catch (e) { bad = i; break; }
        }
        if (bad === -1) return { data: out, format: 'JSON Lines' };
      }
      var pos = errorPosition(text);
      if (pos >= 0) {
        var before = text.slice(0, pos), line = before.split('\n').length, col = pos - before.lastIndexOf('\n');
        var near = text.slice(pos, pos + 20).split('\n')[0];
        throw new Error('Invalid JSON at line ' + line + ', column ' + col + (near ? ' (near "' + near + '")' : ' (the text ends too early)') + '.');
      }
      throw new Error('Invalid JSON: ' + first.message);
    }
  }

  /** Index of the first syntax error in a JSON text (-1 if none found). Small validator, used only for messages. */
  function errorPosition(s) {
    var i = 0;
    function ws() { while (i < s.length && /\s/.test(s[i])) i++; }
    function fail() { throw i; }
    function str() {
      i++;
      while (i < s.length && s[i] !== '"') { if (s[i] === '\\') i++; else if (s[i] === '\n') fail(); i++; }
      if (i >= s.length) fail(); i++;
    }
    function lit(w) { if (s.substr(i, w.length) !== w) fail(); i += w.length; }
    function num() { var m = /^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/.exec(s.slice(i, i + 400)); if (!m) fail(); i += m[0].length; }
    function val() {
      ws(); var c = s[i];
      if (c === '{') { i++; ws(); if (s[i] === '}') { i++; return; } for (;;) { ws(); if (s[i] !== '"') fail(); str(); ws(); if (s[i] !== ':') fail(); i++; val(); ws(); if (s[i] === ',') { i++; continue; } if (s[i] === '}') { i++; return; } fail(); } }
      if (c === '[') { i++; ws(); if (s[i] === ']') { i++; return; } for (;;) { val(); ws(); if (s[i] === ',') { i++; continue; } if (s[i] === ']') { i++; return; } fail(); } }
      if (c === '"') return str();
      if (c === 't') return lit('true');
      if (c === 'f') return lit('false');
      if (c === 'n') return lit('null');
      return num();
    }
    try { val(); ws(); return i < s.length ? i : -1; } catch (p) { return typeof p === 'number' ? Math.min(p, s.length) : -1; }
  }

  /** Find the list of records inside any JSON shape. Returns { records, path }. */
  function findRecords(data) {
    if (Array.isArray(data)) {
      if (data.length && data.every(Array.isArray)) {
        var head = data[0];
        if (head.every(function (h) { return typeof h === 'string'; }) && data.length > 1) {
          return { records: data.slice(1).map(function (r) { var o = {}; head.forEach(function (h, i) { o[h] = r[i]; }); return o; }), path: '(array of arrays, first row as header)' };
        }
        return { records: data.map(function (r) { var o = {}; r.forEach(function (v, i) { o['col' + (i + 1)] = v; }); return o; }), path: '(array of arrays)' };
      }
      return { records: data.map(function (r) { return isPlainObject(r) ? r : { value: r }; }), path: '(top-level array)' };
    }
    if (isPlainObject(data)) {
      var best = null;
      (function walk(obj, path, depth) {
        Object.keys(obj).forEach(function (k) {
          var v = obj[k], p = path ? path + '.' + k : k;
          if (Array.isArray(v) && v.length && v.some(isPlainObject)) {
            var score = v.length + (WRAPPER_KEYS.indexOf(k.toLowerCase()) >= 0 ? 0.5 : 0);
            if (!best || score > best.score) best = { score: score, records: v, path: p };
          } else if (isPlainObject(v) && depth < 2) walk(v, p, depth + 1);
        });
      })(data, '', 0);
      if (best && best.records.length > 1) {
        return { records: best.records.map(function (r) { return isPlainObject(r) ? r : { value: r }; }), path: best.path };
      }
      return { records: [data], path: '(single object)' };
    }
    return { records: [{ value: data }], path: '(single value)' };
  }

  /** First path (dot notation) that holds an array of objects, by how many records have it. */
  function detectExplodePath(records) {
    var counts = {};
    records.slice(0, 500).forEach(function (r) {
      (function walk(obj, path) {
        Object.keys(obj).forEach(function (k) {
          var v = obj[k], p = path ? path + '.' + k : k;
          if (Array.isArray(v) && v.some(isPlainObject)) counts[p] = (counts[p] || 0) + 1;
          else if (isPlainObject(v)) walk(v, p);
        });
      })(r, '');
    });
    var best = null;
    Object.keys(counts).forEach(function (p) { if (!best || counts[p] > counts[best]) best = p; });
    return best;
  }

  function getPath(obj, path) {
    return path.split('.').reduce(function (o, k) { return o == null ? undefined : o[k]; }, obj);
  }
  function withoutPath(obj, path) {
    var parts = path.split('.');
    var copy = Array.isArray(obj) ? obj.slice() : Object.assign({}, obj), cur = copy;
    for (var i = 0; i < parts.length - 1; i++) {
      if (!isPlainObject(cur[parts[i]])) return copy;
      cur[parts[i]] = Object.assign({}, cur[parts[i]]); cur = cur[parts[i]];
    }
    delete cur[parts[parts.length - 1]];
    return copy;
  }

  /**
   * Flatten records into rows of scalar values.
   * opts.arrays: 'join' (default: lists of values joined with "; ", lists of objects as JSON text),
   *              'columns' (tags.0, tags.1, items.0.name ...), 'rows' (one row per item of opts.explodePath).
   * opts.joiner: separator for 'join' (default "; ").
   */
  function flatten(records, opts) {
    opts = opts || {};
    var mode = opts.arrays || 'join', joiner = opts.joiner == null ? '; ' : opts.joiner;
    var explodePath = mode === 'rows' ? (opts.explodePath || detectExplodePath(records)) : null;
    var rows = [], colIndex = {}, cols = [];
    function addCol(k) { if (!(k in colIndex)) { colIndex[k] = cols.length; cols.push(k); } }

    function flat(value, prefix, row) {
      if (value === null || value === undefined) { if (prefix) { addCol(prefix); row[prefix] = null; } return; }
      if (Array.isArray(value)) {
        if (mode === 'columns') {
          if (!value.length) { addCol(prefix); row[prefix] = ''; return; }
          value.forEach(function (v, i) { flat(v, prefix + '.' + i, row); });
          return;
        }
        addCol(prefix);
        row[prefix] = value.every(function (v) { return v === null || typeof v !== 'object'; })
          ? value.filter(function (v) { return v !== null && v !== undefined; }).join(joiner)
          : JSON.stringify(value);
        return;
      }
      if (isPlainObject(value)) {
        var keys = Object.keys(value);
        if (!keys.length && prefix) { addCol(prefix); row[prefix] = ''; return; }
        keys.forEach(function (k) { flat(value[k], prefix ? prefix + '.' + k : k, row); });
        return;
      }
      addCol(prefix || 'value'); row[prefix || 'value'] = value;
    }

    records.forEach(function (rec) {
      if (explodePath) {
        var arr = getPath(rec, explodePath);
        var parent = withoutPath(rec, explodePath);
        if (Array.isArray(arr) && arr.length) {
          arr.forEach(function (item) {
            var row = {}; flat(parent, '', row);
            flat(item, explodePath, row);
            rows.push(row);
          });
          return;
        }
        var r0 = {}; flat(parent, '', r0); rows.push(r0); return;
      }
      var row = {}; flat(rec, '', row); rows.push(row);
    });
    return { rows: rows, columns: cols, explodePath: explodePath };
  }

  function looksNumeric(s) {
    // Plain decimal numbers only; keeps IDs with leading zeros, phone numbers with +, and >15 digit numbers as text.
    return typeof s === 'string' && /^-?(0|[1-9]\d{0,14})(\.\d+)?$/.test(s.trim()) && s.trim() === s;
  }

  function cellValue(v) {
    if (v === null || v === undefined) return '';
    if (typeof v === 'object') return JSON.stringify(v);
    return v;
  }

  /** CSV text. opts: { delimiter: ',', bom: true, protectFormulas: true, lineEnding: '\r\n' } */
  function toCSV(rows, columns, opts) {
    opts = opts || {};
    var d = opts.delimiter || ',', eol = opts.lineEnding || '\r\n', protect = opts.protectFormulas !== false;
    function esc(v) {
      v = cellValue(v);
      var s = typeof v === 'string' ? v : String(v);
      if (protect && typeof v === 'string' && /^[=+\-@\t\r]/.test(s) && !looksNumeric(s)) s = "'" + s;
      if (s.indexOf(d) >= 0 || /["\r\n]/.test(s) || /^\s|\s$/.test(s)) s = '"' + s.replace(/"/g, '""') + '"';
      return s;
    }
    var lines = [columns.map(esc).join(d)];
    rows.forEach(function (r) { lines.push(columns.map(function (c) { return esc(r[c]); }).join(d)); });
    return (opts.bom === false ? '' : '﻿') + lines.join(eol) + eol;
  }

  function xmlEsc(s) {
    return String(s).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F￾￿]/g, '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function colName(i) { var s = ''; i++; while (i > 0) { var m = (i - 1) % 26; s = String.fromCharCode(65 + m) + s; i = Math.floor((i - 1) / 26); } return s; }

  /**
   * Build .xlsx parts. Returns { files: {path: string}, truncatedCells, droppedRows, droppedCols }.
   * opts: { numericText: true (turn "12.5" into a number), sheetName: 'Data' }
   */
  function xlsxParts(rows, columns, opts) {
    opts = opts || {};
    var numericText = opts.numericText !== false;
    var truncated = 0, droppedRows = Math.max(0, rows.length - MAX_ROWS), droppedCols = Math.max(0, columns.length - MAX_COLS);
    var cols = columns.slice(0, MAX_COLS), data = rows.slice(0, MAX_ROWS);
    var widths = cols.map(function (c) { return Math.min(60, Math.max(8, String(c).length + 2)); });
    var out = [];
    function cell(ref, v, style) {
      v = cellValue(v);
      if (v === '') return '';
      var s = style ? ' s="' + style + '"' : '';
      if (typeof v === 'number' && isFinite(v)) return '<c r="' + ref + '"' + s + '><v>' + v + '</v></c>';
      if (typeof v === 'boolean') return '<c r="' + ref + '"' + s + ' t="b"><v>' + (v ? 1 : 0) + '</v></c>';
      var str = String(v);
      if (numericText && looksNumeric(str)) return '<c r="' + ref + '"' + s + '><v>' + Number(str) + '</v></c>';
      if (str.length > MAX_CELL) { str = str.slice(0, MAX_CELL); truncated++; }
      return '<c r="' + ref + '"' + s + ' t="inlineStr"><is><t xml:space="preserve">' + xmlEsc(str) + '</t></is></c>';
    }
    out.push('<row r="1">' + cols.map(function (c, i) { return cell(colName(i) + '1', String(c), 1); }).join('') + '</row>');
    data.forEach(function (r, ri) {
      var n = ri + 2, cells = '';
      for (var i = 0; i < cols.length; i++) {
        var v = r[cols[i]];
        if (ri < 200 && v != null) { var len = String(cellValue(v)).length; if (len + 2 > widths[i]) widths[i] = Math.min(60, len + 2); }
        cells += cell(colName(i) + n, v, 0);
      }
      out.push('<row r="' + n + '">' + cells + '</row>');
    });
    var last = colName(Math.max(0, cols.length - 1)) + (data.length + 1);
    var sheet = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">' +
      '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>' +
      '<cols>' + widths.map(function (w, i) { return '<col min="' + (i + 1) + '" max="' + (i + 1) + '" width="' + w + '" customWidth="1"/>'; }).join('') + '</cols>' +
      '<sheetData>' + out.join('') + '</sheetData>' +
      (cols.length ? '<autoFilter ref="A1:' + last + '"/>' : '') + '</worksheet>';
    var name = xmlEsc(String(opts.sheetName || 'Data').replace(/[\\\/?*\[\]:]/g, ' ').slice(0, 31));
    var files = {
      '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>',
      '_rels/.rels': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>',
      'docProps/core.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>Pandapi Tools</dc:creator></cp:coreProperties>',
      'docProps/app.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Pandapi Tools</Application></Properties>',
      'xl/workbook.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="' + name + '" sheetId="1" r:id="rId1"/></sheets>' + (cols.length ? '<definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">\'' + name.replace(/'/g, "''") + '\'!$A$1:$' + colName(cols.length - 1) + '$' + (data.length + 1) + '</definedName></definedNames>' : '') + '</workbook>',
      'xl/_rels/workbook.xml.rels': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
      'xl/styles.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>',
      'xl/worksheets/sheet1.xml': sheet
    };
    return { files: files, truncatedCells: truncated, droppedRows: droppedRows, droppedCols: droppedCols };
  }

  return { parseText: parseText, findRecords: findRecords, flatten: flatten, detectExplodePath: detectExplodePath,
    toCSV: toCSV, xlsxParts: xlsxParts, looksNumeric: looksNumeric, colName: colName, MAX_ROWS: MAX_ROWS };
});
