(function () {
  'use strict';
  var P = window.Pandapi, T = window.PandapiTables, J = window.PandapiJson, $ = P.$;
  var input = $('#html-in'), list = $('#table-list'), preview = $('#preview'), summary = $('#summary'), status = $('#status');
  var opt = { header: $('#opt-header'), merged: $('#opt-merged'), numbers: $('#opt-numbers'), symbols: $('#opt-symbols'),
    footnotes: $('#opt-footnotes'), links: $('#opt-links'), rich: $('#opt-rich'), delim: $('#opt-delim') };
  var tables = [], current = 0, chosen = {}, fileBase = 'tables', timer = null;
  var buttons = ['#btn-xlsx', '#btn-csv', '#btn-copy'].map(function (s) { return $(s); });

  function options() {
    return { header: opt.header.value, mergedCells: opt.merged.value, numbers: opt.numbers.checked, stripSymbols: opt.symbols.checked,
      footnotes: opt.footnotes.checked ? 'remove' : 'keep', links: opt.links.checked };
  }

  function render() {
    var html = input.value;
    status.textContent = '';
    if (!html.trim()) { tables = []; draw(); P.setStatus(summary, ''); return; }
    var t0 = performance.now();
    try { tables = T.extract(html, options()); } catch (e) { tables = []; draw(); P.setStatus(summary, 'Could not read this HTML: ' + e.message, 'error'); return; }
    if (!tables.length) {
      draw();
      P.setStatus(summary, /<table/i.test(html) ? 'The tables in this HTML are empty.' : 'No <table> found. Copy the table from the web page (select it, then Ctrl+C) and paste it here, or paste the page source (Ctrl+U).', 'error');
      return;
    }
    // Keep earlier choices when options change; by default pick real data tables, not 1-row layout tables.
    tables.forEach(function (t) { if (!(t.index in chosen)) chosen[t.index] = !t.small && !t.nested; });
    if (!tables.some(function (t) { return chosen[t.index]; })) chosen[tables[0].index] = true;
    if (current >= tables.length) current = 0;
    draw();
    var n = tables.length;
    P.setStatus(summary, n + (n === 1 ? ' table' : ' tables') + ' found in ' + Math.round(performance.now() - t0) + ' ms. Nothing was uploaded.', 'ok');
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 200); }

  function draw() {
    list.innerHTML = '';
    tables.forEach(function (t, i) {
      var li = document.createElement('li'), cb = document.createElement('input'), btn = document.createElement('button');
      cb.type = 'checkbox'; cb.checked = !!chosen[t.index]; cb.setAttribute('aria-label', 'Include ' + t.name + ' in the download');
      cb.addEventListener('change', function () { chosen[t.index] = cb.checked; updateButtons(); });
      btn.type = 'button'; btn.className = 'linklike' + (i === current ? ' active' : '');
      btn.textContent = t.name + ' (' + t.rowCount.toLocaleString() + ' × ' + t.colCount + ')';
      if (i === current) btn.setAttribute('aria-current', 'true');
      btn.addEventListener('click', function () { current = i; draw(); });
      li.appendChild(cb); li.appendChild(btn); list.appendChild(li);
    });
    $('#tables-wrap').hidden = !tables.length;
    drawPreview(); updateButtons();
  }

  function drawPreview() {
    preview.innerHTML = '';
    var t = tables[current];
    if (!t) return;
    var thead = preview.createTHead().insertRow();
    t.columns.forEach(function (c) { var th = document.createElement('th'); th.textContent = c; thead.appendChild(th); });
    var tb = preview.createTBody();
    t.rows.slice(0, 50).forEach(function (r) {
      var tr = tb.insertRow();
      t.columns.forEach(function (c) { var td = tr.insertCell(); var v = r[c]; td.textContent = v; if (opt.numbers.checked && J.looksNumeric(String(v))) td.className = 'num'; });
    });
    $('#preview-note').textContent = t.rowCount > 50 ? 'Showing the first 50 of ' + t.rowCount.toLocaleString() + ' rows of "' + t.name + '".' : 'Preview of "' + t.name + '".';
  }

  function selected() { return tables.filter(function (t) { return chosen[t.index]; }); }
  function updateButtons() { var any = selected().length > 0; buttons[0].disabled = !any; buttons[1].disabled = !any; buttons[2].disabled = !tables[current]; }
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || 'table'; }

  $('#btn-xlsx').addEventListener('click', function () {
    var sel = selected();
    if (!sel.length) return;
    var wb = T.workbook(sel, options()), enc = new TextEncoder(), zip = {};
    Object.keys(wb.files).forEach(function (k) { zip[k] = enc.encode(wb.files[k]); });
    var name = sel.length === 1 ? slug(sel[0].name) : fileBase;
    P.downloadBlob(new Blob([window.fflate.zipSync(zip, { level: 6 })], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), name + '.xlsx');
    var notes = [];
    if (wb.droppedRows) notes.push(wb.droppedRows.toLocaleString() + ' rows past Excel\'s limit were left out (use CSV)');
    if (wb.truncatedCells) notes.push(wb.truncatedCells + ' very long cells were cut to 32,767 characters');
    P.setStatus(status, notes.length ? 'Downloaded, but ' + notes.join('; ') + '.' : 'Excel file downloaded: ' + sel.length + (sel.length === 1 ? ' sheet.' : ' sheets, one per table.'), notes.length ? 'error' : 'ok');
  });
  function csv(t) { return J.toCSV(t.rows, t.columns, { delimiter: opt.delim.value === 'tab' ? '\t' : opt.delim.value, protectFormulas: true }); }
  $('#btn-csv').addEventListener('click', function () {
    var sel = selected();
    if (!sel.length) return;
    var ext = opt.delim.value === 'tab' ? '.tsv' : '.csv';
    if (sel.length === 1) P.downloadText(csv(sel[0]), slug(sel[0].name) + ext, 'text/csv;charset=utf-8');
    else {
      var used = {};
      P.downloadBlob(P.zipFiles(sel.map(function (t) { var n = slug(t.name), k = 2, b = n; while (used[n]) n = b + '-' + (k++); used[n] = 1; return { name: n + ext, data: csv(t) }; })), fileBase + '-csv.zip');
    }
    P.setStatus(status, sel.length === 1 ? 'CSV downloaded.' : sel.length + ' CSV files downloaded in one .zip.', 'ok');
  });
  $('#btn-copy').addEventListener('click', function () {
    var t = tables[current];
    if (!t) return;
    P.copyText(T.toTSV(t)).then(function (ok) { P.setStatus(status, ok ? 'Copied "' + t.name + '". Paste it into Excel or Google Sheets.' : 'Copy failed: download the CSV instead.', ok ? 'ok' : 'error'); });
  });
  $('#btn-all').addEventListener('click', function () { var all = !tables.every(function (t) { return chosen[t.index]; }); tables.forEach(function (t) { chosen[t.index] = all; }); draw(); });

  input.addEventListener('input', function () { fileBase = 'tables'; chosen = {}; current = 0; schedule(); });
  Object.keys(opt).forEach(function (k) { if (k !== 'rich' && k !== 'delim') opt[k].addEventListener('change', render); });

  // Paste from a web page: take the clipboard's HTML (the real table) instead of tab-separated text.
  input.addEventListener('paste', function (e) {
    if (!opt.rich.checked || !e.clipboardData) return;
    var html = e.clipboardData.getData('text/html');
    if (!html || !/<table/i.test(html)) return;
    e.preventDefault();
    input.value = html.replace(/<!--StartFragment-->|<!--EndFragment-->/g, '');
    fileBase = 'tables'; chosen = {}; current = 0;
    render();
  });

  P.setupDrop($('#drop'), $('#file-in'), function (files) {
    var f = files.filter(function (x) { return /\.(html?|xhtml|xls)$/i.test(x.name) || /html/.test(x.type); })[0];
    if (!f) { P.setStatus(summary, 'Drop an .html or .htm file (a saved web page).', 'error'); return; }
    f.text().then(function (txt) { input.value = txt; fileBase = slug(P.baseName(f.name)); chosen = {}; current = 0; render(); });
  });

  $('#btn-clear').addEventListener('click', function () { input.value = ''; chosen = {}; current = 0; render(); input.focus(); });
  $('#btn-sample').addEventListener('click', function () { input.value = document.getElementById('sample-html').textContent.trim(); fileBase = 'sample'; chosen = {}; current = 0; render(); });
})();
