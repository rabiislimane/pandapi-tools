(function () {
  'use strict';
  var P = window.Pandapi, M = window.PandapiMdPdf, $ = P.$;
  var markedLib = window.marked, hljs = window.hljs;
  var input = $('#md-in'), preview = $('#preview'), status = $('#status'), notes = $('#notes'), imgNote = $('#img-note');
  var o = { size: $('#opt-size'), orient: $('#opt-orient'), margins: $('#opt-margins'), font: $('#opt-font'), toc: $('#opt-toc'),
    nums: $('#opt-nums'), breakH1: $('#opt-break'), header: $('#opt-header') };
  var images = {}, blobUrls = {}, fileBase = 'document', timer = null;

  function opts() {
    return { pageSize: o.size.value, orientation: o.orient.value, margins: o.margins.value, fontSize: Number(o.font.value), toc: o.toc.checked,
      pageNumbers: o.nums.checked, breakH1: o.breakH1.checked, titleInHeader: o.header.checked };
  }
  function env() { return { marked: markedLib, hljs: hljs, images: images }; }

  /* ---------- Preview (sanitized HTML) ---------- */
  var ALLOWED = { A: 1, ABBR: 1, B: 1, BLOCKQUOTE: 1, BR: 1, CODE: 1, DD: 1, DEL: 1, DETAILS: 1, DIV: 1, DL: 1, DT: 1, EM: 1, H1: 1, H2: 1, H3: 1, H4: 1, H5: 1, H6: 1,
    HR: 1, I: 1, IMG: 1, INPUT: 1, KBD: 1, LI: 1, MARK: 1, OL: 1, P: 1, PRE: 1, S: 1, SMALL: 1, SPAN: 1, STRONG: 1, SUB: 1, SUMMARY: 1, SUP: 1, TABLE: 1,
    TBODY: 1, TD: 1, TFOOT: 1, TH: 1, THEAD: 1, TR: 1, U: 1, UL: 1 };
  var ATTRS = { href: 1, src: 1, alt: 1, title: 1, id: 1, class: 1, align: 1, colspan: 1, rowspan: 1, start: 1, type: 1, checked: 1, disabled: 1, width: 1, height: 1 };

  function sanitize(html) {
    var doc = new DOMParser().parseFromString('<div>' + html + '</div>', 'text/html');
    var root = doc.body.firstChild;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 8) { n.remove(); return; }
        if (n.nodeType !== 1) return;
        if (!ALLOWED[n.tagName]) {
          if (/^(SCRIPT|STYLE|IFRAME|OBJECT|EMBED|NOSCRIPT|TEMPLATE|SVG|MATH|FORM|TEXTAREA|SELECT|BUTTON|LINK|META|BASE)$/.test(n.tagName)) { n.remove(); return; }
          var frag = doc.createDocumentFragment(); while (n.firstChild) frag.appendChild(n.firstChild);
          var parent = n.parentNode; parent.replaceChild(frag, n); walk(parent); return;
        }
        Array.prototype.slice.call(n.attributes).forEach(function (a) {
          var name = a.name.toLowerCase();
          if (!ATTRS[name]) { n.removeAttribute(a.name); return; }
          if (name === 'href' && !/^(https?:|mailto:|tel:|#)/i.test(a.value.trim())) n.removeAttribute(a.name);
          if (name === 'class' && !/^(language-[\w+-]+|hljs[\w\s-]*|pdf-page-break|md-alert[\w\s-]*)$/.test(a.value)) n.removeAttribute(a.name);
        });
        if (n.tagName === 'INPUT') { if ((n.getAttribute('type') || '').toLowerCase() !== 'checkbox') { n.remove(); return; } n.setAttribute('disabled', ''); }
        if (n.tagName === 'A' && /^https?:/i.test(n.getAttribute('href') || '')) { n.setAttribute('target', '_blank'); n.setAttribute('rel', 'noopener noreferrer nofollow'); }
        if (n.tagName === 'IMG') {
          var src = n.getAttribute('src') || '', key = M.baseName(src);
          if (blobUrls[key]) n.setAttribute('src', blobUrls[key]);
          else if (/^data:image\/(png|jpe?g|gif|webp);/i.test(src)) { /* keep */ }
          else { var sp = doc.createElement('span'); sp.className = 'img-missing'; sp.textContent = '[image' + (n.getAttribute('alt') ? ': ' + n.getAttribute('alt') : '') + ']'; n.replaceWith(sp); return; }
        }
        walk(n);
      });
    })(root);
    return root.innerHTML;
  }

  function renderPreview(md) {
    var fm = M.frontMatter(md);
    var body = fm.body.replace(/^[ \t]*(\\pagebreak|\\newpage|<!--\s*page-?break\s*-->)[ \t]*$/gim, '\n<div class="pdf-page-break"></div>\n');
    var slug = M.slugger();
    var html = markedLib.parse(body, { gfm: true, async: false });
    var clean = sanitize(html);
    var title = fm.meta.title && !/^\s*#\s/m.test(body) ? '<h1 class="fm-title">' + esc(fm.meta.title) + '</h1>' + ([fm.meta.author, fm.meta.date].filter(Boolean).length ? '<p class="fm-by">' + esc([fm.meta.author, fm.meta.date].filter(Boolean).join(' · ')) + '</p>' : '') : '';
    preview.innerHTML = title + clean;
    // heading ids + code colors + GitHub alerts
    // heading anchors get an md- prefix so they never clash with the page's own ids; #links inside the text follow them
    Array.prototype.forEach.call(preview.querySelectorAll('h1,h2,h3,h4,h5,h6'), function (h) { if (!h.classList.contains('fm-title')) h.id = 'md-' + slug(h.textContent); });
    Array.prototype.forEach.call(preview.querySelectorAll('a[href^="#"]'), function (a) { a.setAttribute('href', '#md-' + a.getAttribute('href').slice(1).toLowerCase()); });
    Array.prototype.forEach.call(preview.querySelectorAll('[id]:not(h1):not(h2):not(h3):not(h4):not(h5):not(h6)'), function (el) { el.removeAttribute('id'); });
    Array.prototype.forEach.call(preview.querySelectorAll('pre code'), function (c) {
      var m = /language-([\w+-]+)/.exec(c.className || '');
      if (m && hljs.getLanguage(m[1])) { c.innerHTML = hljs.highlight(c.textContent, { language: m[1], ignoreIllegals: true }).value; c.classList.add('hljs'); }
    });
    Array.prototype.forEach.call(preview.querySelectorAll('blockquote'), function (bq) {
      var p = bq.firstElementChild;
      var m = p && /^\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*/i.exec(p.textContent);
      if (!m) return;
      var kind = m[1].toLowerCase();
      bq.className = 'md-alert md-alert-' + kind;
      p.innerHTML = p.innerHTML.replace(/^\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(<br>)?\s*/i, '');
      var label = document.createElement('p'); label.className = 'md-alert-title'; label.textContent = kind.charAt(0).toUpperCase() + kind.slice(1);
      bq.insertBefore(label, p);
      if (!p.textContent.trim() && !p.querySelector('img')) p.remove();
    });
  }

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  function pageCss() {
    var size = { A4: 'A4', LETTER: 'letter', LEGAL: 'legal', A5: 'A5' }[o.size.value] || 'A4';
    var margin = { narrow: '0.5in', normal: '0.75in', wide: '1in' }[o.margins.value];
    return '@page { size: ' + size + ' ' + o.orient.value + '; margin: ' + margin + '; ' +
      (o.nums.checked ? '@bottom-center { content: counter(page) " / " counter(pages); font: 9px system-ui, sans-serif; color: #59636e; }' : '') + '}' +
      'html, body { background: #fff; margin: 0; } .md-body { font-size: ' + o.font.value + 'pt; padding: 0; border: 0; box-shadow: none; max-height: none; overflow: visible; }';
  }
  function applyPageCss() { preview.style.fontSize = (Number(o.font.value) * 1.333).toFixed(1) + 'px'; }

  // Print / Save as PDF: the browser's own PDF engine, so every language and emoji works. Prints a clean copy of the preview.
  function printDoc() {
    var old = document.getElementById('print-frame'); if (old) old.remove();
    var f = document.createElement('iframe');
    f.id = 'print-frame'; f.setAttribute('aria-hidden', 'true'); f.tabIndex = -1;
    f.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0;visibility:hidden';
    var r = M.toDoc(input.value, opts(), env());
    f.srcdoc = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>' + esc(fileNameFor(r, fileBase)) + '</title>' +
      '<link rel="stylesheet" href="md.css"><style>' + pageCss() + '</style></head><body><article class="md-body">' + preview.innerHTML + '</article></body></html>';
    f.onload = function () { setTimeout(function () { try { f.contentWindow.focus(); f.contentWindow.print(); } catch (e) { P.setStatus(status, 'Printing is blocked in this browser.', 'error'); } }, 150); };
    document.body.appendChild(f);
  }

  function render() {
    var md = input.value;
    applyPageCss();
    notes.innerHTML = '';
    if (!md.trim()) { preview.innerHTML = '<p class="meta">The preview appears here as you type.</p>'; setButtons(false); P.setStatus(status, ''); return; }
    try { renderPreview(md); } catch (e) { P.setStatus(status, 'Preview failed: ' + e.message, 'error'); }
    var r;
    try { r = M.toDoc(md, opts(), env()); } catch (e) { P.setStatus(status, 'Could not read this Markdown: ' + e.message, 'error'); setButtons(false); return; }
    r.warnings.forEach(function (w) { var li = document.createElement('li'); li.textContent = w.text; li.dataset.code = w.code; notes.appendChild(li); });
    setButtons(true);
    var words = (md.match(/\S+/g) || []).length;
    P.setStatus(status, words.toLocaleString() + ' words. Ready: Download PDF makes a PDF with real, selectable text.', 'ok');
  }

  function setButtons(on) { ['#btn-pdf', '#btn-print'].forEach(function (s) { $(s).disabled = !on; }); }
  function schedule() { clearTimeout(timer); timer = setTimeout(render, 250); }

  function pdfBlob(doc) {
    return new Promise(function (resolve, reject) {
      try { window.pdfMake.createPdf(doc, null, FONTS).getBlob(resolve); } catch (e) { reject(e); }
    });
  }
  var FONTS = {
    Roboto: { normal: 'Roboto-Regular.ttf', bold: 'Roboto-Medium.ttf', italics: 'Roboto-Italic.ttf', bolditalics: 'Roboto-MediumItalic.ttf' },
    Mono: { normal: 'JetBrainsMono-Regular.ttf', bold: 'JetBrainsMono-Regular.ttf', italics: 'JetBrainsMono-Regular.ttf', bolditalics: 'JetBrainsMono-Regular.ttf' }
  };

  function fileNameFor(r, fallback) {
    var n = (fallback && fallback !== 'document') ? fallback : (r.title || 'document');
    return n.replace(/[\\/:*?"<>|\u0000-\u001F]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 80) || 'document';
  }

  $('#btn-pdf').addEventListener('click', function () {
    var btn = this; btn.disabled = true;
    P.setStatus(status, 'Making the PDF…');
    var r;
    try { r = M.toDoc(input.value, opts(), env()); } catch (e) { P.setStatus(status, e.message, 'error'); btn.disabled = false; return; }
    var t0 = Date.now();
    pdfBlob(r.doc).then(function (blob) {
      P.downloadBlob(blob, fileNameFor(r, fileBase) + '.pdf');
      P.setStatus(status, 'PDF ready (' + P.formatBytes(blob.size) + ', ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s). It is downloading.', 'ok');
    }).catch(function (e) { P.setStatus(status, 'PDF failed: ' + e.message, 'error'); }).then(function () { btn.disabled = false; });
  });

  $('#btn-print').addEventListener('click', printDoc);

  /* ---------- Files ---------- */
  function isImage(f) { return /^image\/(png|jpe?g|gif|webp|svg\+xml|bmp)$/i.test(f.type) || /\.(png|jpe?g|gif|webp|svg|bmp)$/i.test(f.name); }
  function isMd(f) { return /\.(md|markdown|mdown|mkd|txt|text)$/i.test(f.name) || f.type === 'text/markdown'; }

  // pdfmake takes PNG and JPEG; other formats are drawn to a canvas and saved as PNG.
  function loadImage(f) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(f), img = new Image();
      img.onload = function () {
        var key = f.name.toLowerCase();
        var w = img.naturalWidth || 600, h = img.naturalHeight || 400;
        if (/^image\/(png|jpeg)$/.test(f.type) && !/\.svg$/i.test(f.name)) {
          var rd = new FileReader();
          rd.onload = function () { resolve({ key: key, url: url, data: { dataUrl: rd.result, width: w, height: h } }); };
          rd.onerror = function () { reject(new Error('Could not read ' + f.name)); };
          rd.readAsDataURL(f);
        } else {
          var scale = Math.min(1, 2400 / Math.max(w, h)), c = document.createElement('canvas');
          c.width = Math.max(1, Math.round(w * scale)); c.height = Math.max(1, Math.round(h * scale));
          c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
          resolve({ key: key, url: url, data: { dataUrl: c.toDataURL('image/png'), width: w, height: h } });
        }
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error(f.name + ' is not an image the browser can open.')); };
      img.src = url;
    });
  }

  function addImages(files) {
    return Promise.all(files.map(function (f) { return loadImage(f).catch(function (e) { P.setStatus(status, e.message, 'error'); return null; }); })).then(function (list) {
      list.filter(Boolean).forEach(function (x) { if (blobUrls[x.key]) URL.revokeObjectURL(blobUrls[x.key]); images[x.key] = x.data; blobUrls[x.key] = x.url; });
      var n = Object.keys(images).length;
      imgNote.textContent = n ? n + ' image' + (n > 1 ? 's' : '') + ' added: ' + Object.keys(images).slice(0, 6).join(', ') + (n > 6 ? '…' : '') : '';
    });
  }

  function readText(f) { return f.arrayBuffer().then(function (b) { return new TextDecoder('utf-8').decode(b).replace(/^﻿/, ''); }); }

  function batch(mdFiles) {
    var list = $('#batch-list'), bstatus = $('#batch-status');
    list.innerHTML = '';
    var combine = $('#opt-combine').checked;
    P.setStatus(bstatus, 'Making ' + mdFiles.length + ' PDFs…');
    var results = [], outFiles = [], failed = 0, chain = Promise.resolve();
    mdFiles.sort(function (a, b) { return a.name.localeCompare(b.name, undefined, { numeric: true }); });
    mdFiles.forEach(function (f) {
      chain = chain.then(function () { return readText(f); }).then(function (text) {
        var r = M.toDoc(text, opts(), env());
        if (combine) { results.push(r); return { name: f.name, ok: true }; }
        return pdfBlob(r.doc).then(function (blob) { return blob.arrayBuffer(); }).then(function (buf) {
          outFiles.push({ name: P.baseName(f.name) + '.pdf', data: new Uint8Array(buf) });
          return { name: f.name, ok: true, size: buf.byteLength };
        });
      }).catch(function (e) { failed++; return { name: f.name, ok: false, err: e.message }; }).then(function (res) {
        var li = document.createElement('li');
        li.innerHTML = '<span class="name">' + esc(res.name) + '</span><span class="meta"' + (res.ok ? '' : ' style="color:var(--danger)"') + '>' + (res.ok ? (res.size ? P.formatBytes(res.size) : 'added') : esc(res.err)) + '</span>';
        list.appendChild(li);
      });
    });
    chain.then(function () {
      if (combine && results.length) {
        return pdfBlob(M.combine(results)).then(function (blob) { P.downloadBlob(blob, 'combined.pdf'); P.setStatus(bstatus, results.length + ' files in one PDF (' + P.formatBytes(blob.size) + '). It is downloading.', 'ok'); });
      }
      if (outFiles.length) { P.downloadBlob(P.zipFiles(outFiles), 'pdf-files.zip'); P.setStatus(bstatus, outFiles.length + ' PDFs made' + (failed ? ', ' + failed + ' failed' : '') + '. Your .zip is downloading.', 'ok'); }
      else P.setStatus(bstatus, 'No PDF could be made.', 'error');
    }).catch(function (e) { P.setStatus(bstatus, 'Failed: ' + e.message, 'error'); });
  }

  function onFiles(files) {
    var imgs = files.filter(isImage), mds = files.filter(function (f) { return !isImage(f) && isMd(f); });
    var other = files.length - imgs.length - mds.length;
    var p = imgs.length ? addImages(imgs) : Promise.resolve();
    p.then(function () {
      if (mds.length === 1) {
        return readText(mds[0]).then(function (t) { input.value = t; fileBase = P.baseName(mds[0].name); render(); });
      }
      if (mds.length > 1) { render(); batch(mds); return; }
      render();
      if (other) P.setStatus(status, 'Drop .md files (Markdown) or images.', 'error');
    });
  }

  P.setupDrop($('#drop'), $('#file-in'), onFiles);
  P.setupDrop($('#img-drop'), $('#img-in'), function (fs) { addImages(fs.filter(isImage)).then(render); });
  input.addEventListener('input', schedule);
  Object.keys(o).forEach(function (k) { o[k].addEventListener('change', render); });
  $('#btn-sample').addEventListener('click', function () { input.value = $('#sample-md').textContent.replace(/^\n/, ''); fileBase = 'document'; render(); input.focus(); });
  $('#btn-clear').addEventListener('click', function () { input.value = ''; fileBase = 'document'; render(); input.focus(); });
  // paste a screenshot straight into the text: it is added as an image and referenced
  input.addEventListener('paste', function (e) {
    var items = (e.clipboardData && e.clipboardData.files) ? Array.prototype.slice.call(e.clipboardData.files) : [];
    var pics = items.filter(isImage);
    if (!pics.length) return;
    e.preventDefault();
    var named = pics.map(function (f, i) { return new File([f], 'pasted-' + Date.now() + '-' + i + '.png', { type: f.type }); });
    addImages(named).then(function () {
      var ins = named.map(function (f) { return '![](' + f.name + ')'; }).join('\n');
      var s = input.selectionStart, en = input.selectionEnd;
      input.value = input.value.slice(0, s) + ins + input.value.slice(en);
      render();
    });
  });
  render();
})();
