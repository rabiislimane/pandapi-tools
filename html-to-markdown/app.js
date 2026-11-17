(function () {
  'use strict';
  var P = window.Pandapi, C = window.PandapiHtmlToMd, $ = P.$;
  var input = $('#html-in'), output = $('#md-out'), status = $('#status'), stats = $('#stats');
  var opt = {
    mainContent: $('#opt-main'), dropImages: $('#opt-noimg'), referenceLinks: $('#opt-reflinks'),
    frontMatter: $('#opt-fm'), richPaste: $('#opt-rich'), baseUrl: $('#opt-base')
  };
  var timer = null;

  function options() {
    return { mainContent: opt.mainContent.checked, dropImages: opt.dropImages.checked, referenceLinks: opt.referenceLinks.checked,
      frontMatter: opt.frontMatter.checked, baseUrl: opt.baseUrl.value };
  }

  function run() {
    var html = input.value;
    if (!html.trim()) { output.value = ''; stats.textContent = ''; P.setStatus(status, ''); return; }
    try {
      var t0 = performance.now();
      var r = C.convert(html, options());
      output.value = r.markdown;
      var words = (r.markdown.match(/\S+/g) || []).length;
      stats.textContent = words.toLocaleString() + ' words · ~' + P.estimateTokens(r.markdown).toLocaleString() + ' tokens';
      var msg = (r.usedReadability ? 'Main content kept, menus and footers dropped. ' : '') + (r.note || '');
      P.setStatus(status, (msg.trim() || 'Converted') + ' (' + Math.round(performance.now() - t0) + ' ms).', r.note ? '' : 'ok');
    } catch (e) {
      output.value = '';
      P.setStatus(status, 'Could not convert this HTML: ' + e.message, 'error');
    }
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(run, 150); }

  input.addEventListener('input', schedule);
  Object.keys(opt).forEach(function (k) { opt[k].addEventListener(k === 'baseUrl' ? 'input' : 'change', schedule); });

  // Paste from a web page: take the clipboard's HTML (formatting) instead of plain text.
  input.addEventListener('paste', function (e) {
    if (!opt.richPaste.checked || !e.clipboardData) return;
    var html = e.clipboardData.getData('text/html');
    if (!html) return;
    e.preventDefault();
    html = html.replace(/<!--StartFragment-->|<!--EndFragment-->/g, '');
    var start = input.selectionStart, end = input.selectionEnd;
    input.value = input.value.slice(0, start) + html + input.value.slice(end);
    input.selectionStart = input.selectionEnd = start + html.length;
    run();
  });

  $('#btn-copy').addEventListener('click', function () {
    if (!output.value) return;
    P.copyText(output.value).then(function (ok) { P.setStatus(status, ok ? 'Markdown copied.' : 'Copy failed: select the text and copy it.', ok ? 'ok' : 'error'); });
  });
  $('#btn-download').addEventListener('click', function () {
    if (!output.value) return;
    var r = C.convert(input.value, options());
    var name = (r.title ? r.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) : '') || 'converted';
    P.downloadText(output.value, name + '.md', 'text/markdown;charset=utf-8');
  });
  $('#btn-clear').addEventListener('click', function () { input.value = ''; run(); input.focus(); });
  $('#btn-sample').addEventListener('click', function () { input.value = document.getElementById('sample-html').textContent.trim(); run(); });

  // Batch: many .html files -> one .zip of .md files.
  var list = $('#batch-list'), batchStatus = $('#batch-status');
  P.setupDrop($('#drop'), $('#file-in'), function (files) {
    var htmlFiles = files.filter(function (f) { return /\.(html?|xhtml)$/i.test(f.name) || /html/.test(f.type); });
    if (!htmlFiles.length) { P.setStatus(batchStatus, 'Those files are not .html files.', 'error'); return; }
    list.innerHTML = '';
    P.setStatus(batchStatus, 'Converting ' + htmlFiles.length + ' file(s)…');
    Promise.all(htmlFiles.map(function (f) { return f.text().then(function (t) { return { file: f, text: t }; }); })).then(function (items) {
      var out = [], failed = 0;
      items.forEach(function (it) {
        var li = document.createElement('li'), name = document.createElement('span'), meta = document.createElement('span');
        name.className = 'name'; meta.className = 'meta'; name.textContent = it.file.name;
        try {
          var r = C.convert(it.text, options());
          out.push({ name: P.baseName(it.file.name) + '.md', data: r.markdown });
          meta.textContent = '~' + P.estimateTokens(r.markdown).toLocaleString() + ' tokens';
        } catch (e) { failed++; meta.textContent = 'failed: ' + e.message; }
        li.appendChild(name); li.appendChild(meta); list.appendChild(li);
      });
      if (!out.length) { P.setStatus(batchStatus, 'Nothing could be converted.', 'error'); return; }
      if (out.length === 1) P.downloadText(out[0].data, out[0].name, 'text/markdown;charset=utf-8');
      else P.downloadBlob(P.zipFiles(out), 'markdown-files.zip');
      P.setStatus(batchStatus, out.length + ' converted' + (failed ? ', ' + failed + ' failed' : '') + '. Your download has started.', failed ? 'error' : 'ok');
    });
  });
})();
