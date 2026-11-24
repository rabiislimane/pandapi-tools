/* Word (.docx) and pasted Word / Google Docs content to Markdown (browser).
   Uses mammoth (docx to HTML), Turndown + GFM plugin (HTML to Markdown) and fflate (document properties), all vendored.
   Exposed as window.PandapiDocx. */
(function (global) {
  'use strict';

  var IMAGE_EXT = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif', 'image/bmp': 'bmp', 'image/tiff': 'tif', 'image/svg+xml': 'svg',
    'image/webp': 'webp', 'image/x-emf': 'emf', 'image/x-wmf': 'wmf', 'image/emf': 'emf', 'image/wmf': 'wmf' };

  // Word styles that mammoth doesn't map by default, so they don't fall back to plain paragraphs.
  var STYLE_MAP = [
    "p[style-name='Title'] => h1:fresh",
    "p[style-name='Subtitle'] => p:fresh",
    "p[style-name='Quote'] => blockquote > p:fresh",
    "p[style-name='Intense Quote'] => blockquote > p:fresh",
    "p[style-name='Block Text'] => blockquote > p:fresh",
    "p[style-name='Source Code'] => pre:separator('\\n')",
    "p[style-name='Code'] => pre:separator('\\n')",
    "p[style-name='HTML Preformatted'] => pre:separator('\\n')",
    "p[style-name='Plain Text'] => pre:separator('\\n')",
    "r[style-name='Verbatim Char'] => code",
    "r[style-name='Code Char'] => code",
    "r[style-name='HTML Code'] => code",
    "r[style-name='Source Code Char'] => code",
    "r[style-name='Inline Code'] => code"
  ];

  function slug(s) { return String(s || '').toLowerCase().replace(/\.[a-z0-9]+$/i, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'document'; }

  function xmlText(xml, tag) {
    var m = new RegExp('<' + tag + '\\b[^>]*>([\\s\\S]*?)</' + tag + '>').exec(xml);
    if (!m) return '';
    return m[1].replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&').trim();
  }

  /** Title, author, dates and keywords from docProps/core.xml. bytes: Uint8Array; unzip: fflate.unzipSync. */
  function docProps(bytes, unzip) {
    try {
      var files = unzip(bytes, { filter: function (f) { return f.name === 'docProps/core.xml'; } });
      var core = files['docProps/core.xml'];
      if (!core) return {};
      var x = new TextDecoder('utf-8').decode(core);
      var p = { title: xmlText(x, 'dc:title'), author: xmlText(x, 'dc:creator'), subject: xmlText(x, 'dc:subject'),
        description: xmlText(x, 'dc:description'), keywords: xmlText(x, 'cp:keywords'),
        created: xmlText(x, 'dcterms:created'), modified: xmlText(x, 'dcterms:modified') };
      Object.keys(p).forEach(function (k) { if (!p[k]) delete p[k]; });
      return p;
    } catch (e) { return {}; }
  }

  function yaml(s) { return '"' + String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\s+/g, ' ').trim() + '"'; }

  /** YAML front matter from document properties (and a fallback title). */
  function frontMatter(props, fallbackTitle) {
    var lines = [];
    var title = props.title || fallbackTitle;
    if (title) lines.push('title: ' + yaml(title));
    if (props.author) lines.push('author: ' + yaml(props.author));
    if (props.created) lines.push('date: ' + props.created.slice(0, 10));
    if (props.modified) lines.push('updated: ' + props.modified.slice(0, 10));
    if (props.subject) lines.push('subject: ' + yaml(props.subject));
    if (props.description) lines.push('description: ' + yaml(props.description));
    if (props.keywords) {
      var tags = props.keywords.split(/[;,]/).map(function (t) { return t.trim(); }).filter(Boolean);
      if (tags.length) lines.push('tags: [' + tags.map(yaml).join(', ') + ']');
    }
    return lines.length ? '---\n' + lines.join('\n') + '\n---\n\n' : '';
  }

  /** .docx bytes to HTML with mammoth. opts.images: 'files' (default) | 'inline' | 'drop'; opts.base: name for image files. */
  function docxToHtml(bytes, opts) {
    opts = opts || {};
    var mammoth = global.mammoth;
    if (!(bytes[0] === 0x50 && bytes[1] === 0x4B)) {
      if (bytes[0] === 0xD0 && bytes[1] === 0xCF) return Promise.reject(new Error('This is an old .doc file (Word 97-2003), or a password-protected one. Open it in Word or LibreOffice and save it as .docx, then drop it here again.'));
      return Promise.reject(new Error('This file is not a .docx document.'));
    }
    var images = [], mode = opts.images || 'files', base = opts.base || 'document', n = 0;
    var convertImage = mammoth.images.imgElement(function (image) {
      if (mode === 'drop') return Promise.resolve({ src: '' });
      return image.readAsArrayBuffer().then(function (buf) {
        n++;
        var type = image.contentType || 'application/octet-stream', ext = IMAGE_EXT[type] || 'bin';
        var u8 = new Uint8Array(buf);
        if (mode === 'inline' && !/emf|wmf|tif/.test(ext)) {
          var bin = '';
          for (var i = 0; i < u8.length; i += 0x8000) bin += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
          return { src: 'data:' + type + ';base64,' + btoa(bin) };
        }
        var name = 'images/' + base + '-' + n + '.' + ext;
        images.push({ name: name, bytes: u8, type: type });
        return { src: name };
      });
    });
    return mammoth.convertToHtml({ arrayBuffer: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) },
      { styleMap: STYLE_MAP, convertImage: convertImage, ignoreEmptyParagraphs: true })
      .then(function (r) {
        var notes = r.messages.filter(function (m) { return !/^Unrecognised (paragraph|run|table) style/.test(m.message); }).map(function (m) { return m.message; });
        return { html: r.value, images: images, messages: notes };
      }, function (e) {
        throw new Error(/central directory|zip/i.test(String(e && e.message)) ? 'The document could not be opened (the file looks damaged).' : 'The document could not be read: ' + (e && e.message || e));
      });
  }

  // ---------- pasted content ----------
  function isWordHtml(html) { return /urn:schemas-microsoft-com:office|class="?Mso|mso-/i.test(html.slice(0, 200000)); }
  function isGoogleDocsHtml(html) { return /docs-internal-guid/.test(html); }

  function styleOf(el) { return (el.getAttribute('style') || '').toLowerCase(); }

  function wrap(el, tag) {
    var w = el.ownerDocument.createElement(tag);
    while (el.firstChild) w.appendChild(el.firstChild);
    el.appendChild(w);
  }

  /** Google Docs puts bold, italic and strike-through in inline styles and wraps everything in <b style="font-weight:normal">. */
  function fixGoogleDocs(doc) {
    doc.querySelectorAll('b[id^="docs-internal-guid"]').forEach(function (b) {
      while (b.firstChild) b.parentNode.insertBefore(b.firstChild, b);
      b.remove();
    });
    doc.querySelectorAll('span[style]').forEach(function (s) {
      var st = styleOf(s);
      if (/font-weight:\s*(700|800|900|bold)/.test(st)) wrap(s, 'strong');
      if (/font-style:\s*italic/.test(st)) wrap(s, 'em');
      if (/text-decoration[^;]*line-through/.test(st)) wrap(s, 's');
      if (/vertical-align:\s*super/.test(st)) wrap(s, 'sup');
      if (/vertical-align:\s*sub/.test(st)) wrap(s, 'sub');
      if (/font-family:[^;]*(courier|consolas|mono)/.test(st) && !s.closest('pre')) wrap(s, 'code');
    });
    // Headings in Google Docs often hold their text in a bold span; the heading is already bold.
    doc.querySelectorAll('h1 strong, h2 strong, h3 strong, h4 strong, h5 strong, h6 strong').forEach(function (s) {
      while (s.firstChild) s.parentNode.insertBefore(s.firstChild, s);
      s.remove();
    });
  }

  /** Word desktop clipboard: lists are paragraphs with mso-list styles and a typed bullet; rebuild real lists. */
  function fixWord(doc) {
    doc.querySelectorAll('style, xml, meta, link, title').forEach(function (n) { n.remove(); });
    doc.querySelectorAll('o\\:p').forEach(function (n) { n.remove(); });
    doc.querySelectorAll('p.MsoTitle, p.MsoTitleCxSpFirst').forEach(function (p) { retag(p, 'h1'); });
    doc.querySelectorAll('p.MsoSubtitle').forEach(function (p) { retag(p, 'p'); });
    doc.querySelectorAll('p.MsoQuote, p.MsoIntenseQuote').forEach(function (p) {
      var bq = doc.createElement('blockquote'); p.parentNode.insertBefore(bq, p); bq.appendChild(p);
    });
    var items = [];
    doc.querySelectorAll('p').forEach(function (p) {
      var st = p.getAttribute('style') || '';
      var m = /mso-list:\s*l(\d+)\s+level(\d+)/i.exec(st);
      if (!m && !/MsoListParagraph/.test(p.className)) return;
      var marker = p.querySelector('span[style*="mso-list:Ignore"], span[style*="mso-list: Ignore"]');
      var text = marker ? marker.textContent.replace(/ /g, ' ').trim() : '';
      if (marker) {
        // the marker span sits inside the conditional block; drop it and its wrapper spans
        var top = marker;
        while (top.parentNode && top.parentNode !== p && top.parentNode.childNodes.length === 1) top = top.parentNode;
        top.remove();
      }
      items.push({ p: p, list: m ? m[1] : '0', level: m ? Number(m[2]) : 1, ordered: /^\(?([0-9]{1,3}|[a-z]{1,2}|[ivxlc]{1,6})[.)]$/i.test(text) });
    });
    // group consecutive list paragraphs (siblings) into nested lists
    var i = 0;
    while (i < items.length) {
      var group = [items[i]];
      while (i + group.length < items.length) {
        var prev = group[group.length - 1].p, next = items[i + group.length].p, s = prev.nextSibling;
        while (s && s.nodeType === 3 && !s.textContent.trim()) s = s.nextSibling;
        if (s !== next) break;
        group.push(items[i + group.length]);
      }
      buildList(doc, group);
      i += group.length;
    }
    doc.querySelectorAll('img').forEach(function (img) {
      if (/^file:|^cid:/i.test(img.getAttribute('src') || '')) img.setAttribute('data-unreadable', '1');
    });
  }

  function retag(el, tag) {
    var n = el.ownerDocument.createElement(tag);
    while (el.firstChild) n.appendChild(el.firstChild);
    el.parentNode.replaceChild(n, el);
    return n;
  }

  function buildList(doc, group) {
    var first = group[0].p, root = null, stack = [];
    group.forEach(function (it) {
      var li = doc.createElement('li');
      while (it.p.firstChild) li.appendChild(it.p.firstChild);
      while (stack.length && stack[stack.length - 1].level > it.level) stack.pop();
      var top = stack[stack.length - 1];
      if (!top || top.level < it.level) {
        var list = doc.createElement(it.ordered ? 'ol' : 'ul');
        if (top) {
          var lastLi = top.el.lastElementChild || top.el.appendChild(doc.createElement('li'));
          lastLi.appendChild(list);
        } else root = list;
        stack.push({ level: it.level, el: list });
        top = stack[stack.length - 1];
      }
      top.el.appendChild(li);
    });
    first.parentNode.insertBefore(root, first);
    group.forEach(function (it) { it.p.remove(); });
  }

  /** Clean pasted HTML. Returns { html, source: 'word' | 'google-docs' | 'html', unreadableImages }. */
  function cleanPastedHtml(html) {
    var doc = new DOMParser().parseFromString(String(html).replace(/<!--StartFragment-->|<!--EndFragment-->/g, ''), 'text/html');
    var source = isGoogleDocsHtml(html) ? 'google-docs' : isWordHtml(html) ? 'word' : 'html';
    if (source === 'google-docs') fixGoogleDocs(doc);
    if (source === 'word') fixWord(doc);
    var unreadable = doc.querySelectorAll('img[data-unreadable]').length;
    doc.querySelectorAll('img[data-unreadable]').forEach(function (img) { img.remove(); });
    doc.querySelectorAll('script, style, meta, link, title').forEach(function (n) { n.remove(); });
    return { html: doc.body.innerHTML, source: source, unreadableImages: unreadable };
  }

  // ---------- HTML to Markdown ----------
  function hasMergedCells(table) {
    return Array.prototype.some.call(table.querySelectorAll('td, th'), function (c) {
      return (Number(c.getAttribute('rowspan')) || 1) > 1 || (Number(c.getAttribute('colspan')) || 1) > 1;
    }) || !!table.querySelector('td table, th table, td ul, td ol, th ul, th ol, td pre');
  }

  function cellHtml(cell) {
    var parts = [];
    cell.childNodes.forEach(function (n) {
      if (n.nodeType === 1 && n.nodeName === 'P') parts.push(n.innerHTML.trim());
      else if (n.nodeType === 1) parts.push(n.outerHTML);
      else if (n.textContent.trim()) parts.push(n.textContent.trim());
    });
    return parts.filter(Boolean).join('<br>');
  }

  function makeService(opts) {
    var td = new global.TurndownService({ headingStyle: 'atx', hr: '---', bulletListMarker: '-', codeBlockStyle: 'fenced', emDelimiter: '*', strongDelimiter: '**' });
    td.use(global.turndownPluginGfm.gfm);
    td.remove(['script', 'style', 'noscript', 'template']);
    var notes = { order: {}, count: 0 };
    function noteLabel(id) {
      if (!notes.order[id]) notes.order[id] = ++notes.count;
      return notes.order[id];
    }
    td.addRule('strike', {
      filter: ['s', 'del', 'strike'],
      replacement: function (content) { return content.trim() ? '~~' + content + '~~' : content; }
    });
    td.addRule('pre', {
      filter: function (node) { return node.nodeName === 'PRE'; },
      replacement: function (content, node) {
        var text = node.textContent.replace(/\n$/, '');
        var fence = /```/.test(text) ? '````' : '```';
        return '\n\n' + fence + '\n' + text + '\n' + fence + '\n\n';
      }
    });
    td.addRule('tightListItem', {
      filter: 'li',
      replacement: function (content, node, options) {
        content = content.replace(/^\n+/, '').replace(/\n+$/, '\n').replace(/\n/gm, '\n  ');
        var prefix = options.bulletListMarker + ' ';
        var parent = node.parentNode;
        if (parent.nodeName === 'OL') {
          var start = parent.getAttribute('start');
          var index = Array.prototype.indexOf.call(parent.children, node);
          prefix = (start ? Number(start) + index : index + 1) + '. ';
          content = content.replace(/\n  /g, '\n   ');
        }
        return prefix + content + (node.nextSibling && !/\n$/.test(content) ? '\n' : '');
      }
    });
    // Footnote and endnote references: <sup><a href="#footnote-3">[1]</a></sup> -> [^1]
    td.addRule('noteRef', {
      filter: function (node) {
        var a = node.nodeName === 'SUP' ? node.querySelector('a[href^="#footnote-"], a[href^="#endnote-"]') : null;
        return !!a && node.textContent.trim() === a.textContent.trim();
      },
      replacement: function (content, node) {
        var a = node.querySelector('a');
        return '[^' + noteLabel(a.getAttribute('href').slice(1)) + ']';
      }
    });
    td.addRule('noteBackLink', {
      filter: function (node) { return node.nodeName === 'A' && /^#(footnote|endnote)-ref-/.test(node.getAttribute('href') || ''); },
      replacement: function () { return ''; }
    });
    td.addRule('noteList', {
      filter: function (node) {
        return node.nodeName === 'OL' && node.children.length > 0 &&
          Array.prototype.every.call(node.children, function (li) { return /^(footnote|endnote)-/.test(li.id || ''); });
      },
      replacement: function (content, node) {
        var out = Array.prototype.map.call(node.children, function (li) {
          var label = noteLabel(li.id);
          var body = td.turndown(li.innerHTML).replace(/\s*↑\s*$/, '').trim().replace(/\n/g, '\n    ');
          return '[^' + label + ']: ' + body;
        });
        return '\n\n' + out.join('\n') + '\n\n';
      }
    });
    // Word bookmarks (table of contents, cross-references) point nowhere in Markdown: keep the text.
    td.addRule('bookmarkLinks', {
      filter: function (node) { return node.nodeName === 'A' && /^#(_|bookmark)/i.test(node.getAttribute('href') || ''); },
      replacement: function (content) { return content; }
    });
    td.addRule('emptyLinks', {
      filter: function (node) { return node.nodeName === 'A' && !node.textContent.trim() && !node.querySelector('img'); },
      replacement: function () { return ''; }
    });
    td.addRule('emptyImages', {
      filter: function (node) { return node.nodeName === 'IMG' && !node.getAttribute('src'); },
      replacement: function () { return ''; }
    });
    td.addRule('underline', {
      filter: ['u', 'ins'],
      replacement: function (content) { return opts.underline ? '<u>' + content + '</u>' : content; }
    });
    // Tables: a pipe table with the first row as header; tables with merged cells or lists inside stay HTML so nothing is lost.
    td.addRule('table', {
      filter: 'table',
      replacement: function (content, node) {
        var rows = Array.prototype.filter.call(node.rows, function (r) { return r.cells.length; });
        if (!rows.length) return '';
        if (hasMergedCells(node)) {
          notes.htmlTables = (notes.htmlTables || 0) + 1;
          var h = rows.map(function (r) {
            return '  <tr>' + Array.prototype.map.call(r.cells, function (c) {
              var tag = c.nodeName.toLowerCase(), attrs = '';
              ['rowspan', 'colspan'].forEach(function (a) { var v = c.getAttribute(a); if (v && v !== '1') attrs += ' ' + a + '="' + v + '"'; });
              return '<' + tag + attrs + '>' + cellHtml(c) + '</' + tag + '>';
            }).join('') + '</tr>';
          });
          return '\n\n<table>\n' + h.join('\n') + '\n</table>\n\n';
        }
        var width = Math.max.apply(null, rows.map(function (r) { return r.cells.length; }));
        var md = rows.map(function (r) {
          var cells = Array.prototype.map.call(r.cells, function (c) {
            return td.turndown(cellHtml(c) || '').trim().replace(/ *\n+ */g, '<br>').replace(/\|/g, '\\|');
          });
          while (cells.length < width) cells.push('');
          return '| ' + cells.join(' | ') + ' |';
        });
        var sep = '|' + new Array(width + 1).join(' --- |');
        md.splice(1, 0, sep);
        return '\n\n' + md.join('\n') + '\n\n';
      }
    });
    td.notes = notes;
    return td;
  }

  function tidy(md) {
    return md.replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').replace(/^\s+|\s+$/g, '') + '\n';
  }

  /** HTML to Markdown. Returns { markdown, stats }. */
  function htmlToMarkdown(html, opts) {
    opts = opts || {};
    var td = makeService(opts);
    var doc = new DOMParser().parseFromString('<body>' + String(html) + '</body>', 'text/html');
    // <li><p>text</p></li> (Google Docs, many editors) would give a loose list with blank lines between items.
    doc.querySelectorAll('li').forEach(function (li) {
      var kids = Array.prototype.filter.call(li.childNodes, function (n) { return n.nodeType === 1 || n.textContent.trim(); });
      if (kids.length && kids[0].nodeName === 'P' && kids.filter(function (n) { return n.nodeName === 'P'; }).length === 1) {
        var p = kids[0];
        while (p.firstChild) li.insertBefore(p.firstChild, p);
        p.remove();
      }
    });
    var md = tidy(td.turndown(doc.body));
    var body = md.replace(/```[\s\S]*?```/g, '');
    var stats = {
      words: (body.replace(/!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|[#*_>|`\-]/g, ' ').match(/[\p{L}\p{N}][\p{L}\p{N}'’.-]*/gu) || []).length,
      headings: (body.match(/^#{1,6} /gm) || []).length,
      tables: (body.match(/^\| --- \|/gm) || []).length + (td.notes.htmlTables || 0),
      htmlTables: td.notes.htmlTables || 0,
      images: (md.match(/!\[[^\]]*\]\(/g) || []).length,
      footnotes: td.notes.count
    };
    return { markdown: md, stats: stats };
  }

  /** One .docx file to Markdown. Returns a Promise of { name, markdown, images, stats, messages, props }. */
  function convertDocx(bytes, name, opts) {
    opts = opts || {};
    var base = slug(name);
    var props = global.fflate ? docProps(bytes, global.fflate.unzipSync) : {};
    return docxToHtml(bytes, { images: opts.images, base: base }).then(function (r) {
      var out = htmlToMarkdown(r.html, opts);
      var md = out.markdown;
      if (opts.frontMatter) md = frontMatter(props, (/^# (.+)$/m.exec(md) || [])[1]) + md;
      return { name: base + '.md', base: base, markdown: md, images: r.images, stats: out.stats, messages: r.messages, props: props };
    });
  }

  /** Pasted HTML (Word, Google Docs or any page) to Markdown. */
  function convertPasted(html, opts) {
    var c = cleanPastedHtml(html);
    var out = htmlToMarkdown(c.html, opts || {});
    out.source = c.source;
    out.unreadableImages = c.unreadableImages;
    return out;
  }

  global.PandapiDocx = { docxToHtml: docxToHtml, docProps: docProps, frontMatter: frontMatter, cleanPastedHtml: cleanPastedHtml,
    htmlToMarkdown: htmlToMarkdown, convertDocx: convertDocx, convertPasted: convertPasted, slug: slug, STYLE_MAP: STYLE_MAP };
})(typeof window !== 'undefined' ? window : this);
