// EU TED (Tenders Electronic Daily): official anonymous search API, newest first.
// Covers the 27 EU countries plus EEA/candidate countries publishing on TED.
import { fetchJson, cleanText, toIso, num, iso3to2, iso2to3 } from '../common.js';

export const id = 'ted';
export const name = 'TED (European Union)';
export const countries = null; // many

const API = 'https://api.ted.europa.eu/v3/notices/search';
const TYPES = {
    tender: ['cn-standard', 'cn-social', 'cn-desg', 'qu-sy'],
    'pre-notice': ['pin-only', 'pin-buyer', 'pin-cfc-standard', 'pin-cfc-social', 'pin-rtl', 'pin-tran'],
    award: ['can-standard', 'can-social', 'can-desg', 'can-tran', 'can-modif', 'veat'],
    other: ['pmc', 'compl'],
};
const LABELS = {
    'cn-standard': 'Contract notice', 'cn-social': 'Contract notice (social & other services)', 'cn-desg': 'Design contest notice', 'qu-sy': 'Qualification system notice',
    'pin-only': 'Prior information notice', 'pin-buyer': 'Buyer profile notice', 'pin-cfc-standard': 'Prior information notice (call for competition)', 'pin-cfc-social': 'Prior information notice (call for competition, social)', 'pin-rtl': 'Prior information notice (reducing time limits)', 'pin-tran': 'Prior information notice (public transport)',
    'can-standard': 'Contract award notice', 'can-social': 'Contract award notice (social & other services)', 'can-desg': 'Design contest result', 'can-tran': 'Contract award notice (public transport)', 'can-modif': 'Contract modification notice', veat: 'Voluntary ex-ante transparency notice',
    pmc: 'Pre-market consultation notice', compl: 'Contract completion notice',
};
const PROCEDURES = {
    open: 'Open procedure', restricted: 'Restricted procedure', 'neg-w-call': 'Negotiated with prior publication', 'neg-wo-call': 'Negotiated without prior publication',
    'comp-dial': 'Competitive dialogue', innovation: 'Innovation partnership', 'oth-single': 'Other single-stage procedure', 'oth-mult': 'Other multiple-stage procedure', 'exp-int-rail': 'Call for expressions of interest',
};
const CODE_TO_TYPE = Object.fromEntries(Object.entries(TYPES).flatMap(([t, cs]) => cs.map((c) => [c, t])));

const FIELDS = ['publication-number', 'notice-type', 'publication-date', 'title-proc', 'notice-title', 'title-lot', 'description-proc', 'description-lot', 'buyer-name', 'buyer-city', 'buyer-country',
    'deadline-receipt-tender-date-lot', 'deadline-receipt-tender-time-lot', 'classification-cpv', 'main-classification-proc', 'estimated-value-proc', 'estimated-value-cur-proc',
    'estimated-value-lot', 'result-value-notice', 'total-value-cur', 'organisation-name-tenderer', 'contract-nature-main-proc', 'procedure-type', 'place-of-performance-country-proc', 'document-url-lot', 'links'];

const PAGE = 250;

