(function () {
  'use strict';
  var P = window.Pandapi, M = window.PandapiEmails, T = window.PandapiTables, J = window.PandapiJson, C = window.PandapiCsvJson, $ = P.$;
  var input = $('#emails-in'), summary = $('#summary'), status = $('#status'), preview = $('#preview'), note = $('#preview-note');
  var opt = { rich: $('#opt-rich'), dedupe: $('#opt-dedupe'), deob: $('#opt-deob'), lower: $('#opt-lower') };
  var drop = { personal: $('#f-personal'), role: $('#f-role'), free: $('#f-free'), noreply: $('#f-noreply') };
  var fQuery = $('#f-q'), fSort = $('#f-sort'), delim = $('#opt-delim'), sep = $('#opt-sep');
  var files = null, fileBase = 'emails', result = null, timer = null, SHOW = 200, pasteNames = null;
  var buttons = ['#btn-xlsx', '#btn-csv', '#btn-copy-list', '#btn-copy'].map(function (s) { return $(s); });
  var pdfLib = window.pdfjsLib;
  if (pdfLib) pdfLib.GlobalWorkerOptions.workerSrc = '../vendor/pdf.worker.min.js';

  function options() { return { dedupe: opt.dedupe.checked, deobfuscate: opt.deob.checked, lowercase: opt.lower.checked }; }
  function filters() {
    return { drop: { personal: !drop.personal.checked, role: !drop.role.checked, 'free mailbox': !drop.free.checked, 'no-reply': !drop.noreply.checked },
      query: fQuery.value, sort: fSort.value };
  }
  function plural(n, one, many) { return n.toLocaleString() + ' ' + (n === 1 ? one : many); }

  function render() {
    var src = files || (input.value.trim() ? [pastedSource()] : null);
    status.textContent = '';
    if (!src) { result = null; draw(); P.setStatus(summary, ''); return; }
    var t0 = performance.now();
    try { result = M.extract(src, options()); } catch (e) { result = null; draw(); P.setStatus(summary, 'Could not read this input: ' + e.message, 'error'); return; }
    draw();
    if (!result.unique) {
      P.setStatus(summary, 'No email addresses found. Paste text, a page\'s HTML, a contact list or an email thread, or drop files (PDF, Word, Excel, CSV, .eml, .vcf, .html).', 'error');
      return;
    }
    var c = result.counts, parts = [];
    if (c.personal) parts.push(plural(c.personal, 'personal', 'personal'));
    if (c.role) parts.push(plural(c.role, 'role address', 'role addresses'));
    if (c['free mailbox']) parts.push(plural(c['free mailbox'], 'free mailbox', 'free mailboxes'));
    if (c['no-reply']) parts.push(plural(c['no-reply'], 'no-reply', 'no-reply'));
    var msg = plural(result.unique, 'unique address', 'unique addresses') +
      (result.total !== result.unique ? ' (' + result.total.toLocaleString() + ' in total)' : '') + ' from ' +
      (files ? plural(files.length, 'file', 'files') : 'your text') + ': ' + parts.join(', ') + '. ' +
      plural(result.domains.rows.length, 'domain', 'domains') + ', ' + Math.round(performance.now() - t0) + ' ms. Nothing was uploaded.';
    var skipped = files && files.skipped && files.skipped.length;
    if (skipped) msg += ' Skipped: ' + files.skipped.join('; ') + '.';
    P.setStatus(summary, msg, skipped ? 'error' : 'ok');
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 200); }

  function pastedSource() {
    var s = M.textSource('', input.value);
    if (pasteNames) s.names = Object.assign({}, s.names || {}, pasteNames);
    return s;
  }

  function view() { return result ? M.filter(result.rows, filters()) : []; }

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
        var td = tr.insertCell();
        td.textContent = r[c] == null ? '' : r[c];
        if (c === 'Count') td.className = 'num';
      });
    });
    note.textContent = rows.length > SHOW ? 'Showing the first ' + SHOW + ' of ' + rows.length.toLocaleString() + ' addresses. Downloads include all of them.' :
      plural(rows.length, 'address', 'addresses') + (rows.length < result.rows.length ? ' match the filters.' : '.');
    var dl = $('#domains');
    dl.innerHTML = '';
    result.domains.rows.slice(0, 12).forEach(function (d) {
      var li = document.createElement('li'); li.textContent = d.Domain + ' ' + d.Emails.toLocaleString(); dl.appendChild(li);
    });
    $('#domains-more').textContent = result.domains.rows.length > 12 ? '+ ' + (result.domains.rows.length - 12).toLocaleString() + ' more in the Excel file' : '';
  }

  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || 'emails'; }

  $('#btn-xlsx').addEventListener('click', function () {
    var rows = view();
    if (!rows.length) return;
    var sheets = [{ name: 'Emails', rows: rows, columns: result.columns }];
    if (result.domains.rows.length) sheets.push({ name: 'Domains', rows: result.domains.rows, columns: result.domains.columns });
    var wb = T.workbook(sheets, { numbers: true }), enc = new TextEncoder(), zip = {};
    Object.keys(wb.files).forEach(function (k) { zip[k] = enc.encode(wb.files[k]); });
    P.downloadBlob(new Blob([window.fflate.zipSync(zip, { level: 6 })], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), fileBase + '.xlsx');
    P.setStatus(status, wb.droppedRows ? 'Downloaded, but ' + wb.droppedRows.toLocaleString() + ' rows past Excel\'s limit were left out (use CSV).' :
      'Excel file downloaded: ' + plural(rows.length, 'address', 'addresses') + ' and a Domains sheet.', wb.droppedRows ? 'error' : 'ok');
  });
  $('#btn-csv').addEventListener('click', function () {
    var rows = view();
    if (!rows.length) return;
    var d = delim.value === 'tab' ? '\t' : delim.value;
    P.downloadText(J.toCSV(rows, result.columns, { delimiter: d, protectFormulas: true }), fileBase + (d === '\t' ? '.tsv' : '.csv'), 'text/csv;charset=utf-8');
    P.setStatus(status, 'CSV downloaded: ' + plural(rows.length, 'address', 'addresses') + '.', 'ok');
  });
  $('#btn-copy-list').addEventListener('click', function () {
    var rows = view();
    P.copyText(M.joinList(rows, sep.value)).then(function (ok) {
      var how = sep.value === 'lines' ? 'one per line' : sep.value === 'comma' ? 'separated by commas' : 'separated by semicolons (ready for Outlook\'s To box)';
      P.setStatus(status, ok ? 'Copied ' + plural(rows.length, 'address', 'addresses') + ', ' + how + '.' : 'Copy failed: download the CSV instead.', ok ? 'ok' : 'error');
    });
  });
  $('#btn-copy').addEventListener('click', function () {
    var rows = view();
    P.copyText(T.toTSV({ columns: result.columns, rows: rows })).then(function (ok) {
      P.setStatus(status, ok ? 'Copied the table. Paste it into Excel or Google Sheets.' : 'Copy failed: download the CSV instead.', ok ? 'ok' : 'error');
    });
  });

  function resetFiles() { files = null; fileBase = 'emails'; fQuery.value = ''; $('#file-note').textContent = ''; }
  input.addEventListener('input', function () { resetFiles(); pasteNames = null; schedule(); });
  ['dedupe', 'deob', 'lower'].forEach(function (k) { opt[k].addEventListener('change', render); });
  Object.keys(drop).forEach(function (k) { drop[k].addEventListener('change', draw); });
  fSort.addEventListener('change', draw);
  fQuery.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(draw, 150); });

  // Copy part of a web page or an email: mailto links often hide the address behind a name, so keep the clipboard's HTML.
  input.addEventListener('paste', function (e) {
    if (!opt.rich.checked || !e.clipboardData) return;
    var html = e.clipboardData.getData('text/html');
    if (!html || !/mailto:/i.test(html)) return;
    e.preventDefault();
    var h = M.fromHtml(html.replace(/<!--StartFragment-->|<!--EndFragment-->/g, ''));
    var start = input.selectionStart, end = input.selectionEnd, v = input.value;
    input.value = v.slice(0, start) + h.text.replace(/[ \t]+/g, ' ').replace(/\n\s*\n+/g, '\n').trim() + v.slice(end);
    pasteNames = Object.assign({}, pasteNames || {}, h.names);
    resetFiles(); render();
  });

  // ---------- files ----------
  function ext(name) { var m = /\.([a-z0-9]+)$/i.exec(name); return m ? m[1].toLowerCase() : ''; }
  var TEXT_EXT = /^(txt|csv|tsv|md|json|eml|mbox|vcf|html?|xhtml|xml|log|ics|ldif|rtf|js|sql|yaml|yml)$/;

  function pdfLines(page) {
    // group text items into lines by their y position; keep pieces of one address together
    var items = page.items.slice().sort(function (a, b) { return a.y - b.y || a.x - b.x; }), lines = [], cur = null;
    items.forEach(function (it) {
      if (cur && Math.abs(it.y - cur.y) <= Math.max(2, it.size * 0.45)) {
        var gap = it.x - cur.end;
        cur.text += (gap > it.size * 0.2 ? ' ' : '') + it.str;
        cur.end = it.x + it.w;
      } else {
        cur = { y: it.y, text: it.str, end: it.x + it.w };
        lines.push(cur);
      }
    });
    return lines.map(function (l) { return l.text; }).join('\n');
  }

  function readOne(f) {
    var e = ext(f.name);
    if (e === 'pdf' || f.type === 'application/pdf') {
      if (!pdfLib) return Promise.reject(new Error('the PDF reader did not load'));
      return f.arrayBuffer().then(function (buf) {
        return window.PandapiPdf.extractPages(pdfLib, new Uint8Array(buf));
      }).then(function (r) {
        var parts = r.pages.map(function (p, i) { return { text: pdfLines(p), where: 'page ' + (i + 1) }; });
        if (!parts.some(function (p) { return p.text.trim(); })) throw new Error('this PDF has no text layer (a scan)');
        return { name: f.name, file: true, parts: parts };
      });
    }
    if (e === 'docx') {
      return f.arrayBuffer().then(function (buf) {
        return { name: f.name, file: true, parts: [{ text: M.docxText(new Uint8Array(buf), window.fflate.unzipSync), where: '' }], lines: false };
      });
    }
    if (e === 'xlsx' || e === 'xlsm') {
      return f.arrayBuffer().then(function (buf) {
        var wb = C.readXlsx(new Uint8Array(buf), window.fflate.unzipSync), parts = [];
        wb.sheets.forEach(function (sh) {
          sh.rows.forEach(function (row, i) {
            var t = row.filter(function (v) { return v !== '' && v != null; }).join('\t');
            if (t.indexOf('@') >= 0 || /\[at\]|\(at\)/i.test(t)) parts.push({ text: t, where: sh.name + ' row ' + (i + 1) });
          });
        });
        return { name: f.name, file: true, parts: parts };
      });
    }
    if (e === 'doc' || e === 'xls') return Promise.reject(new Error('old ' + e.toUpperCase() + ' format: save it as .' + e + 'x first'));
    if (TEXT_EXT.test(e) || /^text\/|json|xml/.test(f.type) || !e) {
      return f.text().then(function (t) {
        var s = M.textSource(f.name, t, e === 'eml' || e === 'mbox' ? 'eml' : /^(html?|xhtml)$/.test(e) ? 'html' : (/^(txt|csv|tsv|md|vcf|log)$/.test(e) ? 'text' : undefined));
        s.file = true;
        return s;
      });
    }
    return Promise.reject(new Error('this file type can\'t be read'));
  }

  P.setupDrop($('#drop'), $('#file-in'), function (list) {
    if (!list.length) return;
    P.setStatus(summary, 'Reading ' + plural(list.length, 'file', 'files') + '...');
    var skipped = [];
    Promise.all(list.map(function (f) {
      return readOne(f).catch(function (err) { skipped.push(f.name + ' (' + String(err.message || err).replace(/\.$/, '') + ')'); return null; });
    })).then(function (loaded) {
      loaded = loaded.filter(Boolean);
      input.value = ''; fQuery.value = ''; pasteNames = null;
      files = loaded; files.skipped = skipped;
      fileBase = list.length === 1 ? slug('emails-' + P.baseName(list[0].name)) : 'emails-' + list.length + '-files';
      $('#file-note').textContent = list.length === 1 ? 'Read ' + list[0].name + ' (' + P.formatBytes(list[0].size) + ').' :
        'Read ' + plural(loaded.length, 'file', 'files') + '; the Source column says where each address was found.';
      if (!loaded.length) { files = null; result = null; draw(); P.setStatus(summary, 'Could not read: ' + skipped.join('; ') + '.', 'error'); return; }
      render();
    });
  });

  $('#btn-clear').addEventListener('click', function () { input.value = ''; pasteNames = null; resetFiles(); render(); input.focus(); });
  $('#btn-sample').addEventListener('click', function () {
    input.value = document.getElementById('sample-text').textContent.trim(); pasteNames = null; resetFiles(); fileBase = 'sample-emails'; render();
  });
})();
