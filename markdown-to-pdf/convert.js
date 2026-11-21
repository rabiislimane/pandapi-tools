/* Markdown to PDF core: turns Markdown into a pdfmake document definition (real, selectable text; no screenshots).
   Pure functions; works in the browser (window.PandapiMdPdf) and in Node (module.exports).
   env: { marked, hljs, images: { "<file name>": { dataUrl, width, height } } } */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api; else root.PandapiMdPdf = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var PAGE = { A4: [595.28, 841.89], LETTER: [612, 792], LEGAL: [612, 1008], A5: [419.53, 595.28] };
  var MARGINS = { narrow: 36, normal: 54, wide: 72 };
  var COLORS = { text: '#1f2328', muted: '#59636e', border: '#d1d9e0', link: '#0969da', codeBg: '#f6f8fa', inlineCodeBg: '#eff1f3', head: '#f6f8fa' };
  var HL = { keyword: '#cf222e', built_in: '#8250df', type: '#953800', literal: '#0550ae', number: '#0550ae', string: '#0a3069', regexp: '#0a3069',
    comment: '#6e7781', quote: '#6e7781', doctag: '#6e7781', title: '#8250df', 'title.function': '#8250df', 'title.class': '#953800', params: '#1f2328',
    attr: '#0550ae', attribute: '#0550ae', variable: '#953800', 'template-variable': '#953800', meta: '#0550ae', tag: '#116329', name: '#116329',
    'selector-tag': '#116329', 'selector-class': '#8250df', 'selector-id': '#0550ae', property: '#0550ae', symbol: '#0550ae', bullet: '#953800',
    section: '#0550ae', addition: '#116329', deletion: '#82071e', subst: '#1f2328', operator: '#cf222e', punctuation: '#1f2328' };
  var ALERTS = { NOTE: ['Note', '#0969da'], TIP: ['Tip', '#1a7f37'], IMPORTANT: ['Important', '#8250df'], WARNING: ['Warning', '#9a6700'], CAUTION: ['Caution', '#d1242f'] };
  var EMOJI = /\p{Extended_Pictographic}️?(‍\p{Extended_Pictographic}️?)*|[\u{1F1E6}-\u{1F1FF}]{2}|️/gu;
  // Scripts the embedded fonts don't cover: Hebrew, Arabic, Indic, Thai, CJK, Hangul...
  var UNSUPPORTED = /[֐-ࣿऀ-෿฀-࿿ᄀ-ᇿ⺀-鿿ꥠ-꥿가-힯豈-﫿︰-﹏＀-￯]/;

  function decodeEntities(s) {
    return String(s).replace(/&(#x[0-9a-fA-F]+|#\d+|amp|lt|gt|quot|apos|nbsp|#39);/g, function (m, e) {
      if (e === 'nbsp') return ' ';
      if (e[0] === '#') { var n = e[1] === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10); try { return String.fromCodePoint(n); } catch (x) { return m; } }
      return { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" }[e];
    });
  }

  /** YAML-style front matter at the very top: title, author, date, subject, keywords. Returns { meta, body }. */
  function frontMatter(md) {
    md = String(md || '').replace(/^﻿/, '').replace(/\r\n?/g, '\n');
    var m = /^---\n([\s\S]*?)\n(---|\.\.\.)\n?/.exec(md);
    if (!m) return { meta: {}, body: md };
    var meta = {};
    m[1].split('\n').forEach(function (line) {
      var kv = /^([A-Za-z_][\w-]*)\s*:\s*(.*)$/.exec(line);
      if (kv) meta[kv[1].toLowerCase()] = kv[2].replace(/^["']|["']$/g, '').trim();
    });
    return { meta: meta, body: md.slice(m[0].length) };
  }

  /** GitHub-style heading anchors: lower case, spaces to dashes, punctuation dropped, duplicates get -1, -2. */
  function slugger() {
    var seen = Object.create(null);
    return function (text) {
      var s = String(text).toLowerCase().trim().replace(/<[^>]*>/g, '').replace(/[^\p{L}\p{N}\s_-]/gu, '').replace(/\s/g, '-');
      var base = s, n = seen[base] || 0;
      if (seen[base] != null) { s = base + '-' + n; }
      seen[base] = n + 1;
      return s || 'section';
    };
  }

  function plain(tokens) {
    return (tokens || []).map(function (t) { return t.tokens ? plain(t.tokens) : (t.type === 'image' ? t.text : decodeEntities(t.text || '')); }).join('');
  }

  function baseName(src) {
    var s = String(src || '').split(/[?#]/)[0];
    try { s = decodeURIComponent(s); } catch (e) { /* keep */ }
    return s.split(/[\\/]/).pop().toLowerCase();
  }

  /** Turn highlight.js HTML into pdfmake text runs with colors. */
  function hlRuns(html) {
    var runs = [], stack = [], re = /<span class="([^"]*)">|<\/span>|([^<]+)/g, m;
    while ((m = re.exec(html))) {
      if (m[1] != null) {
        var cls = m[1].split(/\s+/).map(function (c) { return c.replace(/^hljs-/, '').replace(/_+$/, ''); });
        var col = null;
        for (var i = 0; i < cls.length && !col; i++) col = HL[cls.slice(i).join('.')] || HL[cls[i]] || null;
        stack.push(col || (stack.length ? stack[stack.length - 1] : null));
      } else if (m[0] === '</span>') stack.pop();
      else if (m[2]) {
        var c = stack.length ? stack[stack.length - 1] : null;
        runs.push(c ? { text: decodeEntities(m[2]), color: c } : { text: decodeEntities(m[2]) });
      }
    }
    return runs;
  }

  /** Hard-wrap runs at maxChars per line so long code lines never run off the page. */
  function wrapRuns(runs, maxChars) {
    var out = [], col = 0;
    runs.forEach(function (r) {
      var parts = r.text.split('\n');
      parts.forEach(function (p, pi) {
        if (pi > 0) { out.push({ text: '\n' }); col = 0; }
        while (p.length) {
          var room = maxChars - col;
          if (room <= 0) { out.push({ text: '\n' }); col = 0; room = maxChars; }
          var piece = p.slice(0, room);
          out.push(Object.assign({}, r, { text: piece }));
          col += piece.length; p = p.slice(piece.length);
        }
      });
    });
    return out;
  }

  /** Build the pdfmake document definition. */
  function toDoc(md, opts, env) {
    opts = Object.assign({ pageSize: 'A4', orientation: 'portrait', margins: 'normal', fontSize: 11, toc: false, pageNumbers: true,
      breakH1: false, titleInHeader: false }, opts || {});
    env = env || {};
    var marked = env.marked, hljs = env.hljs, images = env.images || {};
    var warnings = [], missingImages = [], remoteImages = 0, emojiCount = 0;
    var fm = frontMatter(md);
    var meta = fm.meta;
    var body = fm.body;
    var unsupported = UNSUPPORTED.exec(body);
    if (unsupported) warnings.push({ code: 'script', text: 'This text has characters the PDF fonts don\'t include (for example "' + unsupported[0] + '"). Use Print / Save as PDF, which supports every language.' });
    // page break markers
    body = body.replace(/^[ \t]*(\\pagebreak|\\newpage|<!--\s*page-?break\s*-->)[ \t]*$/gim, '\n<div class="pdf-page-break"></div>\n');

    var size = PAGE[opts.pageSize] || PAGE.A4;
    var landscape = opts.orientation === 'landscape';
    var pageW = landscape ? size[1] : size[0], pageH = landscape ? size[0] : size[1];
    var margin = MARGINS[opts.margins] != null ? MARGINS[opts.margins] : 54;
    var avail = pageW - 2 * margin;
    var fs = Number(opts.fontSize) || 11;
    var codeFs = Math.round(fs * 0.82 * 10) / 10;
    var codeChars = Math.max(20, Math.floor((avail - 20) / (codeFs * 0.6)));
    var slug = slugger();
    var firstH1 = true, title = meta.title || null, h1Count = 0;

    var tokens = marked.lexer(body, { gfm: true });

    function clean(s) {
      s = String(s);
      if (EMOJI.test(s)) { EMOJI.lastIndex = 0; emojiCount++; s = s.replace(EMOJI, ''); }
      EMOJI.lastIndex = 0;
      return s;
    }

    function inline(tks, st) {
      var out = [];
      st = st || {};
      (tks || []).forEach(function (t) {
        var s = Object.assign({}, st);
        switch (t.type) {
          case 'strong': s.bold = true; out = out.concat(inline(t.tokens, s)); break;
          case 'em': s.italics = true; out = out.concat(inline(t.tokens, s)); break;
          case 'del': s.decoration = 'lineThrough'; out = out.concat(inline(t.tokens, s)); break;
          case 'codespan': out.push(Object.assign(run(decodeEntities(t.text), s), { font: 'Mono', fontSize: codeFs, background: COLORS.inlineCodeBg })); break;
          case 'br': out.push({ text: '\n' }); break;
          case 'link': {
            var href = t.href || '';
            if (href.charAt(0) === '#') s.linkToDestination = href.slice(1).toLowerCase();
            else if (/^(https?:|mailto:|tel:)/i.test(href)) s.link = href;
            s.color = COLORS.link;
            out = out.concat(inline(t.tokens, s));
            break;
          }
          case 'image': {
            var im = images[baseName(t.href)];
            if (!im) { if (/^https?:/i.test(t.href)) remoteImages++; else missingImages.push(t.href); }
            out.push(Object.assign(run('[image' + (t.text ? ': ' + t.text : '') + ']', s), { italics: true, color: COLORS.muted }));
            break;
          }
          case 'html': {
            if (/^<br\s*\/?>$/i.test(t.text.trim())) out.push({ text: '\n' });
            else if (/^<(b|strong)>$/i.test(t.text)) st.bold = true;
            else if (/^<\/(b|strong)>$/i.test(t.text)) st.bold = false;
            else if (/^<(i|em)>$/i.test(t.text)) st.italics = true;
            else if (/^<\/(i|em)>$/i.test(t.text)) st.italics = false;
            break; // other inline tags are dropped, their text stays
          }
          case 'escape': out.push(run(decodeEntities(t.text), s)); break;
          case 'checkbox': break;
          default:
            if (t.tokens) out = out.concat(inline(t.tokens, s));
            else out.push(run(decodeEntities(t.text != null ? t.text : t.raw || ''), s));
        }
      });
      return out;
    }
    function run(text, s) { var r = Object.assign({ text: clean(text) }, s); return r; }

    // Images that stand alone in a paragraph become real images.
    function imageBlock(t) {
      var im = images[baseName(t.href)];
      if (!im) return null;
      var w = Math.min(avail, (im.width || avail) * 0.75);
      var h = (im.height || w) * 0.75 * (w / ((im.width || avail) * 0.75));
      var maxH = (pageH - 2 * margin) * 0.75;
      if (h > maxH) { w = w * maxH / h; }
      return { image: im.dataUrl, width: w, alignment: 'center', margin: [0, 4, 0, 10] };
    }

    function headingSize(d) { return [fs * 2, fs * 1.55, fs * 1.27, fs * 1.09, fs, fs * 0.95][d - 1]; }

    function block(t, ctx) {
      ctx = ctx || {};
      switch (t.type) {
        case 'space': return null;
        case 'heading': {
          var text = plain(t.tokens);
          var id = slug(text);
          if (t.depth === 1) { h1Count++; if (!title) title = clean(text).trim(); }
          var node = { text: inline(t.tokens, { bold: true }), fontSize: headingSize(t.depth), id: id, color: t.depth === 6 ? COLORS.muted : COLORS.text,
            margin: [0, t.depth <= 2 ? 14 : 10, 0, t.depth <= 2 ? 2 : 4], lineHeight: 1.15 };
          if (opts.toc && t.depth <= 3 && !ctx.nested) { node.tocItem = true; node.tocMargin = [(t.depth - 1) * 14, 0, 0, 2]; node.tocStyle = t.depth === 1 ? { bold: true } : {}; }
          var stack = [node];
          if (t.depth <= 2) stack.push({ canvas: [{ type: 'line', x1: 0, y1: 0, x2: avail - (ctx.indent || 0), y2: 0, lineWidth: 0.6, lineColor: COLORS.border }], margin: [0, 2, 0, 6] });
          var out = { stack: stack, headlineLevel: t.depth };
          if (opts.breakH1 && t.depth === 1 && !ctx.nested) { if (!firstH1) out.pageBreak = 'before'; firstH1 = false; }
          return out;
        }
        case 'paragraph': {
          var tk = t.tokens || [];
          var only = tk.filter(function (x) { return !(x.type === 'text' && !x.text.trim()); });
          if (only.length === 1 && only[0].type === 'image') { var ib = imageBlock(only[0]); if (ib) return ib; }
          if (only.length === 1 && only[0].type === 'link' && only[0].tokens && only[0].tokens.length === 1 && only[0].tokens[0].type === 'image') {
            var ib2 = imageBlock(only[0].tokens[0]); if (ib2) { if (/^https?:/i.test(only[0].href)) ib2.link = only[0].href; return ib2; }
          }
          return { text: inline(tk), margin: [0, 0, 0, fs * 0.75], lineHeight: 1.3 };
        }
        case 'text': return { text: t.tokens ? inline(t.tokens) : clean(decodeEntities(t.text)), lineHeight: 1.3 };
        case 'hr': return { canvas: [{ type: 'line', x1: 0, y1: 0, x2: avail - (ctx.indent || 0), y2: 0, lineWidth: 1.5, lineColor: COLORS.border }], margin: [0, 8, 0, 14] };
        case 'code': {
          var lang = (t.lang || '').split(/\s/)[0].toLowerCase();
          if (lang === 'mermaid') warnings.push({ code: 'mermaid', text: 'Mermaid diagrams are shown as code in the PDF.' });
          var runs;
          try {
            if (hljs && lang && hljs.getLanguage(lang)) runs = hlRuns(hljs.highlight(t.text, { language: lang, ignoreIllegals: true }).value);
          } catch (e) { runs = null; }
          if (!runs) runs = [{ text: t.text }];
          runs = wrapRuns(runs, codeChars - Math.floor((ctx.indent || 0) / (codeFs * 0.6)));
          return { table: { widths: ['*'], body: [[{ text: runs.length ? runs : ' ', font: 'Mono', fontSize: codeFs, lineHeight: 1.25, preserveLeadingSpaces: true, fillColor: COLORS.codeBg }]] },
            layout: { hLineWidth: function () { return 0; }, vLineWidth: function () { return 0; }, paddingLeft: function () { return 9; }, paddingRight: function () { return 9; }, paddingTop: function () { return 7; }, paddingBottom: function () { return 7; } },
            margin: [0, 0, 0, fs * 0.9] };
        }
        case 'blockquote': {
          var inner = t.tokens || [];
          var alert = null;
          if (inner[0] && inner[0].type === 'paragraph') {
            var am = /^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*\n?/i.exec(inner[0].text || '');
            if (am) {
              alert = ALERTS[am[1].toUpperCase()];
              inner = inner.slice();
              var rest = inner[0].text.slice(am[0].length);
              inner[0] = rest.trim() ? marked.lexer(rest)[0] : { type: 'space' };
            }
          }
          var content = blocks(inner, { nested: true, indent: (ctx.indent || 0) + 14 });
          if (alert) content.unshift({ text: alert[0], bold: true, color: alert[1], margin: [0, 0, 0, 3] });
          var last = content[content.length - 1]; if (last && last.margin) last.margin = [last.margin[0], last.margin[1], last.margin[2], 0];
          var barColor = alert ? alert[1] : COLORS.border;
          return { table: { widths: ['*'], body: [[{ stack: content, color: alert ? COLORS.text : COLORS.muted }]] },
            layout: { hLineWidth: function () { return 0; }, vLineWidth: function (i) { return i === 0 ? 3 : 0; }, vLineColor: function () { return barColor; },
              paddingLeft: function () { return 11; }, paddingRight: function () { return 0; }, paddingTop: function () { return 2; }, paddingBottom: function () { return 2; } },
            margin: [0, 0, 0, fs * 0.9] };
        }
        case 'list': {
          var items = t.items.map(function (it) {
            var kids = blocks(it.tokens, { nested: true, indent: (ctx.indent || 0) + 18, inList: true });
            kids.forEach(function (k) { if (k && k.margin && !k.table) k.margin = [k.margin[0], k.margin[1], k.margin[2], it.loose || t.loose ? fs * 0.5 : 2]; });
            var item = kids.length === 1 ? kids[0] : { stack: kids };
            if (it.task) {
              var box = { canvas: [{ type: 'rect', x: 0, y: 2, w: fs * 0.78, h: fs * 0.78, r: 1.5, lineWidth: 0.9, lineColor: COLORS.muted }]
                .concat(it.checked ? [{ type: 'polyline', points: [{ x: fs * 0.16, y: 2 + fs * 0.4 }, { x: fs * 0.34, y: 2 + fs * 0.6 }, { x: fs * 0.64, y: 2 + fs * 0.16 }], lineWidth: 1.4, lineColor: COLORS.text }] : []), width: fs * 1.2 };
              item = { columns: [box, Object.assign({ width: '*' }, kids.length === 1 ? kids[0] : { stack: kids })], columnGap: 2 };
            }
            return item;
          });
          var anyTask = t.items.some(function (it) { return it.task; });
          var l = t.ordered ? { ol: items, start: Number(t.start) || 1 } : { ul: items };
          if (anyTask && !t.ordered) l.type = 'none';
          l.margin = [ctx.inList ? 0 : 4, 0, 0, ctx.inList ? 2 : fs * 0.75];
          l.lineHeight = 1.3;
          if (!t.ordered && ctx.inList) l.type = l.type || 'circle';
          return l;
        }
        case 'table': {
          var ncol = t.header.length;
          var align = t.align.map(function (a) { return a === 'center' ? 'center' : a === 'right' ? 'right' : 'left'; });
          var head = t.header.map(function (c, i) { return { text: inline(c.tokens, { bold: true }), alignment: align[i], fillColor: COLORS.head }; });
          var rows = t.rows.map(function (r) { return r.map(function (c, i) { return { text: inline(c.tokens), alignment: align[i] }; }); });
          var lens = t.header.map(function (c, i) { return Math.max(plain(c.tokens).length, Math.max.apply(null, [0].concat(t.rows.map(function (r) { return r[i] ? plain(r[i].tokens).length : 0; })))); });
          var est = lens.reduce(function (a, b) { return a + b * fs * 0.52 + 12; }, 0);
          var widths = est <= avail - (ctx.indent || 0) ? lens.map(function () { return 'auto'; }) : lens.map(function (n) { return n > 12 ? '*' : 'auto'; });
          var tableFs = ncol > 6 ? fs * 0.82 : ncol > 4 ? fs * 0.9 : fs;
          return { table: { headerRows: 1, dontBreakRows: true, widths: widths, body: [head].concat(rows) }, fontSize: tableFs, lineHeight: 1.2,
            layout: { hLineWidth: function () { return 0.6; }, vLineWidth: function () { return 0.6; }, hLineColor: function () { return COLORS.border; }, vLineColor: function () { return COLORS.border; },
              paddingLeft: function () { return 6; }, paddingRight: function () { return 6; }, paddingTop: function () { return 4; }, paddingBottom: function () { return 4; } },
            margin: [0, 2, 0, fs * 0.9] };
        }
        case 'html': {
          if (/class="pdf-page-break"|page-break-(after|before)\s*:\s*always|break-(after|before)\s*:\s*page/i.test(t.text)) return { text: '', pageBreak: 'after' };
          var txt = decodeEntities(t.text.replace(/<!--[\s\S]*?-->/g, '').replace(/<(script|style)[\s\S]*?<\/\1>/gi, '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/(p|div|h\d|li|tr)>/gi, '\n').replace(/<[^>]+>/g, '')).replace(/\n{3,}/g, '\n\n').trim();
          return txt ? { text: clean(txt), margin: [0, 0, 0, fs * 0.75], lineHeight: 1.3 } : null;
        }
        case 'def': return null;
        default:
          if (t.tokens) return { text: inline(t.tokens), margin: [0, 0, 0, fs * 0.75] };
          return t.text ? { text: clean(decodeEntities(t.text)), margin: [0, 0, 0, fs * 0.75] } : null;
      }
    }

    function blocks(tks, ctx) { return (tks || []).map(function (t) { return block(t, ctx); }).filter(Boolean); }

    var content = blocks(tokens);
    // a page break at the very end makes a blank page
    while (content.length && content[content.length - 1].pageBreak === 'after' && content[content.length - 1].text === '') content.pop();

    // Title block from front matter when the text has no # heading of its own
    var head = [];
    if (meta.title && !h1Count) {
      head.push({ text: clean(meta.title), fontSize: fs * 2.1, bold: true, margin: [0, 0, 0, 4] });
      var by = [meta.author, meta.date].filter(Boolean).join(' · ');
      if (by) head.push({ text: clean(by), color: COLORS.muted, margin: [0, 0, 0, 14] });
      else head[0].margin = [0, 0, 0, 14];
    }
    if (opts.toc) {
      head.push({ toc: { title: { text: 'Contents', fontSize: fs * 1.45, bold: true, margin: [0, 0, 0, 8] }, numberStyle: { color: COLORS.muted } }, margin: [0, 0, 0, 8] });
      head.push({ text: '', pageBreak: 'after' });
    }

    if (missingImages.length) warnings.push({ code: 'images', text: missingImages.length + ' image' + (missingImages.length > 1 ? 's are' : ' is') + ' not loaded (' + missingImages.slice(0, 3).join(', ') + '). Add the image files with "Add images" and they go into the PDF.' });
    if (remoteImages) warnings.push({ code: 'remote', text: remoteImages + ' web image' + (remoteImages > 1 ? 's' : '') + ' (https://...) shown as alt text: the page doesn\'t download images from other sites. Save them and add them with "Add images".' });
    if (emojiCount) warnings.push({ code: 'emoji', text: 'Emoji were left out of the PDF (its fonts have none). Print / Save as PDF keeps them.' });

    var docTitle = title || 'Document';
    var doc = {
      pageSize: opts.pageSize === 'A5' ? { width: size[0], height: size[1] } : opts.pageSize,
      pageOrientation: landscape ? 'landscape' : 'portrait',
      pageMargins: [margin, margin, margin, margin + (opts.pageNumbers ? 6 : 0)],
      info: { title: docTitle, author: meta.author || undefined, subject: meta.subject || meta.description || undefined, keywords: meta.keywords || undefined, creator: 'Pandapi Tools: Markdown to PDF', producer: 'Pandapi Tools (pdfmake)' },
      content: head.concat(content),
      defaultStyle: { font: 'Roboto', fontSize: fs, color: COLORS.text, lineHeight: 1.25 },
      pageBreakBefore: function (node, nodesAfterOnPage) { return !!node.headlineLevel && nodesAfterOnPage.length === 0 && node.startPosition && node.startPosition.top > 0; }
    };
    if (opts.pageNumbers) doc.footer = function (cur, total) { return { text: cur + ' / ' + total, alignment: 'center', fontSize: 8.5, color: COLORS.muted, margin: [0, margin / 2.6, 0, 0] }; };
    if (opts.titleInHeader && docTitle) doc.header = function (cur) { return cur === 1 ? null : { text: docTitle, alignment: 'right', fontSize: 8.5, color: COLORS.muted, margin: [margin, margin / 2.6, margin, 0] }; };
    if (!doc.info.author) delete doc.info.author;
    if (!doc.info.subject) delete doc.info.subject;
    if (!doc.info.keywords) delete doc.info.keywords;
    return { doc: doc, title: docTitle, meta: meta, warnings: warnings };
  }

  /** Several documents in one PDF: each starts on a new page; the table of contents (if on) lists them all. */
  function combine(results) {
    if (!results.length) return null;
    var first = results[0].doc;
    var doc = Object.assign({}, first);
    var content = [];
    results.forEach(function (r, i) {
      var c = r.doc.content.filter(function (n) { return !n.toc && !(n.pageBreak === 'after' && n.text === ''); });
      if (i > 0 && c.length) c[0] = Object.assign({}, c[0], { pageBreak: 'before' });
      content = content.concat(c);
    });
    var tocNodes = first.content.filter(function (n) { return n.toc; });
    if (tocNodes.length) content = tocNodes.concat([{ text: '', pageBreak: 'after' }], content);
    doc.content = content;
    doc.info = Object.assign({}, first.info, { title: results.length + ' documents' });
    return doc;
  }

  return { toDoc: toDoc, combine: combine, frontMatter: frontMatter, slugger: slugger, hlRuns: hlRuns, wrapRuns: wrapRuns, baseName: baseName, PAGE: PAGE };
});
