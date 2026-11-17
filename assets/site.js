/* Pandapi Tools: shared helpers. Everything runs in the browser; nothing is sent anywhere. */
(function (global) {
  'use strict';

  function $(sel, root) { return (root || document).querySelector(sel); }

  function setStatus(el, text, kind) {
    el.textContent = text || '';
    el.classList.remove('error', 'ok');
    if (kind) el.classList.add(kind);
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = filename; a.rel = 'noopener';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  function downloadText(text, filename, type) {
    downloadBlob(new Blob([text], { type: type || 'text/plain;charset=utf-8' }), filename);
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return fallbackCopy(text); });
    }
    return Promise.resolve(fallbackCopy(text));
  }
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    var ok = false; try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    ta.remove(); return ok;
  }

  /* Zip a list of {name, data(string|Uint8Array)} with fflate (vendor/fflate.js). Names are made unique. */
  function zipFiles(files) {
    var enc = new TextEncoder();
    var out = {}; var seen = {};
    files.forEach(function (f) {
      var name = f.name, i = 1;
      while (seen[name]) { name = f.name.replace(/(\.[^.]*)?$/, '-' + (++i) + '$1'); }
      seen[name] = true;
      out[name] = typeof f.data === 'string' ? enc.encode(f.data) : f.data;
    });
    return new Blob([global.fflate.zipSync(out, { level: 6 })], { type: 'application/zip' });
  }

  function baseName(filename) { return String(filename || 'file').replace(/\.[^.\/]+$/, '') || 'file'; }

  function formatBytes(n) {
    if (n < 1024) return n + ' B';
    if (n < 1048576) return (n / 1024).toFixed(1) + ' KB';
    return (n / 1048576).toFixed(1) + ' MB';
  }

  /* Wire a drop zone + hidden file input. onFiles receives an Array of File. */
  function setupDrop(zone, input, onFiles) {
    zone.addEventListener('click', function () { input.click(); });
    zone.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.click(); } });
    input.addEventListener('change', function () { if (input.files.length) onFiles(Array.prototype.slice.call(input.files)); input.value = ''; });
    ['dragenter', 'dragover'].forEach(function (t) { zone.addEventListener(t, function (e) { e.preventDefault(); zone.classList.add('over'); }); });
    ['dragleave', 'drop'].forEach(function (t) { zone.addEventListener(t, function (e) { e.preventDefault(); zone.classList.remove('over'); }); });
    zone.addEventListener('drop', function (e) { var fl = e.dataTransfer && e.dataTransfer.files; if (fl && fl.length) onFiles(Array.prototype.slice.call(fl)); });
  }

  /* Rough token estimate for LLM use: ~4 characters per token for English text. */
  function estimateTokens(text) { return Math.ceil(String(text || '').length / 4); }

  global.Pandapi = { $: $, setStatus: setStatus, downloadBlob: downloadBlob, downloadText: downloadText, copyText: copyText,
    zipFiles: zipFiles, baseName: baseName, formatBytes: formatBytes, setupDrop: setupDrop, estimateTokens: estimateTokens };
})(window);
