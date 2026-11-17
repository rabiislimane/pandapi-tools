(function () {
  'use strict';
  var P = window.Pandapi, C = window.PandapiPdf, $ = P.$;
  var lib = window.pdfjsLib;
  lib.GlobalWorkerOptions.workerSrc = '../vendor/pdf.worker.min.js';
  var output = $('#md-out'), status = $('#status'), stats = $('#stats'), list = $('#file-list');
  var optMarkers = $('#opt-markers'), optKeep = $('#opt-keep');
  var results = [];   // { name, pages, md, stats }
  var lastFiles = [];
  var busy = false;

  function opts() { return { pageMarkers: optMarkers.checked, keepHeadersFooters: optKeep.checked }; }

  function showResult(r) {
    output.value = r.md;
    var words = (r.md.match(/\S+/g) || []).length;
    stats.textContent = r.name + ' · ' + r.stats.pages + ' page' + (r.stats.pages === 1 ? '' : 's') + ' · ' + words.toLocaleString() + ' words · ~' + P.estimateTokens(r.md).toLocaleString() + ' tokens';
  }

  function setButtons() {
    var any = results.some(function (r) { return r.md; });
    $('#btn-copy').disabled = !output.value;
    $('#btn-download').disabled = !any;
    $('#btn-download').textContent = results.filter(function (r) { return r.md; }).length > 1 ? 'Download all (.zip)' : 'Download .md';
  }

  function convertAll(files) {
    if (busy) return;
    busy = true; results = []; list.innerHTML = ''; output.value = ''; stats.textContent = ''; setButtons();
    var rows = files.map(function (f) {
      var li = document.createElement('li'), name = document.createElement('span'), meta = document.createElement('span');
      name.className = 'name'; meta.className = 'meta'; name.textContent = f.name; meta.textContent = 'waiting';
      li.appendChild(name); li.appendChild(meta); list.appendChild(li);
      return meta;
    });
    var done = 0, failed = 0, scanned = 0;
    function one(i) {
      if (i >= files.length) {
        busy = false;
        var ok = results.filter(function (r) { return r.md; });
        if (ok.length) showResult(ok[0]);
        setButtons();
        var msg = done + ' of ' + files.length + ' converted in your browser';
        if (failed) msg += ', ' + failed + ' could not be read';
        if (scanned) msg += '. ' + scanned + ' look' + (scanned === 1 ? 's' : '') + ' scanned (no text layer): this tool has no OCR';
        P.setStatus(status, msg + '.', failed || scanned ? 'error' : 'ok');
        return;
      }
      var f = files[i];
      rows[i].textContent = 'reading…';
      P.setStatus(status, 'Converting ' + f.name + ' (' + (i + 1) + ' of ' + files.length + ')…');
      f.arrayBuffer().then(function (buf) {
        return C.extractPages(lib, new Uint8Array(buf), function (p, n) { rows[i].textContent = 'page ' + p + ' of ' + n; });
      }).then(function (ex) {
        var r = C.pagesToMarkdown(ex.pages, opts());
        var title = ex.info && ex.info.Title && String(ex.info.Title).trim();
        results.push({ name: f.name, md: r.markdown, stats: r.stats, title: title });
        done++;
        if (r.stats.likelyScanned) { scanned++; rows[i].textContent = 'no text found (scanned?)'; }
        else rows[i].textContent = r.stats.pages + ' pages · ~' + P.estimateTokens(r.markdown).toLocaleString() + ' tokens';
        if (results.length === 1 && r.markdown.trim()) { showResult(results[0]); setButtons(); }
      }).catch(function (e) {
        failed++;
        var msg = /password/i.test(e && e.name + ' ' + e.message) ? 'password-protected' : 'not a readable PDF';
        rows[i].textContent = msg;
        results.push({ name: f.name, md: '', stats: null });
      }).then(function () { one(i + 1); });
    }
    one(0);
  }

  P.setupDrop($('#drop'), $('#file-in'), function (files) {
    var pdfs = files.filter(function (f) { return /\.pdf$/i.test(f.name) || f.type === 'application/pdf'; });
    if (!pdfs.length) { P.setStatus(status, 'Please choose PDF files.', 'error'); return; }
    lastFiles = pdfs;
    convertAll(pdfs);
  });
  [optMarkers, optKeep].forEach(function (el) { el.addEventListener('change', function () { if (lastFiles.length) convertAll(lastFiles); }); });

  $('#btn-copy').addEventListener('click', function () {
    P.copyText(output.value).then(function (ok) { P.setStatus(status, ok ? 'Markdown copied.' : 'Copy failed: select the text and copy it.', ok ? 'ok' : 'error'); });
  });
  $('#btn-download').addEventListener('click', function () {
    var ok = results.filter(function (r) { return r.md; });
    if (!ok.length) return;
    if (ok.length === 1) P.downloadText(ok[0].md, P.baseName(ok[0].name) + '.md', 'text/markdown;charset=utf-8');
    else P.downloadBlob(P.zipFiles(ok.map(function (r) { return { name: P.baseName(r.name) + '.md', data: r.md }; })), 'pdf-markdown.zip');
  });
  $('#btn-sample').addEventListener('click', function () {
    P.setStatus(status, 'Loading the sample PDF…');
    fetch('sample.pdf').then(function (r) { if (!r.ok) throw new Error(r.status); return r.blob(); })
      .then(function (b) { var f = new File([b], 'sample.pdf', { type: 'application/pdf' }); lastFiles = [f]; convertAll([f]); })
      .catch(function () { P.setStatus(status, 'Could not load the sample.', 'error'); });
  });
})();
