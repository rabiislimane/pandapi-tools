(function () {
  'use strict';
  var P = window.Pandapi, D = window.PandapiDocx, $ = P.$;
  var input = $('#word-in'), output = $('#md-out'), summary = $('#summary'), status = $('#status'), pick = $('#file-pick');
  var opt = { images: $('#opt-images'), front: $('#opt-front'), underline: $('#opt-underline') };
  var results = [], current = 0, pasted = null, files = null, timer = null;

  function options() { return { images: opt.images.value, frontMatter: opt.front.checked, underline: opt.underline.checked }; }
  function plural(n, one, many) { return n.toLocaleString() + ' ' + (n === 1 ? one : many); }
  function escapeHtml(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  function describe(st) {
    var parts = [plural(st.words, 'word', 'words')];
    if (st.headings) parts.push(plural(st.headings, 'heading', 'headings'));
    if (st.tables) parts.push(plural(st.tables, 'table', 'tables'));
    if (st.images) parts.push(plural(st.images, 'image', 'images'));
    if (st.footnotes) parts.push(plural(st.footnotes, 'footnote', 'footnotes'));
    return parts.join(', ');
  }

  function show() {
    var r = results[current];
    output.value = r ? r.markdown : '';
    var any = results.length > 0;
    ['#btn-md', '#btn-copy'].forEach(function (s) { $(s).disabled = !r; });
    var imgs = results.reduce(function (n, x) { return n + (x.images ? x.images.length : 0); }, 0);
    $('#btn-zip').hidden = !(results.length > 1 || imgs);
    $('#btn-zip').disabled = !any;
    $('#btn-zip').textContent = results.length > 1 ? 'Download all (.zip)' : 'Download .zip (Markdown + images)';
    pick.hidden = results.length < 2;
    if (results.length > 1) {
      pick.innerHTML = results.map(function (x, i) { return '<option value="' + i + '">' + escapeHtml(x.name) + (x.error ? ' (failed)' : '') + '</option>'; }).join('');
      pick.value = String(current);
    }
    var note = $('#file-note2');
    if (!r) { note.textContent = ''; return; }
    var bits = [];
    if (r.stats) bits.push(describe(r.stats));
    if (r.stats && r.stats.htmlTables) bits.push(plural(r.stats.htmlTables, 'table has', 'tables have') + ' merged cells, so ' + (r.stats.htmlTables === 1 ? 'it stays' : 'they stay') + ' an HTML table (Markdown tables can\'t merge cells)');
    if (r.images && r.images.length) bits.push('images are saved in the .zip under images/');
    if (r.unreadableImages) bits.push(plural(r.unreadableImages, 'pasted image was', 'pasted images were') + ' left out: browsers can\'t read images copied from Word. Drop the .docx file instead to get them');
    if (r.messages && r.messages.length) bits.push('Notes from the document: ' + r.messages.slice(0, 3).join('; '));
    if (r.error) bits = [r.error];
    note.textContent = bits.join('. ') + (bits.length ? '.' : '');
  }

  function convertText() {
    var html = pasted;
    var text = input.value;
    if (!html && !text.trim()) { results = []; show(); P.setStatus(summary, ''); return; }
    if (!html) html = /<(p|div|h[1-6]|ul|ol|table|br|strong|b|em|a)\b/i.test(text) ? text : text.split(/\n{2,}/).map(function (p) { return '<p>' + escapeHtml(p).replace(/\n/g, '<br>') + '</p>'; }).join('');
    var t0 = performance.now();
    var r;
    try { r = D.convertPasted(html, options()); } catch (e) { results = []; show(); P.setStatus(summary, 'Could not convert this: ' + e.message, 'error'); return; }
    r.name = 'document.md';
    results = [r]; current = 0; show();
    var from = r.source === 'word' ? 'Word' : r.source === 'google-docs' ? 'Google Docs' : pasted ? 'the pasted page' : 'your text';
    P.setStatus(summary, 'Converted from ' + from + ' in ' + Math.round(performance.now() - t0) + ' ms: ' + describe(r.stats) + '. Nothing was uploaded.', 'ok');
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(convertText, 250); }

  function convertFiles(list) {
    var t0 = performance.now(), o = options(), used = {};
    P.setStatus(summary, 'Converting ' + plural(list.length, 'file', 'files') + '...');
    var out = [];
    return list.reduce(function (chain, f) {
      return chain.then(function () { return f.arrayBuffer(); }).then(function (buf) {
        var base = D.slug(f.name), k = 2;
        while (used[base]) base = D.slug(f.name) + '-' + k++;
        used[base] = true;
        return D.convertDocx(new Uint8Array(buf), base + '.docx', o).then(function (r) { r.source = f.name; out.push(r); });
      }).catch(function (e) { out.push({ name: f.name, error: f.name + ': ' + e.message, markdown: '' }); });
    }, Promise.resolve()).then(function () {
      results = out; current = 0;
      var firstOk = out.findIndex(function (r) { return !r.error; });
      if (firstOk > 0) current = firstOk;
      show();
      var ok = out.filter(function (r) { return !r.error; }), bad = out.length - ok.length;
      if (!ok.length) { P.setStatus(summary, out.map(function (r) { return r.error; }).join(' '), 'error'); return; }
      var words = ok.reduce(function (n, r) { return n + r.stats.words; }, 0), imgs = ok.reduce(function (n, r) { return n + r.images.length; }, 0);
      P.setStatus(summary, 'Converted ' + plural(ok.length, 'document', 'documents') + ' (' + plural(words, 'word', 'words') + (imgs ? ', ' + plural(imgs, 'image', 'images') : '') + ') in ' +
        Math.round(performance.now() - t0) + ' ms. Nothing was uploaded.' + (bad ? ' ' + plural(bad, 'file', 'files') + ' failed: ' + out.filter(function (r) { return r.error; }).map(function (r) { return r.error; }).join(' ') : ''), bad ? 'error' : 'ok');
    });
  }

  function zip() {
    var enc = new TextEncoder(), z = {};
    results.forEach(function (r) {
      if (r.error) return;
      z[r.name] = enc.encode(r.markdown);
      (r.images || []).forEach(function (im) { z[im.name] = im.bytes; });
    });
    return window.fflate.zipSync(z, { level: 6 });
  }

  $('#btn-md').addEventListener('click', function () {
    var r = results[current];
    if (!r) return;
    P.downloadText(r.markdown, r.name, 'text/markdown;charset=utf-8');
    P.setStatus(status, 'Downloaded ' + r.name + (r.images && r.images.length ? '. Its images are only in the .zip download.' : '.'), 'ok');
  });
  $('#btn-zip').addEventListener('click', function () {
    var ok = results.filter(function (r) { return !r.error; });
    if (!ok.length) return;
    var name = ok.length === 1 ? ok[0].name.replace(/\.md$/, '') + '.zip' : 'markdown-' + ok.length + '-documents.zip';
    P.downloadBlob(new Blob([zip()], { type: 'application/zip' }), name);
    P.setStatus(status, 'Downloaded ' + name + ': ' + plural(ok.length, 'Markdown file', 'Markdown files') + ' and their images.', 'ok');
  });
  $('#btn-copy').addEventListener('click', function () {
    P.copyText(output.value).then(function (ok) { P.setStatus(status, ok ? 'Copied the Markdown.' : 'Copy failed: select the text and press Ctrl+C.', ok ? 'ok' : 'error'); });
  });
  pick.addEventListener('change', function () { current = Number(pick.value); show(); });

  // Rich paste: take the clipboard's HTML so headings, lists, bold, links and tables come along.
  input.addEventListener('paste', function (e) {
    var html = e.clipboardData && e.clipboardData.getData('text/html');
    if (!html) return;
    e.preventDefault();
    pasted = html; files = null;
    input.value = e.clipboardData.getData('text/plain') || '';
    $('#paste-note').textContent = 'Formatting read from the clipboard. Typing here switches back to plain text.';
    convertText();
  });
  input.addEventListener('input', function () { pasted = null; files = null; $('#paste-note').textContent = ''; schedule(); });
  [opt.images, opt.front, opt.underline].forEach(function (el) {
    el.addEventListener('change', function () { if (files) convertFiles(files); else convertText(); });
  });

  P.setupDrop($('#drop'), $('#file-in'), function (list) {
    var docs = list.filter(function (f) { return /\.(docx|docm|dotx|doc)$/i.test(f.name); });
    if (!docs.length) { P.setStatus(summary, 'Drop Word documents (.docx).', 'error'); return; }
    files = docs; pasted = null; input.value = ''; $('#paste-note').textContent = '';
    convertFiles(docs);
  });

  $('#btn-clear').addEventListener('click', function () { input.value = ''; pasted = null; files = null; results = []; show(); P.setStatus(summary, ''); status.textContent = ''; $('#paste-note').textContent = ''; input.focus(); });
  $('#btn-sample').addEventListener('click', function () {
    status.textContent = '';
    fetch('sample.docx').then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.blob(); }).then(function (b) {
      var f = new File([b], 'sample.docx');
      files = [f]; pasted = null; input.value = ''; $('#paste-note').textContent = '';
      return convertFiles(files);
    }).catch(function (e) { P.setStatus(summary, 'Could not load the sample: ' + e.message, 'error'); });
  });
  show();
})();
