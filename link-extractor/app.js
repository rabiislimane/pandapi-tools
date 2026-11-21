(function () {
  'use strict';
  var P = window.Pandapi, L = window.PandapiLinks, T = window.PandapiTables, J = window.PandapiJson, $ = P.$;
  var input = $('#links-in'), summary = $('#summary'), status = $('#status'), preview = $('#preview'), note = $('#preview-note');
  var opt = { base: $('#opt-base'), rich: $('#opt-rich'), images: $('#opt-images'), resources: $('#opt-resources'),
    dedupe: $('#opt-dedupe'), hash: $('#opt-hash'), tracking: $('#opt-tracking') };
  var fType = $('#f-type'), fQuery = $('#f-q'), fSort = $('#f-sort'), delim = $('#opt-delim');
  var files = null, fileBase = 'links', result = null, timer = null, SHOW = 200;
  var buttons = ['#btn-xlsx', '#btn-csv', '#btn-copy-urls', '#btn-copy'].map(function (s) { return $(s); });

  function options() {
    return { base: opt.base.value.trim(), images: opt.images.checked, resources: opt.resources.checked, dedupe: opt.dedupe.checked,
      stripHash: opt.hash.checked, stripTracking: opt.tracking.checked };
  }
  var KIND_NAME = { html: 'web page', text: 'text', sitemap: 'sitemap' };

  function render() {
    var src = files || (input.value.trim() ? input.value : null);
    status.textContent = '';
    if (!src) { result = null; draw(); P.setStatus(summary, ''); return; }
    var t0 = performance.now();
    try { result = L.extract(src, options()); } catch (e) { result = null; draw(); P.setStatus(summary, 'Could not read this input: ' + e.message, 'error'); return; }
    var types = Object.keys(result.counts).sort(function (a, b) { return result.counts[b] - result.counts[a]; });
    var keep = fType.value;
    fType.innerHTML = '<option value="all">All (' + result.unique.toLocaleString() + ')</option>' +
      types.map(function (t) { return '<option value="' + t.replace(/"/g, '&quot;') + '">' + t + ' (' + result.counts[t].toLocaleString() + ')</option>'; }).join('');
    fType.value = types.indexOf(keep) >= 0 ? keep : 'all';
    $('#sort-lastmod').hidden = result.kind !== 'sitemap';
    draw();
    if (!result.unique) {
      P.setStatus(summary, 'No links found. Paste a page\'s HTML (Ctrl+U on the page), copy part of a page, paste text with URLs, or paste a sitemap.xml.', 'error');
      return;
    }
    var msg = result.unique.toLocaleString() + ' unique ' + (result.unique === 1 ? 'link' : 'links') +
      (result.total !== result.unique ? ' (' + result.total.toLocaleString() + ' in total)' : '') + ' from ' +
      (files ? files.length + (files.length === 1 ? ' file' : ' files') : 'this ' + KIND_NAME[result.kind]) + ', ' +
      result.domains.rows.length.toLocaleString() + (result.domains.rows.length === 1 ? ' domain' : ' domains') + ', in ' + Math.round(performance.now() - t0) + ' ms. Nothing was uploaded.';
    if (result.broken) msg += ' The XML is not valid, so only the <loc> addresses were read.';
    P.setStatus(summary, msg, 'ok');
    var hint = $('#base-hint');
    hint.hidden = !(result.kind === 'html' && !result.base && result.counts.Relative);
    if (result.kind === 'html' && result.base && !opt.base.value) opt.base.placeholder = result.base + ' (found in the page)';
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 200); }

  function view() {
    if (!result) return [];
    return L.sortRows(L.filter(result.rows, fType.value, fQuery.value), fSort.value);
  }

  function draw() {
    preview.innerHTML = '';
    var rows = view();
    $('#results-wrap').hidden = !result || !result.unique;
    buttons.forEach(function (b) { b.disabled = !rows.length; });
    if (!result || !result.unique) return;
    var cols = result.columns;
    var thead = preview.createTHead().insertRow();
    cols.forEach(function (c) { var th = document.createElement('th'); th.textContent = c; thead.appendChild(th); });
    var tb = preview.createTBody();
    rows.slice(0, SHOW).forEach(function (r) {
      var tr = tb.insertRow();
      cols.forEach(function (c) {
        var td = tr.insertCell(), v = r[c];
        if (c === 'URL' && /^https?:\/\//i.test(v)) {
          var a = document.createElement('a'); a.href = v; a.textContent = v; a.rel = 'noopener noreferrer nofollow'; a.target = '_blank'; td.appendChild(a);
        } else td.textContent = v == null ? '' : v;
        if (c === 'Count') td.className = 'num';
      });
    });
    note.textContent = rows.length > SHOW ? 'Showing the first ' + SHOW + ' of ' + rows.length.toLocaleString() + ' links. Downloads include all of them.' :
      rows.length + (rows.length === 1 ? ' link' : ' links') + (rows.length < result.unique ? ' match the filter.' : '.');
    var dl = $('#domains');
    dl.innerHTML = '';
    result.domains.rows.slice(0, 12).forEach(function (d) {
      var li = document.createElement('li'); li.textContent = d.Domain + ' ' + d.Links.toLocaleString(); dl.appendChild(li);
    });
    $('#domains-more').textContent = result.domains.rows.length > 12 ? '+ ' + (result.domains.rows.length - 12).toLocaleString() + ' more in the Excel file' : '';
  }

  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || 'links'; }
  function name() {
    if (files) return fileBase;
    if (result && result.base) { try { return slug('links-' + new URL(result.base).hostname.replace(/^www\./, '')); } catch (e) { /* fall through */ } }
    return fileBase;
  }

  $('#btn-xlsx').addEventListener('click', function () {
    var rows = view();
    if (!rows.length) return;
    var sheets = [{ name: 'Links', rows: rows, columns: result.columns }];
    if (result.domains.rows.length) sheets.push({ name: 'Domains', rows: result.domains.rows, columns: result.domains.columns });
    var wb = T.workbook(sheets, { numbers: true }), enc = new TextEncoder(), zip = {};
    Object.keys(wb.files).forEach(function (k) { zip[k] = enc.encode(wb.files[k]); });
    P.downloadBlob(new Blob([window.fflate.zipSync(zip, { level: 6 })], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), name() + '.xlsx');
    P.setStatus(status, wb.droppedRows ? 'Downloaded, but ' + wb.droppedRows.toLocaleString() + ' rows past Excel\'s limit were left out (use CSV).' :
      'Excel file downloaded: ' + rows.length.toLocaleString() + ' links' + (sheets.length > 1 ? ' and a Domains sheet.' : '.'), wb.droppedRows ? 'error' : 'ok');
  });
  $('#btn-csv').addEventListener('click', function () {
    var rows = view();
    if (!rows.length) return;
    var d = delim.value === 'tab' ? '\t' : delim.value;
    P.downloadText(J.toCSV(rows, result.columns, { delimiter: d, protectFormulas: true }), name() + (d === '\t' ? '.tsv' : '.csv'), 'text/csv;charset=utf-8');
    P.setStatus(status, 'CSV downloaded: ' + rows.length.toLocaleString() + ' links.', 'ok');
  });
  $('#btn-copy-urls').addEventListener('click', function () {
    var rows = view();
    P.copyText(rows.map(function (r) { return r.URL; }).join('\n') + '\n').then(function (ok) {
      P.setStatus(status, ok ? 'Copied ' + rows.length.toLocaleString() + ' URLs, one per line.' : 'Copy failed: download the CSV instead.', ok ? 'ok' : 'error');
    });
  });
  $('#btn-copy').addEventListener('click', function () {
    var rows = view();
    P.copyText(T.toTSV({ columns: result.columns, rows: rows })).then(function (ok) {
      P.setStatus(status, ok ? 'Copied the table. Paste it into Excel or Google Sheets.' : 'Copy failed: download the CSV instead.', ok ? 'ok' : 'error');
    });
  });

  // New input: start with no search, so nothing is hidden by an old query.
  function resetFiles() { files = null; fileBase = 'links'; fQuery.value = ''; $('#file-note').textContent = ''; }
  input.addEventListener('input', function () { resetFiles(); schedule(); });
  opt.base.addEventListener('input', schedule);
  ['images', 'resources', 'dedupe', 'hash', 'tracking'].forEach(function (k) { opt[k].addEventListener('change', render); });
  [fType, fSort].forEach(function (el) { el.addEventListener('change', draw); });
  fQuery.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(draw, 150); });

  // Paste part of a web page: take the clipboard's HTML so the links come with it (plain text would lose them).
  input.addEventListener('paste', function (e) {
    if (!opt.rich.checked || !e.clipboardData) return;
    var html = e.clipboardData.getData('text/html');
    if (!html || !/<a\s[^>]*href/i.test(html)) return;
    e.preventDefault();
    input.value = html.replace(/<!--StartFragment-->|<!--EndFragment-->/g, '');
    resetFiles(); render();
  });

  P.setupDrop($('#drop'), $('#file-in'), function (list) {
    var ok = list.filter(function (f) { return /\.(html?|xhtml|xml|txt|md|csv|json)$/i.test(f.name) || /html|xml|text/.test(f.type); });
    if (!ok.length) { P.setStatus(summary, 'Drop saved web pages (.html), a sitemap (.xml) or text files.', 'error'); return; }
    Promise.all(ok.map(function (f) { return f.text().then(function (t) { return { name: f.name, text: t }; }); })).then(function (loaded) {
      files = loaded; input.value = ''; fQuery.value = '';
      fileBase = loaded.length === 1 ? slug('links-' + P.baseName(loaded[0].name)) : 'links-' + loaded.length + '-files';
      $('#file-note').textContent = loaded.length === 1 ? 'Reading ' + loaded[0].name + ' (' + P.formatBytes(ok[0].size) + ').' : 'Reading ' + loaded.length + ' files; the Source column says where each link was found.';
      render();
    });
  });

  $('#btn-clear').addEventListener('click', function () { input.value = ''; opt.base.value = ''; opt.base.placeholder = 'https://example.com/page'; resetFiles(); render(); input.focus(); });
  $('#btn-sample').addEventListener('click', function () {
    input.value = document.getElementById('sample-html').textContent.trim(); opt.base.value = ''; resetFiles(); fileBase = 'sample'; render();
  });
})();
