/* Pandapi Tools: Link Extractor. Finds every link in pasted HTML, plain text or a sitemap XML, in the browser. */
(function (root) {
  'use strict';

  var TRACKING = /^(utm_[a-z_]+|fbclid|gclid|gbraid|wbraid|dclid|msclkid|mc_cid|mc_eid|yclid|igshid|_hsenc|_hsmi|mkt_tok|ref_src)$/i;
  var COLS = {
    html: ['URL', 'Anchor text', 'Type', 'Nofollow', 'Rel', 'Target', 'Title', 'Domain', 'Count', 'Tag', 'Source'],
    text: ['URL', 'Type', 'Domain', 'Count', 'Source'],
    sitemap: ['URL', 'Kind', 'Last modified', 'Change frequency', 'Priority', 'Images', 'Domain', 'Source']
  };

  /** 'sitemap' for <urlset>/<sitemapindex>, 'html' when it holds tags with links, else 'text'. */
  function detect(input) {
    var s = String(input || '').slice(0, 200000);
    if (/<(?:[a-z]+:)?(urlset|sitemapindex)[\s>]/i.test(s)) return 'sitemap';
    if (/<(a|area|img|link|html|body|div|p|li|table|span)[\s>\/]/i.test(s)) return 'html';
    return 'text';
  }

  function safeURL(raw, base) {
    try { return base ? new URL(raw, base) : new URL(raw); } catch (e) { return null; }
  }

  function hostOf(h) { return String(h || '').toLowerCase().replace(/^www\./, ''); }

  /** Clean a URL: drop #fragment and tracking parameters when asked. Returns the string to show and to dedupe on. */
  function cleanURL(u, opts) {
    if (!u || !/^https?:$/.test(u.protocol)) return u ? u.href : '';
    var c = new URL(u.href);
    if (opts.stripHash) c.hash = '';
    if (opts.stripTracking) {
      var keep = [];
      c.searchParams.forEach(function (v, k) { if (!TRACKING.test(k)) keep.push([k, v]); });
      if (keep.length !== Array.from(c.searchParams.keys()).length) {
        c.search = keep.length ? '?' + keep.map(function (p) { return encodeURIComponent(p[0]) + '=' + encodeURIComponent(p[1]); }).join('&') : '';
      }
    }
    return c.href;
  }

  function classify(raw, u, baseHost) {
    var r = String(raw || '').trim();
    if (/^mailto:/i.test(r)) return 'Email';
    if (/^tel:/i.test(r)) return 'Phone';
    if (/^javascript:/i.test(r)) return 'JavaScript';
    if (/^#/.test(r)) return 'Same page (#)';
    if (/^(data|blob):/i.test(r)) return 'Data';
    if (!u) return baseHost ? 'Invalid' : 'Relative';
    if (!/^https?:$/.test(u.protocol)) return u.protocol.replace(':', '').toUpperCase();
    if (!baseHost) return /^[a-z][a-z0-9+.\-]*:/i.test(r) || /^\/\//.test(r) ? 'Full URL' : 'Relative';
    return hostOf(u.hostname) === baseHost ? 'Internal' : 'External';
  }

  function textOf(el) {
    var t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!t) {
      var img = el.querySelector && el.querySelector('img[alt]');
      if (img && img.getAttribute('alt').trim()) t = '[image] ' + img.getAttribute('alt').trim();
      else if (el.querySelector && el.querySelector('img,svg,picture')) t = '[image]';
      else if (el.getAttribute && el.getAttribute('aria-label')) t = el.getAttribute('aria-label').trim();
    }
    return t;
  }

  /** Find the page's own address: <base href>, canonical, og:url. */
  function pageBase(doc) {
    var b = doc.querySelector('base[href]'), c = doc.querySelector('link[rel~="canonical"][href]'), og = doc.querySelector('meta[property="og:url"][content]');
    var cands = [b && b.getAttribute('href'), c && c.getAttribute('href'), og && og.getAttribute('content')];
    for (var i = 0; i < cands.length; i++) { var u = cands[i] && safeURL(cands[i]); if (u && /^https?:$/.test(u.protocol)) return u.href; }
    return '';
  }

  function fromHTML(html, opts, source) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var base = opts.base || pageBase(doc) || '';
    var baseURL = base ? safeURL(base) : null;
    var baseHost = baseURL ? hostOf(baseURL.hostname) : '';
    var out = [];
    function add(el, attr, tag, text) {
      var raw = (el.getAttribute(attr) || '').trim();
      if (!raw) return;
      if (attr === 'srcset') raw = raw.split(',')[0].trim().split(/\s+/)[0];
      var u = safeURL(raw, baseURL ? baseURL.href : undefined);
      var rel = (el.getAttribute('rel') || '').toLowerCase().replace(/\s+/g, ' ').trim();
      out.push({
        raw: raw, u: u, type: classify(raw, u, baseHost), text: text, rel: rel,
        nofollow: /\b(nofollow|sponsored|ugc)\b/.test(rel) ? 'yes' : '',
        target: el.getAttribute('target') || '', title: (el.getAttribute('title') || '').trim(), tag: tag, source: source || ''
      });
    }
    doc.querySelectorAll('a[href], area[href]').forEach(function (a) { add(a, 'href', a.tagName.toLowerCase(), textOf(a)); });
    if (opts.images) doc.querySelectorAll('img').forEach(function (i) { add(i, i.getAttribute('src') ? 'src' : 'srcset', 'img', (i.getAttribute('alt') || '').trim()); });
    if (opts.resources) {
      doc.querySelectorAll('link[href]').forEach(function (l) { add(l, 'href', 'link ' + (l.getAttribute('rel') || '').toLowerCase(), ''); });
      doc.querySelectorAll('script[src], iframe[src], source[src], video[src], audio[src]').forEach(function (s) { add(s, 'src', s.tagName.toLowerCase(), ''); });
      doc.querySelectorAll('form[action]').forEach(function (f) { add(f, 'action', 'form', ''); });
    }
    return { kind: 'html', base: base, items: out };
  }

  /** URLs in plain text: http(s)://..., www.... Trailing punctuation and unbalanced brackets are trimmed. */
  function fromText(text, opts, source) {
    var re = /\b(?:https?:\/\/|www\.)[^\s<>"'`{}|\\^  -​　]+/gi, m, out = [];
    while ((m = re.exec(text))) {
      var s = m[0];
      for (;;) {
        var last = s.slice(-1);
        if (/[.,;:!?*'"»”’]/.test(last)) { s = s.slice(0, -1); continue; }
        var pairs = { ')': '(', ']': '[' };
        if (pairs[last] && s.split(pairs[last]).length < s.split(last).length) { s = s.slice(0, -1); continue; }
        break;
      }
      var raw = /^www\./i.test(s) ? 'https://' + s : s;
      var u = safeURL(raw);
      if (!u || !/\./.test(u.hostname)) continue;
      out.push({ raw: s, u: u, type: 'Web', source: source || '' });
    }
    if (opts.emails !== false) {
      var er = /[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,24}\b/gi;
      while ((m = er.exec(text))) {
        var before = text.slice(Math.max(0, m.index - 12), m.index);
        if (/\/\/[^\s]*$/.test(before)) continue; // user@host inside a URL
        out.push({ raw: 'mailto:' + m[0], u: safeURL('mailto:' + m[0]), type: 'Email', source: source || '' });
      }
    }
    return { kind: 'text', base: '', items: out };
  }

  function fromSitemap(xml, opts, source) {
    var doc = new DOMParser().parseFromString(xml, 'application/xml');
    if (doc.getElementsByTagName('parsererror').length) {
      // Broken XML: still pull every <loc>.
      var out0 = [], re = /<(?:[a-z]+:)?loc>\s*(?:<!\[CDATA\[)?\s*([^<\]]+?)\s*(?:\]\]>)?\s*<\/(?:[a-z]+:)?loc>/gi, m;
      while ((m = re.exec(xml))) out0.push({ raw: m[1], u: safeURL(m[1].replace(/&amp;/g, '&')), kind: 'Page', source: source || '' });
      return { kind: 'sitemap', base: '', items: out0, broken: true };
    }
    var out = [];
    function child(el, name) {
      for (var c = el.firstElementChild; c; c = c.nextElementSibling) if (c.localName === name) return (c.textContent || '').trim();
      return '';
    }
    var all = doc.getElementsByTagName('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.localName !== 'url' && el.localName !== 'sitemap') continue;
      var loc = child(el, 'loc');
      if (!loc) continue;
      var imgs = 0;
      for (var c = el.firstElementChild; c; c = c.nextElementSibling) if (c.localName === 'image') imgs++;
      out.push({ raw: loc, u: safeURL(loc), kind: el.localName === 'sitemap' ? 'Sitemap' : 'Page', lastmod: child(el, 'lastmod'),
        changefreq: child(el, 'changefreq'), priority: child(el, 'priority'), images: imgs || '', source: source || '' });
    }
    return { kind: 'sitemap', base: '', items: out };
  }

  /**
   * Extract links. inputs: a string or [{name, text}] (several saved pages).
   * opts: { base, images, resources, dedupe (true), stripHash (true), stripTracking (false), emails (true), kind ('auto') }
   * Returns { kind, base, columns, rows, domains: {columns, rows}, total, unique, counts: {type: n} }.
   */
  function extract(inputs, opts) {
    opts = Object.assign({ dedupe: true, stripHash: true }, opts || {});
    if (typeof inputs === 'string') inputs = [{ name: '', text: inputs }];
    var kind = null, base = '', items = [], broken = false;
    inputs.forEach(function (f) {
      var k = opts.kind && opts.kind !== 'auto' ? opts.kind : detect(f.text);
      kind = kind && kind !== k ? 'mixed' : k;
      var r = k === 'sitemap' ? fromSitemap(f.text, opts, f.name) : k === 'html' ? fromHTML(f.text, opts, f.name) : fromText(f.text, opts, f.name);
      if (r.base && !base) base = r.base;
      if (r.broken) broken = true;
      items = items.concat(r.items);
    });
    if (kind === 'mixed') kind = 'html';
    kind = kind || 'text';
    var multi = inputs.length > 1;
    var rows = [], index = {}, counts = {};
    items.forEach(function (it) {
      var url = it.u ? cleanURL(it.u, opts) : it.raw;
      if (!it.u && it.type === 'Relative') url = it.raw;
      var key = opts.dedupe ? url : rows.length;
      var row = index[key];
      if (row && opts.dedupe) {
        row.Count++;
        if (kind === 'html' && !row['Anchor text'] && it.text) row['Anchor text'] = it.text;
        if (multi && it.source && row.Source.split('; ').indexOf(it.source) < 0) row.Source += '; ' + it.source;
        return;
      }
      var domain = it.u && it.u.hostname ? it.u.hostname.toLowerCase() : '';
      if (kind === 'sitemap') row = { URL: url, Kind: it.kind, 'Last modified': it.lastmod || '', 'Change frequency': it.changefreq || '', Priority: it.priority || '', Images: it.images || '', Domain: domain, Source: it.source };
      else if (kind === 'html') row = { URL: url, 'Anchor text': it.text || '', Type: it.type || (it.kind ? 'Sitemap ' + it.kind.toLowerCase() : 'Web'), Nofollow: it.nofollow || '', Rel: it.rel || '', Target: it.target || '', Title: it.title || '', Domain: domain, Count: 1, Tag: it.tag || (it.kind ? 'sitemap' : 'a'), Source: it.source };
      else row = { URL: url, Type: it.type, Domain: domain, Count: 1, Source: it.source };
      index[key] = row;
      rows.push(row);
    });
    rows.forEach(function (r) { var t = r.Type || r.Kind; counts[t] = (counts[t] || 0) + 1; });
    var cols = COLS[kind].filter(function (c) {
      if (c === 'Source') return multi;
      if (c === 'Count') return opts.dedupe;
      if (kind === 'sitemap' && /Change|Priority|Images|Last/.test(c)) return rows.some(function (r) { return r[c] !== ''; });
      if (kind === 'html' && /^(Target|Title|Rel)$/.test(c)) return rows.some(function (r) { return r[c] !== ''; });
      return true;
    });
    var dmap = {};
    rows.forEach(function (r) { if (!r.Domain) return; var d = dmap[r.Domain] || (dmap[r.Domain] = { Domain: r.Domain, Links: 0, Nofollow: 0 }); d.Links++; if (r.Nofollow) d.Nofollow++; });
    var drows = Object.keys(dmap).map(function (k) { return dmap[k]; }).sort(function (a, b) { return b.Links - a.Links || (a.Domain < b.Domain ? -1 : 1); });
    return { kind: kind, base: base, columns: cols, rows: rows, total: items.length, unique: rows.length, counts: counts, broken: broken,
      domains: { columns: kind === 'html' ? ['Domain', 'Links', 'Nofollow'] : ['Domain', 'Links'], rows: drows } };
  }

  /** Filter rows: type ('all' | a Type/Kind value | 'internal' etc.), query (substring of URL or anchor text). */
  function filter(rows, type, query) {
    var q = String(query || '').toLowerCase().trim();
    return rows.filter(function (r) {
      if (type && type !== 'all' && (r.Type || r.Kind) !== type) return false;
      if (q && (r.URL + ' ' + (r['Anchor text'] || '')).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
  }

  function sortRows(rows, by) {
    var r = rows.slice();
    if (by === 'url') r.sort(function (a, b) { return a.URL < b.URL ? -1 : a.URL > b.URL ? 1 : 0; });
    else if (by === 'domain') r.sort(function (a, b) { return (a.Domain || '').localeCompare(b.Domain || '') || (a.URL < b.URL ? -1 : 1); });
    else if (by === 'count') r.sort(function (a, b) { return (b.Count || 0) - (a.Count || 0); });
    else if (by === 'lastmod') r.sort(function (a, b) { return String(b['Last modified'] || '').localeCompare(String(a['Last modified'] || '')); });
    return r;
  }

  root.PandapiLinks = { extract: extract, detect: detect, filter: filter, sortRows: sortRows, cleanURL: cleanURL };
})(typeof self !== 'undefined' ? self : this);
