(function () {
  'use strict';
  var P = window.Pandapi, C = window.PandapiCsvJson, $ = P.$;
  var input = $('#csv-in'), out = $('#json-out'), status = $('#status'), summary = $('#summary'), fileNote = $('#file-note');
  var o = {
    delim: $('#opt-delim'), header: $('#opt-header'), types: $('#opt-types'), empty: $('#opt-empty'), nested: $('#opt-nested'),
    shape: $('#opt-shape'), key: $('#opt-key'), keyWrap: $('#key-wrap'), indent: $('#opt-indent'), decimal: $('#opt-decimal'),
    transpose: $('#opt-transpose'), sheet: $('#opt-sheet'), sheetWrap: $('#sheet-wrap')
  };
  var MAX_SHOW = 2000000; // characters shown in the output box; downloads always hold everything
  var book = null, bookName = '', bigText = null, fileBase = 'data', json = '', timer = null;

  function opts() {
    return {
      delimiter: o.delim.value, header: o.header.checked, types: o.types.value, empty: o.empty.value, nested: o.nested.value,
      shape: o.shape.value, keyColumn: o.key.value || null, indent: o.indent.value === 'tab' ? 'tab' : Number(o.indent.value),
      decimalComma: o.decimal.checked, transpose: o.transpose.checked, sheet: o.sheet.value || '*'
    };
  }

  function convert() {
    var op = opts();
    if (book) return C.convertWorkbook(book, op);
    var text = bigText != null ? bigText : input.value;
    if (!text.trim()) return null;
    return C.convertText(text, op);
  }

  function render() {
    json = ''; out.value = ''; summary.textContent = ''; setButtons(false);
    o.keyWrap.hidden = o.shape.value !== 'keyed';
    var r;
    try { r = convert(); } catch (e) { P.setStatus(status, e.message, 'error'); return; }
    if (!r) { P.setStatus(status, ''); drawStats(null); return; }
    json = r.json;
    var res = r.result || null;
    if (!res && r.results) { var names = Object.keys(r.results); res = names.length ? r.results[names[0]] : null; }
    fillKeys(res ? res.columns : []);
    var parts = [];
    if (book) {
      if (r.sheet === '*') parts.push(Object.keys(r.results).length + ' sheets · ' + Object.keys(r.results).reduce(function (n, k) { return n + r.results[k].records.length; }, 0).toLocaleString() + ' rows');
      else parts.push('Sheet “' + r.sheet + '” · ' + r.result.records.length.toLocaleString() + ' rows × ' + r.result.columns.length + ' columns');
    } else {
      parts.push(NAMES[r.delimiter] + ' · ' + r.result.records.length.toLocaleString() + ' rows × ' + r.result.columns.length + ' columns');
    }
    parts.push(P.formatBytes(new Blob([json]).size));
    summary.textContent = parts.join(' · ');
    out.value = json.length > MAX_SHOW ? json.slice(0, MAX_SHOW) + '\n… (preview cut here; Copy and Download include everything)' : json;
    drawStats(book && r.sheet === '*' ? null : res);
    var warn = (r.warnings || []).join(' ');
    var count = res ? res.records.length : 0;
    if (r.results) count = Object.keys(r.results).reduce(function (n, k) { return n + r.results[k].records.length; }, 0);
    setButtons(true);
    if (warn) P.setStatus(status, warn, 'error');
    else if (!count) P.setStatus(status, 'No data rows found. If the first row is data, untick “First row is the header”.');
    else P.setStatus(status, 'Done. Copy the JSON or download it.', 'ok');
  }
  var NAMES = { ',': 'Comma-separated', ';': 'Semicolon-separated', '\t': 'Tab-separated', '|': 'Pipe-separated' };

  function fillKeys(cols) {
    var keep = o.key.value;
    o.key.innerHTML = cols.map(function (c) { return '<option>' + esc(c) + '</option>'; }).join('');
    if (keep && cols.indexOf(keep) >= 0) o.key.value = keep;
  }

  function drawStats(res) {
    var wrap = $('#cols'), list = $('#col-list');
    if (!res || !res.stats.length) { wrap.hidden = true; list.innerHTML = ''; return; }
    wrap.hidden = false;
    list.innerHTML = res.stats.slice(0, 200).map(function (s) {
      return '<li><span class="name">' + esc(s.name) + '</span> <span class="meta">' + TYPE[s.type] + (s.empty ? ' · ' + s.empty.toLocaleString() + ' empty' : '') + '</span></li>';
    }).join('');
  }
  var TYPE = { number: 'number', string: 'text', boolean: 'true/false', date: 'date', null: 'null', mixed: 'mixed', empty: 'all empty' };

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function setButtons(on) { ['#btn-copy', '#btn-download'].forEach(function (s) { $(s).disabled = !on; }); }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 200); }
  function ext() { return o.shape.value === 'jsonl' ? '.jsonl' : '.json'; }

  function clearFile() {
    book = null; bookName = ''; bigText = null; fileNote.textContent = '';
    o.sheetWrap.hidden = true; o.sheet.innerHTML = ''; input.readOnly = false;
  }

  function isXlsx(name, bytes) { return /\.(xlsx|xlsm)$/i.test(name) || (bytes[0] === 0x50 && bytes[1] === 0x4B); }

  function readFile(f) {
    return f.arrayBuffer().then(function (buf) { return { name: f.name, bytes: new Uint8Array(buf) }; });
  }

  function loadOne(f) {
    P.setStatus(status, 'Reading ' + f.name + '…');
    return readFile(f).then(function (file) {
      clearFile();
      fileBase = P.baseName(file.name);
      if (/\.xls$/i.test(file.name) || (file.bytes[0] === 0xD0 && file.bytes[1] === 0xCF)) throw new Error('“' + file.name + '” is an old .xls file (Excel 97-2003). Open it in Excel or LibreOffice, save it as .xlsx or .csv, and drop it here again.');
      if (isXlsx(file.name, file.bytes)) {
        book = C.readXlsx(file.bytes, window.fflate.unzipSync);
        bookName = file.name;
        var vis = book.sheets.filter(function (s) { return !s.hidden; });
        o.sheet.innerHTML = (vis.length > 1 ? '<option value="*">All sheets (one JSON object)</option>' : '') +
          book.sheets.map(function (s) { return '<option value="' + esc(s.name) + '">' + esc(s.name) + (s.hidden ? ' (hidden)' : '') + '</option>'; }).join('');
        o.sheet.value = vis.length > 1 ? '*' : (vis[0] || book.sheets[0]).name;
        o.sheetWrap.hidden = false;
        input.value = ''; input.readOnly = true;
        input.placeholder = 'Excel workbook loaded: ' + file.name + '. Click Clear to paste text instead.';
        fileNote.textContent = file.name + ' · ' + P.formatBytes(file.bytes.length) + ' · ' + book.sheets.length + ' sheet' + (book.sheets.length > 1 ? 's' : '');
      } else {
        var d = C.decodeBytes(file.bytes);
        if (d.text.length > 1000000) { bigText = d.text; input.value = d.text.slice(0, 20000) + '\n…'; input.readOnly = true; }
        else input.value = d.text;
        fileNote.textContent = file.name + ' · ' + P.formatBytes(file.bytes.length) + ' · ' + d.encoding + (bigText != null ? ' · large file: the box shows the start, the JSON holds every row' : '');
      }
      render();
    }).catch(function (e) { clearFile(); P.setStatus(status, e.message, 'error'); });
  }

  function batch(files) {
    var list = $('#batch-list'), bstatus = $('#batch-status');
    list.innerHTML = '';
    P.setStatus(bstatus, 'Converting ' + files.length + ' files…');
    var op = opts(); op.sheet = '*';
    var outFiles = [], ok = 0, failed = 0;
    var chain = Promise.resolve();
    files.forEach(function (f) {
      chain = chain.then(function () { return readFile(f); }).then(function (file) {
        var r, li = document.createElement('li');
        try {
          if (/\.xls$/i.test(file.name) || (file.bytes[0] === 0xD0 && file.bytes[1] === 0xCF)) throw new Error('old .xls: save it as .xlsx first');
          if (isXlsx(file.name, file.bytes)) {
            var b = C.readXlsx(file.bytes, window.fflate.unzipSync);
            var vis = b.sheets.filter(function (s) { return !s.hidden; });
            if (vis.length === 1) op.sheet = vis[0].name; else op.sheet = '*';
            r = C.convertWorkbook(b, op);
          } else r = C.convertText(C.decodeBytes(file.bytes).text, op);
          outFiles.push({ name: P.baseName(file.name) + ext(), data: r.json });
          ok++;
          li.innerHTML = '<span class="name">' + esc(file.name) + '</span><span class="meta">' + P.formatBytes(new Blob([r.json]).size) + '</span>';
        } catch (e) {
          failed++;
          li.innerHTML = '<span class="name">' + esc(file.name) + '</span><span class="meta" style="color:var(--danger)">' + esc(e.message) + '</span>';
        }
        list.appendChild(li);
      });
    });
    chain.then(function () {
      if (outFiles.length) P.downloadBlob(P.zipFiles(outFiles), 'json-files.zip');
      P.setStatus(bstatus, ok + ' converted' + (failed ? ', ' + failed + ' failed' : '') + (ok ? '. Your .zip is downloading.' : '.'), failed && !ok ? 'error' : 'ok');
    });
  }

  function onFiles(files) {
    files = files.filter(function (f) { return /\.(csv|tsv|txt|tab|psv|xlsx|xlsm|xls)$/i.test(f.name) || !/\.[a-z0-9]+$/i.test(f.name); });
    if (!files.length) { P.setStatus(status, 'Drop .csv, .tsv, .txt or .xlsx files.', 'error'); return; }
    if (files.length === 1) loadOne(files[0]); else batch(files);
  }

  P.setupDrop($('#drop'), $('#file-in'), onFiles);
  input.addEventListener('input', function () { bigText = null; schedule(); });
  Object.keys(o).forEach(function (k) { var el = o[k]; if (el && /^(INPUT|SELECT)$/.test(el.tagName)) el.addEventListener('change', render); });
  $('#btn-sample').addEventListener('click', function () { clearFile(); fileBase = 'orders'; input.value = $('#sample-csv').textContent.replace(/^\n/, ''); render(); input.focus(); });
  $('#btn-clear').addEventListener('click', function () { clearFile(); input.value = ''; input.placeholder = input.dataset.placeholder; fileBase = 'data'; render(); input.focus(); });
  input.dataset.placeholder = input.placeholder;
  $('#btn-copy').addEventListener('click', function () {
    P.copyText(json).then(function (ok) { P.setStatus(status, ok ? 'JSON copied.' : 'Copy failed. Select the text and press Ctrl+C.', ok ? 'ok' : 'error'); });
  });
  $('#btn-download').addEventListener('click', function () {
    var sheetPart = book && o.sheet.value && o.sheet.value !== '*' ? '-' + o.sheet.value.replace(/[^\w-]+/g, '_') : '';
    P.downloadText(json, fileBase + sheetPart + ext(), o.shape.value === 'jsonl' ? 'application/x-ndjson' : 'application/json');
  });
  render();
})();
