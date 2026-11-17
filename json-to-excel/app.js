(function () {
  'use strict';
  var P = window.Pandapi, J = window.PandapiJson, $ = P.$;
  var input = $('#json-in'), status = $('#status'), summary = $('#summary'), table = $('#preview');
  var arrays = $('#opt-arrays'), explode = $('#opt-explode'), explodeWrap = $('#explode-wrap'), numeric = $('#opt-numeric'),
    delim = $('#opt-delim'), protect = $('#opt-protect');
  var state = null, fileBase = 'data', timer = null, bigText = null;

  function arrayPaths(records) {
    var seen = {}, order = [];
    records.slice(0, 300).forEach(function (r) {
      (function walk(o, p) {
        Object.keys(o).forEach(function (k) {
          var v = o[k], q = p ? p + '.' + k : k;
          if (Array.isArray(v) && v.some(function (x) { return x && typeof x === 'object' && !Array.isArray(x); })) { if (!seen[q]) { seen[q] = 1; order.push(q); } }
          else if (v && typeof v === 'object' && !Array.isArray(v)) walk(v, q);
        });
      })(r, '');
    });
    return order;
  }

  function render() {
    var text = bigText != null ? bigText : input.value;
    state = null; table.innerHTML = ''; summary.textContent = '';
    setButtons(false);
    if (!text.trim()) { P.setStatus(status, ''); return; }
    var parsed, found;
    try { parsed = J.parseText(text); found = J.findRecords(parsed.data); }
    catch (e) { P.setStatus(status, e.message, 'error'); return; }
    var paths = arrayPaths(found.records);
    var keep = explode.value;
    explode.innerHTML = '';
    paths.forEach(function (p) { var o = document.createElement('option'); o.value = p; o.textContent = p; explode.appendChild(o); });
    if (keep && paths.indexOf(keep) >= 0) explode.value = keep;
    explodeWrap.hidden = arrays.value !== 'rows';
    if (arrays.value === 'rows' && !paths.length) P.setStatus(status, 'No list of objects to split into rows, so each record stays one row.');
    var flat = J.flatten(found.records, { arrays: arrays.value, explodePath: arrays.value === 'rows' ? (explode.value || null) : null });
    state = flat;
    summary.textContent = parsed.format + ' · records from ' + found.path + ' · ' + flat.rows.length.toLocaleString() + ' rows × ' + flat.columns.length.toLocaleString() + ' columns';
    if (flat.rows.length > J.MAX_ROWS) summary.textContent += ' · Excel holds 1,048,575 rows: use CSV for the rest';
    drawTable(flat);
    setButtons(flat.rows.length > 0 && flat.columns.length > 0);
    if (!(arrays.value === 'rows' && !paths.length)) P.setStatus(status, 'Ready. Download as Excel or CSV.', 'ok');
  }

  function drawTable(flat) {
    var max = 100, cols = flat.columns.slice(0, 60);
    var thead = '<thead><tr><th>#</th>' + cols.map(function (c) { return '<th title="' + esc(c) + '">' + esc(c) + '</th>'; }).join('') + '</tr></thead>';
    var body = flat.rows.slice(0, max).map(function (r, i) {
      return '<tr><td>' + (i + 1) + '</td>' + cols.map(function (c) { var v = r[c]; v = v == null ? '' : (typeof v === 'object' ? JSON.stringify(v) : String(v)); return '<td title="' + esc(v.slice(0, 500)) + '">' + esc(v.slice(0, 200)) + '</td>'; }).join('') + '</tr>';
    }).join('');
    table.innerHTML = thead + '<tbody>' + body + '</tbody>';
    if (flat.rows.length > max || flat.columns.length > cols.length) {
      table.insertAdjacentHTML('beforeend', '<caption class="sr-only">Preview of the first ' + Math.min(max, flat.rows.length) + ' rows</caption>');
    }
  }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function setButtons(on) { ['#btn-xlsx', '#btn-csv', '#btn-copy'].forEach(function (s) { $(s).disabled = !on; }); }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 200); }

  input.addEventListener('input', function () { fileBase = 'data'; bigText = null; input.placeholder = ''; schedule(); });
  [arrays, explode].forEach(function (el) { el.addEventListener('change', render); });

  $('#btn-xlsx').addEventListener('click', function () {
    if (!state) return;
    var parts = J.xlsxParts(state.rows, state.columns, { numericText: numeric.checked, sheetName: fileBase });
    var enc = new TextEncoder(), zip = {};
    Object.keys(parts.files).forEach(function (k) { zip[k] = enc.encode(parts.files[k]); });
    P.downloadBlob(new Blob([window.fflate.zipSync(zip, { level: 6 })], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), fileBase + '.xlsx');
    var notes = [];
    if (parts.droppedRows) notes.push(parts.droppedRows.toLocaleString() + ' rows past Excel\'s limit were left out (use CSV)');
    if (parts.droppedCols) notes.push(parts.droppedCols + ' columns past Excel\'s limit were left out');
    if (parts.truncatedCells) notes.push(parts.truncatedCells + ' very long cells were cut to Excel\'s 32,767 characters');
    P.setStatus(status, notes.length ? 'Downloaded, but ' + notes.join('; ') + '.' : 'Excel file downloaded.', notes.length ? 'error' : 'ok');
  });
  function csvText() { return J.toCSV(state.rows, state.columns, { delimiter: delim.value === 'tab' ? '\t' : delim.value, protectFormulas: protect.checked }); }
  $('#btn-csv').addEventListener('click', function () {
    if (!state) return;
    P.downloadText(csvText(), fileBase + (delim.value === 'tab' ? '.tsv' : '.csv'), 'text/csv;charset=utf-8');
    P.setStatus(status, 'CSV downloaded.', 'ok');
  });
  $('#btn-copy').addEventListener('click', function () {
    if (!state) return;
    P.copyText(csvText().replace(/^﻿/, '')).then(function (ok) { P.setStatus(status, ok ? 'CSV copied. Paste it into a sheet.' : 'Copy failed.', ok ? 'ok' : 'error'); });
  });
  $('#btn-sample').addEventListener('click', function () { bigText = null; input.value = document.getElementById('sample-json').textContent.trim(); fileBase = 'sample'; render(); });
  $('#btn-clear').addEventListener('click', function () { bigText = null; input.placeholder = ''; input.value = ''; render(); input.focus(); });

  P.setupDrop($('#drop'), $('#file-in'), function (files) {
    var f = files[0];
    P.setStatus(status, 'Reading ' + f.name + ' (' + P.formatBytes(f.size) + ')…');
    f.text().then(function (t) {
      fileBase = P.baseName(f.name);
      // Very large files are not echoed into the text box (slow); they are converted directly.
      if (t.length > 5e6) { bigText = t; input.value = ''; input.placeholder = f.name + ' loaded (' + P.formatBytes(f.size) + '). Converted directly; type here to start over.'; render(); }
      else { bigText = null; input.value = t; render(); }
    });
  });
  render();
})();
