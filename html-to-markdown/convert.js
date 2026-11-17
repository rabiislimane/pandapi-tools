/* HTML to Markdown conversion core (browser). Uses Turndown + GFM plugin + Mozilla Readability, all vendored. */
(function (global) {
  'use strict';

  var DROP_TAGS = ['script', 'style', 'noscript', 'template', 'iframe', 'object', 'embed', 'canvas', 'svg', 'form', 'button', 'input', 'select', 'textarea', 'link', 'meta'];

  function looksLikeFullPage(html) { return /<(html|body|head)[\s>]/i.test(html) || /<(nav|header|footer|aside)[\s>]/i.test(html); }

  var REL = 'pandapi-rel:';
  function absolutize(doc, base) {
    var attrs = [['a', 'href'], ['img', 'src'], ['source', 'src']];
    attrs.forEach(function (pair) {
      doc.querySelectorAll(pair[0] + '[' + pair[1] + ']').forEach(function (el) {
        var v = el.getAttribute(pair[1]);
        if (!v || /^(#|mailto:|tel:|javascript:|data:)/i.test(v)) return;
        if (!base) {
          // Keep relative links relative: protect them from being resolved against this tool's own address.
          if (!/^[a-z][a-z0-9+.-]*:|^\/\//i.test(v)) el.setAttribute(pair[1], REL + v);
          return;
        }
        try { el.setAttribute(pair[1], new URL(v, base).href); } catch (e) { /* keep as is */ }
      });
    });
  }

  function makeService(opts) {
    var td = new global.TurndownService({
      headingStyle: 'atx', hr: '---', bulletListMarker: '-', codeBlockStyle: 'fenced', emDelimiter: '*', strongDelimiter: '**',
      linkStyle: opts.referenceLinks ? 'referenced' : 'inlined', linkReferenceStyle: 'full'
    });
    td.use(global.turndownPluginGfm.gfm);
    td.remove(DROP_TAGS);
    if (opts.dropImages) td.remove(['img', 'picture', 'figure > img']);
    // Fenced code blocks keep a language from class="language-x" / "lang-x".
    td.addRule('fencedWithLang', {
      // Any <pre>, with or without an inner <code> (Sphinx, Pygments and many CMSs use bare <pre> with spans).
      filter: function (node) { return node.nodeName === 'PRE'; },
      replacement: function (content, node) {
        var code = node.querySelector('code') || node;
        var classes = (code.getAttribute('class') || '') + ' ' + (node.getAttribute('class') || '');
        for (var a = node.parentNode, k = 0; a && a.getAttribute && k < 3; a = a.parentNode, k++) classes += ' ' + (a.getAttribute('class') || '');
        var m = /(?:^|\s)(?:language|lang|highlight(?:-source)?)-([\w+#]+)/.exec(classes);
        var text = code.textContent.replace(/\n$/, '');
        var fence = /```/.test(text) ? '````' : '```';
        var lang = m ? m[1].replace(/^(python3|default|none|text)$/, function (x) { return x === 'python3' ? 'python' : ''; }) : '';
        return '\n\n' + fence + lang + '\n' + text + '\n' + fence + '\n\n';
      }
    });
    // List items with a single space after the marker ("- item", "1. item").
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
    // Links with no text (icons) are dropped instead of producing [](url).
    td.addRule('emptyLinks', {
      filter: function (node) { return node.nodeName === 'A' && !node.textContent.trim() && !node.querySelector('img'); },
      replacement: function () { return ''; }
    });
    return td;
  }

  function tidy(md) {
    return md
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/^\s+|\s+$/g, '') + '\n';
  }

  function yamlString(s) { return '"' + String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\s+/g, ' ').trim() + '"'; }

  /**
   * convert(html, opts) -> { markdown, title, usedReadability, note }
   * opts: { mainContent, dropImages, referenceLinks, frontMatter, baseUrl }
   */
  function convert(html, opts) {
    opts = opts || {};
    html = String(html || '');
    if (!html.trim()) return { markdown: '', title: '', usedReadability: false, note: '' };
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var base = (opts.baseUrl || '').trim();
    if (base && !/^https?:\/\//i.test(base)) base = 'https://' + base;
    absolutize(doc, base);
    var title = (doc.querySelector('title') && doc.querySelector('title').textContent.trim()) || '';
    var used = false, note = '';
    var root = doc.body;
    if (opts.mainContent) {
      if (looksLikeFullPage(html)) {
        try {
          var art = new global.Readability(doc.cloneNode(true), { charThreshold: 200, keepClasses: true }).parse();
          if (art && art.content && art.textContent && art.textContent.trim().length > 80) {
            root = new DOMParser().parseFromString(art.content, 'text/html').body;
            title = (art.title || title || '').trim();
            used = true;
          } else {
            note = 'Main-content mode found no clear article, so the whole page was converted.';
          }
        } catch (e) { note = 'Main-content mode failed on this page, so the whole page was converted.'; }
      } else {
        note = 'Looks like a snippet, so it was converted as is (main-content mode is for whole pages).';
      }
    }
    var md = tidy(makeService(opts).turndown(root.innerHTML).split(REL).join(''));
    if (used && title) {
      var firstHeading = /^#\s+(.+)$/m.exec(md);
      if (!firstHeading || firstHeading[1].trim().toLowerCase() !== title.toLowerCase()) md = '# ' + title + '\n\n' + md;
    }
    if (opts.frontMatter) {
      var fm = ['---'];
      if (title) fm.push('title: ' + yamlString(title));
      if (base) fm.push('source: ' + yamlString(base));
      fm.push('converted: ' + new Date().toISOString().slice(0, 10));
      fm.push('---', '');
      md = fm.join('\n') + '\n' + md;
    }
    return { markdown: md, title: title, usedReadability: used, note: note };
  }

  global.PandapiHtmlToMd = { convert: convert, looksLikeFullPage: looksLikeFullPage };
})(window);
