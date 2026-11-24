/* Email extractor core. Pure functions; works in the browser (window.PandapiEmails) and in Node (module.exports).
   Finds email addresses in text, HTML, Word (.docx) and e-mail files, including mailto links and "name [at] domain [dot] com". */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api; else root.PandapiEmails = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var FREE = ('gmail.com googlemail.com yahoo.com ymail.com rocketmail.com hotmail.com outlook.com live.com msn.com aol.com icloud.com me.com mac.com ' +
    'proton.me protonmail.com pm.me gmx.com gmx.net gmx.de web.de mail.com mail.ru inbox.ru list.ru bk.ru yandex.com yandex.ru zoho.com qq.com 163.com 126.com ' +
    'sina.com naver.com daum.net hanmail.net orange.fr wanadoo.fr free.fr sfr.fr laposte.net libero.it virgilio.it alice.it tiscali.it t-online.de freenet.de ' +
    'comcast.net verizon.net att.net sbcglobal.net bellsouth.net cox.net charter.net earthlink.net btinternet.com sky.com virginmedia.com talktalk.net ' +
    'rediffmail.com seznam.cz wp.pl o2.pl interia.pl onet.pl tutanota.com tuta.io fastmail.com hey.com yahoo.co.uk yahoo.fr yahoo.de yahoo.es yahoo.it ' +
    'yahoo.ca yahoo.com.au yahoo.co.in yahoo.co.jp hotmail.co.uk hotmail.fr hotmail.de hotmail.it hotmail.es outlook.fr outlook.de live.co.uk live.fr ' +
    'shaw.ca rogers.com sympatico.ca videotron.ca bigpond.com optusnet.com.au xtra.co.nz uol.com.br bol.com.br terra.com.br').split(' ');
  var FREE_SET = {};
  FREE.forEach(function (d) { FREE_SET[d] = true; });
  var ROLE = /^(info|contact|contacts|contactus|hello|hi|hey|sales|support|help|helpdesk|service|services|customerservice|customer\.service|customer-service|care|office|admin|administrator|enquiries|enquiry|inquiries|inquiry|team|mail|email|general|business|partners|partnerships|press|media|pr|news|newsletter|marketing|careers|jobs|hr|recruiting|recruitment|billing|accounts|accounting|finance|invoices|orders|order|shop|store|bookings|booking|reservations|reception|feedback|webmaster|hostmaster|postmaster|privacy|legal|security|abuse|compliance|dpo|gdpr|noreply|no-reply|donotreply|do-not-reply|notifications|alerts|bounce|mailer-daemon|root|it|tech|events|studio|hq|logistics|shipping|returns|warehouse|purchasing|procurement|operations|ops|payroll|vendors|suppliers|accountspayable|accounts-payable|ap|ar|bonjour|kontakt|contacto|ventas|info\.[a-z]+)$/i;
  var NOREPLY = /^(noreply|no-reply|donotreply|do-not-reply|mailer-daemon|bounce[s]?)([._+-].*)?$/i;
  var BAD_TLD = /^(png|jpe?g|gif|svg|webp|avif|bmp|ico|tiff?|css|js|mjs|json|xml|html?|php|aspx?|pdf|zip|gz|mp4|mp3|woff2?|ttf|eot|map|txt|md)$/i;
  var EXAMPLE = /(^|\.)(example\.(com|org|net)|domain\.(com|tld)|email\.com|test\.com|yourdomain\.com|yoursite\.com|company\.com|sentry\.io|sentry-next\.wixpress\.com|wixpress\.com|localhost)$/i;
  var EMAIL_AT = /([A-Za-z0-9][A-Za-z0-9._%+'-]{0,63})@((?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.){1,8}[A-Za-z]{2,24})(?![A-Za-z0-9-])/;
  var MAX_SCAN = 20000000;

  function decodeEntities(s) {
    return String(s).replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, function (m, e) {
      if (e[0] === '#') { var n = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10); return n > 0 && n < 0x110000 ? String.fromCodePoint(n) : m; }
      var named = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', commat: '@', period: '.', lowbar: '_', hyphen: '-', dash: '-', plus: '+' };
      return Object.prototype.hasOwnProperty.call(named, e.toLowerCase()) ? named[e.toLowerCase()] : m;
    });
  }

  /** Turn written-out addresses back into real ones: "jane [at] acme [dot] com", "jane(at)acme.com", "jane at acme dot com". */
  function deobfuscate(text) {
    var s = String(text);
    s = s.replace(/\s*(?:\[|\(|\{|<)\s*(?:at|@|arroba|chez)\s*(?:\]|\)|\}|>)\s*/gi, '@');
    s = s.replace(/\s*(?:\[|\(|\{|<)\s*(?:dot|\.|punto|point)\s*(?:\]|\)|\}|>)\s*/gi, '.');
    // Plain words ("jane at acme dot com") only next to a hint like "email:" or with a local part that isn't a plain word,
    // so ordinary sentences ("look at this dot com boom") stay untouched.
    s = s.replace(/\b([A-Za-z0-9._%+-]{1,64})\s+(?:at|AT)\s+([A-Za-z0-9-]{1,63}(?:\s+(?:dot|DOT)\s+[A-Za-z0-9-]{1,63}){1,4})\b/g, function (m, a, b, off, all) {
      var parts = b.split(/\s+(?:dot|DOT)\s+/);
      if (!/^[A-Za-z]{2,24}$/.test(parts[parts.length - 1])) return m;
      var hint = /(e-?mail|mail|contact|write|reach|address)\s*(me|us)?\s*[:\-]?\s*(at\s*)?$/i.test(all.slice(Math.max(0, off - 30), off));
      return hint || /[0-9._%+-]/.test(a) ? a + '@' + parts.join('.') : m;
    });
    return s;
  }

  function isHtml(s) { return /<(?:a|p|div|span|td|li|br|body|html|table|meta)\b[^>]*>/i.test(String(s).slice(0, 200000)); }

  /** HTML to scan-able text; mailto links keep their link text as the name. */
  function fromHtml(html) {
    var names = {};
    String(html).replace(/<a\b[^>]*href\s*=\s*["']?\s*mailto:([^"'\s>?]+)[^>]*>([\s\S]*?)<\/a>/gi, function (m, addr, inner) {
      var a = safeDecode(decodeEntities(addr)).toLowerCase();
      var t = decodeEntities(inner.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
      if (t && t.indexOf('@') < 0 && t.length <= 80 && /[A-ZÀ-Þ]/.test(t) && !/^(email|e-mail|mail|contact|write to us|send|click here)/i.test(t)) names[a] = t;
      return m;
    });
    var text = String(html)
      .replace(/<(script|style|noscript|template)\b[\s\S]*?<\/\1>/gi, ' ')
      .replace(/<a\b[^>]*href\s*=\s*["']?\s*mailto:([^"'\s>]+)[^>]*>/gi, function (m, a) { return ' ' + a.split('?')[0] + ' '; })
      .replace(/<(br|\/p|\/div|\/li|\/tr|\/h\d|\/td)\b[^>]*>/gi, '\n')
      .replace(/<[^>]+>/g, ' ');
    return { text: decodeEntities(text), names: names };
  }

  function safeDecode(s) { try { return decodeURIComponent(s); } catch (e) { return s; } }

  /** Quoted-printable bodies of .eml files: soft line breaks and =XX bytes. */
  function decodeQuotedPrintable(s) {
    return String(s).replace(/=\r?\n/g, '').replace(/=([0-9A-F]{2})/g, function (m, h) { return String.fromCharCode(parseInt(h, 16)); });
  }

  /** Text of a .docx: body, headers, footers, footnotes, comments, plus mailto hyperlink targets. unzip: fflate.unzipSync. */
  function docxText(bytes, unzip) {
    if (!(bytes[0] === 0x50 && bytes[1] === 0x4B)) {
      if (bytes[0] === 0xD0 && bytes[1] === 0xCF) throw new Error('This is an old .doc file (Word 97-2003). Open it in Word or LibreOffice and save it as .docx, then drop it here again.');
      throw new Error('This file is not a .docx document.');
    }
    var files;
    try { files = unzip(bytes); } catch (e) { throw new Error('The document could not be opened (the file looks damaged).'); }
    var dec = new TextDecoder('utf-8');
    var names = Object.keys(files).filter(function (n) { return /^word\/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$/.test(n); });
    if (!names.length) throw new Error('This zip file is not a Word document (no word/document.xml).');
    names.sort(function (a, b) { return (a === 'word/document.xml' ? -1 : 0) - (b === 'word/document.xml' ? -1 : 0); });
    var out = names.map(function (n) {
      return decodeEntities(dec.decode(files[n])
        .replace(/<w:tab\/>/g, '\t').replace(/<w:br\/>/g, '\n').replace(/<\/w:p>/g, '\n').replace(/<[^>]+>/g, ''));
    }).join('\n');
    Object.keys(files).filter(function (n) { return /^word\/_rels\/.*\.rels$/.test(n); }).forEach(function (n) {
      (dec.decode(files[n]).match(/Target="mailto:[^"]+"/gi) || []).forEach(function (t) { out += '\n' + safeDecode(decodeEntities(t.slice(15, -1))).split('?')[0]; });
    });
    return out;
  }

  function classify(email) {
    var at = email.lastIndexOf('@'), local = email.slice(0, at), domain = email.slice(at + 1).toLowerCase();
    if (NOREPLY.test(local)) return 'no-reply';
    if (FREE_SET[domain]) return 'free mailbox';
    if (ROLE.test(local)) return 'role';
    return 'personal';
  }

  function cleanAddress(local, domain) {
    local = local.replace(/^[._'%+-]+/, '').replace(/[._'%+-]+$/, '');
    domain = domain.replace(/\.+$/, '').toLowerCase();
    if (!local || local.length > 64 || domain.length > 253 || /\.\./.test(local)) return null;
    var tld = domain.slice(domain.lastIndexOf('.') + 1);
    if (BAD_TLD.test(tld)) return null; // logo@2x.png, icon@3x.webp
    if (EXAMPLE.test(domain)) return null;
    if (/^[0-9a-f]{24,}$/i.test(local)) return null; // tracking and error-reporting ids
    if (/^(u00|x00)/i.test(local) || /%[0-9a-f]{2}/i.test(local)) return null;
    return local + '@' + domain;
  }

  /** Name written before the address on the same line: Jane Doe <jane@x.com>, "Doe, Jane" <...>, or after it: jane@x.com (Jane Doe). */
  var LEAD_WORD = /^(?:(?:Ask|Contact|Contacts|Email|E-mail|Mail|Message|Call|Write|Dear|Hi|Hello|Hey|Thanks|Thank|Please|Reach|From|To|Cc|By|Attn|Attention|Or|And|Our|Your|With|Via|Also|Cheers|Regards)\s+)+/;
  function nameNear(text, start, end) {
    var before = text.slice(Math.max(0, start - 90), start);
    var q = before.match(/"([^"<>@\n]{2,60})"\s*[<(\[]\s*(?:mailto:)?$/);
    if (q && /[A-Za-zÀ-ÿ]{2}/.test(q[1])) return q[1].trim();
    var m = before.match(/(?:^|[\n,;:]\s*|\b(?:from|to|cc):\s*)"?([A-Za-zÀ-ÖØ-öø-ÿ'’.\- ]{2,60}?)"?\s*[<(\[]\s*(?:mailto:)?$/i);
    if (m && /[A-Za-zÀ-ÿ]{2}/.test(m[1]) && m[1].trim().split(/\s+/).length <= 5) return m[1].trim();
    // "... is Lena Park (lena@x.com)" or "Packaging: Tom Becker, tom.becker@x.com": the capitalized words just before.
    // Without brackets the name must match the address ("Tom Becker" and tom.becker@), so headings and greetings aren't taken.
    var cap = before.match(/((?:[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’-]+\.?\s+){1,3}[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ'’-]+)\s*([<(\[]|,|:|\s[-–—|]|)\s*(?:mailto:)?$/);
    if (cap) {
      cap[1] = cap[1].replace(LEAD_WORD, '');
      if (!/\s/.test(cap[1].trim()) && !/[<(\[]/.test(cap[2])) cap = null;
    }
    if (cap) {
      if (/[<(\[]/.test(cap[2])) return cap[1].trim();
      var local = text.slice(start, end).split('@')[0].toLowerCase();
      var hit = cap[1].trim().split(/\s+/).some(function (w) { w = w.toLowerCase().replace(/[^a-z]/g, ''); return w.length >= 2 && local.indexOf(w) >= 0; });
      if (hit) return cap[1].trim();
    }
    var after = text.slice(end, end + 70).match(/^\s*[>)\]]?\s*\(([A-Za-zÀ-ÖØ-öø-ÿ'’.\- ]{2,50})\)/);
    if (after && after[1].trim().split(/\s+/).length <= 5) return after[1].trim();
    return '';
  }

  function lineAt(text, idx, cache) {
    // count newlines incrementally: matches come in order
    while (cache.pos < idx) { var n = text.indexOf('\n', cache.pos); if (n < 0 || n >= idx) { cache.pos = idx; break; } cache.line++; cache.pos = n + 1; }
    return cache.line;
  }

  /** Find addresses in one text. Returns [{ email, name, line }] in order. Linear: only looks around each '@'. */
  function findIn(text, opts) {
    opts = opts || {};
    var t = String(text);
    if (t.length > MAX_SCAN) t = t.slice(0, MAX_SCAN);
    if (opts.deobfuscate !== false) t = deobfuscate(t);
    t = t.replace(/%40/g, '@').replace(/\\u0040/gi, '@');
    var out = [], i = t.indexOf('@'), lastEnd = -1, cache = { pos: 0, line: 1 };
    while (i !== -1) {
      var from = Math.max(0, i - 65, lastEnd);
      var chunk = t.slice(from, i + 260);
      var m = chunk.match(EMAIL_AT);
      if (m) {
        var start = from + m.index, end = start + m[0].length;
        if (start <= i && end > i) {
          var email = cleanAddress(m[1], m[2]);
          if (email) {
            if (opts.lowercase !== false) email = email.toLowerCase();
            out.push({ email: email, name: nameNear(t, start, end), line: lineAt(t, start, cache) });
          }
          lastEnd = end;
          i = t.indexOf('@', end);
          continue;
        }
      }
      i = t.indexOf('@', i + 1);
    }
    return out;
  }

  /** sources: [{ name, parts: [{ text, where }] , names?: {email: name} }]. Returns table rows and a domain summary. */
  function extract(sources, opts) {
    opts = opts || {};
    var byEmail = {}, order = [], total = 0, multi = sources.length > 1;
    sources.forEach(function (src) {
      (src.parts || []).forEach(function (part) {
        var found = findIn(part.text, opts);
        found.forEach(function (f) {
          total++;
          var key = opts.lowercase === false ? f.email : f.email.toLowerCase();
          var where = [multi || src.file ? src.name : '', part.where ? part.where : (src.lines === false ? '' : 'line ' + f.line)].filter(Boolean).join(', ');
          var r = byEmail[key];
          if (!r) {
            r = byEmail[key] = { email: f.email, name: '', count: 0, sources: [] };
            order.push(r);
          }
          r.count++;
          if (!r.name) r.name = f.name || (src.names && src.names[key]) || '';
          if (r.sources.length < 5 && r.sources.indexOf(where) < 0) r.sources.push(where);
        });
        if (src.names) Object.keys(src.names).forEach(function (k) { if (byEmail[k] && !byEmail[k].name) byEmail[k].name = src.names[k]; });
      });
    });
    var rows = order.map(function (r) {
      var domain = r.email.slice(r.email.lastIndexOf('@') + 1).toLowerCase();
      return { Email: r.email, Name: r.name, Domain: domain, Type: classify(r.email), Count: r.count, Source: r.sources.join('; ') };
    });
    if (opts.dedupe === false) {
      // one row per occurrence, in order
      var flat = [];
      rows.forEach(function (r) { for (var k = 0; k < r.Count; k++) flat.push(Object.assign({}, r, { Count: 1 })); });
      rows = flat;
    }
    var counts = { personal: 0, role: 0, 'free mailbox': 0, 'no-reply': 0 };
    rows.forEach(function (r) { counts[r.Type]++; });
    var dom = {};
    rows.forEach(function (r) { (dom[r.Domain] = dom[r.Domain] || { Domain: r.Domain, Emails: 0, Type: FREE_SET[r.Domain] ? 'free mailbox' : 'company' }).Emails++; });
    var domains = Object.keys(dom).map(function (k) { return dom[k]; }).sort(function (a, b) { return b.Emails - a.Emails || (a.Domain < b.Domain ? -1 : 1); });
    return { rows: rows, total: total, unique: order.length, counts: counts, domains: { columns: ['Domain', 'Emails', 'Type'], rows: domains },
      columns: ['Email', 'Name', 'Domain', 'Type', 'Count', 'Source'] };
  }

  /** Filters shown on the page: types to drop, a domain or text to keep, sort order. */
  function filter(rows, f) {
    f = f || {};
    var q = String(f.query || '').trim().toLowerCase();
    var out = rows.filter(function (r) {
      if (f.drop && f.drop[r.Type]) return false;
      if (q && (r.Email + ' ' + r.Name).toLowerCase().indexOf(q) < 0) return false;
      return true;
    });
    var by = f.sort || 'found';
    if (by === 'email') out.sort(function (a, b) { return a.Email < b.Email ? -1 : a.Email > b.Email ? 1 : 0; });
    else if (by === 'domain') out.sort(function (a, b) { return a.Domain < b.Domain ? -1 : a.Domain > b.Domain ? 1 : (a.Email < b.Email ? -1 : 1); });
    else if (by === 'count') out.sort(function (a, b) { return b.Count - a.Count; });
    return out;
  }

  function joinList(rows, sep) {
    var s = sep === 'comma' ? ', ' : sep === 'semicolon' ? '; ' : '\n';
    return rows.map(function (r) { return r.Email; }).join(s) + (s === '\n' ? '\n' : '');
  }

  /** Split a pasted or plain-text file into a source; HTML keeps mailto names. */
  function textSource(name, text, kind) {
    var s = String(text || '');
    if (kind === 'eml' || /^(Received|Return-Path|MIME-Version|Content-Transfer-Encoding):/im.test(s.slice(0, 5000))) s = decodeQuotedPrintable(s);
    if (kind === 'html' || (kind !== 'text' && isHtml(s))) {
      var h = fromHtml(s);
      return { name: name, parts: [{ text: h.text, where: '' }], names: h.names, lines: false };
    }
    return { name: name, parts: [{ text: s, where: '' }] };
  }

  return { FREE: FREE, deobfuscate: deobfuscate, decodeEntities: decodeEntities, fromHtml: fromHtml, isHtml: isHtml, docxText: docxText,
    decodeQuotedPrintable: decodeQuotedPrintable, classify: classify, findIn: findIn, extract: extract, filter: filter, joinList: joinList, textSource: textSource };
});