export function buildQuery(ctx) {
    const types = [...ctx.noticeTypes].flatMap((t) => TYPES[t] || []);
    if (!types.length) return null;
    const parts = [`publication-date>=${ctx.fromIso.slice(0, 10).replace(/-/g, '')}`, `notice-type IN (${types.join(' ')})`];
    const c3 = ctx.countries.map(iso2to3).filter(Boolean);
    if (ctx.countries.length) {
        if (!c3.length) return null; // asked only for countries TED does not cover
        parts.push(`buyer-country IN (${c3.join(' ')})`);
    }
    if (ctx.cpv.length) parts.push(`classification-cpv IN (${ctx.cpv.map((p) => p.padEnd(8, '0')).join(' ')})`);
    if (ctx.keywords.length) {
        // Full-text search (FT) is the only TED field search that handles phrases; it also hits annexes and
        // standard terms, so strict mode re-checks titles and descriptions locally (see _matchText).
        parts.push(`(${ctx.keywords.map((k) => `FT ~ (${/\s/.test(k) ? `"${k.replace(/"/g, '')}"` : k.replace(/[()"]/g, '')})`).join(' OR ')})`);
    }
    return `${parts.join(' AND ')} SORT BY publication-number DESC`;
}

export async function* fetchNotices(ctx) {
    const query = buildQuery(ctx);
    if (!query) return;
    for (let page = 1; page <= 60; page++) {
        const data = await fetchJson(API, {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ query, fields: FIELDS, limit: PAGE, page, paginationMode: 'PAGE_NUMBER' }),
        }, { log: ctx.log });
        const rows = data?.notices || [];
        for (const n of rows) yield normalize(n, ctx.keywords.length > 0);
        if (rows.length < PAGE || page * PAGE >= Math.min(data?.totalNoticeCount ?? 0, 15000)) break;
    }
}

/** Pick English text from TED's multilingual {lang: value|[values]} maps, else the first language. */
function pick(m, { all = false } = {}) {
    if (m == null) return all ? [] : null;
    if (typeof m === 'string') return all ? [m] : m;
    if (Array.isArray(m)) return all ? m : m[0] ?? null;
    const v = m.eng ?? m.ENG ?? m.mul ?? Object.values(m)[0];
    const arr = Array.isArray(v) ? v : (v == null ? [] : [v]);
    return all ? arr : arr[0] ?? null;
}

/** Every language version of a TED multilingual field, flattened to one string. */
function allText(m) {
    if (m == null) return '';
    if (typeof m === 'string') return m;
    if (Array.isArray(m)) return m.map(allText).join('\n');
    return Object.values(m).map(allText).join('\n');
}

export function normalize(n, serverKeyword) {
    const pub = n['publication-number'];
    const type = n['notice-type'];
    const dates = (n['deadline-receipt-tender-date-lot'] || []).map((d, i) => toIso(d, n['deadline-receipt-tender-time-lot']?.[i])).filter(Boolean).sort();
    const isAward = CODE_TO_TYPE[type] === 'award';
    let amount = isAward ? num(n['result-value-notice']) : num(n['estimated-value-proc']);
    let currency = isAward ? (n['total-value-cur']?.[0] ?? null) : (n['estimated-value-cur-proc'] ?? null);
    if (amount == null && !isAward) {
        const lots = (n['estimated-value-lot'] || []).map(num).filter((x) => x != null);
        if (lots.length) { amount = lots.reduce((a, b) => a + b, 0); currency = currency || 'EUR'; }
    }
    if (amount != null && !currency) currency = 'EUR';
    const cpv = [...new Set([...(n['main-classification-proc'] || []), ...(n['classification-cpv'] || [])])];
    const country3 = n['buyer-country']?.[0];
    let title = pick(n['title-proc']);
    if (!title) title = pick(n['notice-title'])?.split(' – ').slice(2).join(' – ') || pick(n['notice-title']);
    const desc = [...new Set(pick(n['description-lot'], { all: true }))].join('\n\n');
    const winners = [...new Set(pick(n['organisation-name-tenderer'], { all: true }))];
    return {
        id: `ted:${pub}`,
        source: id,
        sourceName: name,
        noticeId: pub,
        title: cleanText(title),
        description: cleanText(desc) || null,
        noticeType: CODE_TO_TYPE[type] || 'other',
        noticeTypeLabel: LABELS[type] || type || null,
        status: null,
        buyerName: cleanText(pick(n['buyer-name'])),
        buyerCity: pick(n['buyer-city']),
        country: iso3to2(country3) || null,
        countryCode3: country3 || null,
        publishedAt: toIso(n['publication-date']),
        deadline: dates[0] || null,
        valueAmount: amount,
        valueCurrency: currency,
        category: n['contract-nature-main-proc'] || null,
        procedure: PROCEDURES[n['procedure-type']] || n['procedure-type'] || null,
        cpvCodes: cpv,
        awardedTo: winners.length ? winners : null,
        url: n.links?.html?.ENG || `https://ted.europa.eu/en/notice/-/detail/${pub}`,
        documentsUrl: n['document-url-lot']?.[0] || n.links?.pdf?.ENG || null,
        _serverKeyword: serverKeyword,
        // Titles (TED translates them into every EU language), the CPV category name inside notice-title
        // ("Country – category – title") and descriptions in all languages: what strict keyword matching reads.
        // Most EU notices have no English description, so the English category name is often the only English
        // text: "software development" matches "IT services: consulting, software development, ...".
        _matchText: ['notice-title', 'title-proc', 'title-lot', 'description-proc', 'description-lot'].map((f) => allText(n[f])).join('\n'),
    };
}
