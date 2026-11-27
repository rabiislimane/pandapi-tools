// Input parsing, filters and output shaping (pure functions, unit-tested).
import { keywordMatchers, matchKeywords, codePrefix, convert, daysLeft, countryName, ymd, stripClauses } from './common.js';
import * as sam from './sources/sam.js';
import * as ted from './sources/ted.js';
import { fts, cf } from './sources/uk.js';
import * as canadabuys from './sources/canadabuys.js';
import * as worldbank from './sources/worldbank.js';

export const SOURCES = { sam, ted, 'uk-fts': fts, 'uk-cf': cf, canadabuys, worldbank };
export const CODE_SCHEME = { sam: 'NAICS', ted: 'CPV', 'uk-fts': 'CPV', 'uk-cf': 'CPV', canadabuys: 'UNSPSC', worldbank: null };
export const NOTICE_TYPES = ['tender', 'pre-notice', 'award', 'other'];

// Buyer contacts (official procurement contact points printed in each notice). Owner signed off 2026-11-13
// (ops/decisions.md). Users can switch them off with includeContacts: false.
export const CONTACTS_ENABLED = true;

const arr = (v) => (Array.isArray(v) ? v : (v == null || v === '' ? [] : String(v).split(/[,;\n]/)))
    .map((x) => String(x).trim()).filter(Boolean);

export function buildContext(input = {}, now = new Date()) {
    const errors = [];
    const sources = arr(input.sources).map((s) => s.toLowerCase());
    const unknown = sources.filter((s) => !SOURCES[s]);
    if (unknown.length) errors.push(`Unknown source(s): ${unknown.join(', ')}. Use: ${Object.keys(SOURCES).join(', ')}.`);
    const noticeTypes = new Set(arr(input.noticeTypes ?? ['tender', 'pre-notice']).map((s) => s.toLowerCase()));
    for (const t of noticeTypes) if (!NOTICE_TYPES.includes(t)) errors.push(`Unknown notice type "${t}". Use: ${NOTICE_TYPES.join(', ')}.`);
    const countries = arr(input.countries).map((c) => c.toUpperCase());
    for (const c of countries) if (!/^[A-Z]{2}$/.test(c)) errors.push(`Country "${c}" must be a 2-letter ISO code like US, GB, DE, FR, CA.`);

    let from;
    if (input.postedAfter) {
        const t = Date.parse(String(input.postedAfter).length <= 10 ? `${input.postedAfter}T00:00:00Z` : input.postedAfter);
        if (Number.isNaN(t)) errors.push(`postedAfter "${input.postedAfter}" is not a date (use YYYY-MM-DD).`);
        else from = new Date(t);
    }
    const days = Number(input.postedWithinDays ?? 7);
    if (!from) {
        if (!(days >= 1 && days <= 365)) errors.push('postedWithinDays must be between 1 and 365.');
        from = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()) - (Math.max(1, days) - 1) * 86400000);
    }

    const keywords = arr(input.keywords);
    const cpv = arr(input.cpvCodes).map((c) => codePrefix(c, 'CPV')).filter(Boolean);
    const naics = arr(input.naicsCodes).map((c) => codePrefix(c, 'NAICS')).filter(Boolean);
    const unspsc = arr(input.unspscCodes).map((c) => codePrefix(c, 'UNSPSC')).filter(Boolean);

    const chosen = (sources.length ? sources : Object.keys(SOURCES)).filter((s) => SOURCES[s]);
    const skipped = {};
    const codeSchemes = new Set([cpv.length && 'CPV', naics.length && 'NAICS', unspsc.length && 'UNSPSC'].filter(Boolean));
    const active = chosen.filter((s) => {
        const cov = SOURCES[s].countries;
        if (countries.length && cov && !cov.some((c) => countries.includes(c))) { skipped[s] = `covers ${cov.join('/')} only, not ${countries.join(', ')}`; return false; }
        if (codeSchemes.size && !codeSchemes.has(CODE_SCHEME[s])) { skipped[s] = `has no ${[...codeSchemes].join('/')} codes (uses ${CODE_SCHEME[s] || 'no codes'})`; return false; }
        if (s === 'canadabuys' && ![...noticeTypes].some((t) => t !== 'award')) { skipped[s] = 'award notices are not in the CanadaBuys open-tender feed'; return false; }
        return true;
    });

    const minDaysLeft = input.minDaysLeft === undefined ? 0 : (input.minDaysLeft === null || input.minDaysLeft === '' ? null : Number(input.minDaysLeft));
    return {
        errors,
        sources: active,
        skipped,
        noticeTypes,
        countries,
        keywords,
        matchers: keywordMatchers(keywords),
        excludeMatchers: keywordMatchers(arr(input.excludeKeywords)),
        cpv, naics, unspsc,
        from,
        fromIso: from.toISOString(),
        fromDate: ymd(from),
        minDaysLeft,
        minValueUsd: input.minValueUsd ? Number(input.minValueUsd) : null,
        // SAM.gov's keyword search also matches attachments and clause boilerplate; strict mode re-checks the
        // keywords in the title, full description (clauses removed) and buyer after the detail call.
        strictKeywords: input.strictKeywordMatch !== false,
        onlyNew: Boolean(input.onlyNew),
        stateKey: String(input.stateKey || 'default').replace(/[^a-zA-Z0-9!\-_.'()]/g, '-').slice(0, 200),
        maxPerSource: Math.max(1, Number(input.maxResultsPerSource ?? 50)),
        maxResults: Math.max(1, Number(input.maxResults ?? 1000)),
        includeDescription: input.includeDescription !== false,
        includeContacts: CONTACTS_ENABLED && input.includeContacts !== false,
        descriptionMaxLength: Math.max(100, Number(input.descriptionMaxLength ?? 4000)),
        now: now.getTime(),
    };
}

const prefixMatch = (codes, prefixes) => (codes || []).some((c) => prefixes.some((p) => String(c).replace(/[^0-9]/g, '').startsWith(p)));

/** Filters that can run before enrichment. Returns null (keep) or a short reason (drop). */
export function rejectReason(it, ctx) {
    if (!ctx.noticeTypes.has(it.noticeType)) return 'type';
    if (it.publishedAt && it.publishedAt.slice(0, 10) < ctx.fromDate) return 'date';
    if (ctx.countries.length && !ctx.countries.includes(it.country)) return 'country';
    if (ctx.minDaysLeft != null && it.noticeType !== 'award' && it.deadline && daysLeft(it.deadline, ctx.now) < ctx.minDaysLeft) return 'deadline';
    const text = `${it.title || ''}\n${it.description || ''}\n${it.buyerName || ''}`;
    if (ctx.matchers.length) {
        // Sources that give us their full multilingual text (TED) are checked on it in strict mode.
        if (ctx.strictKeywords && it._matchText != null) { if (!matchKeywords(ctx.matchers, it._matchText).length) return 'keyword'; }
        else if (!it._serverKeyword && !matchKeywords(ctx.matchers, text).length) return 'keyword';
    }
    if (ctx.excludeMatchers.length && matchKeywords(ctx.excludeMatchers, `${it.title || ''}\n${it.description || ''}`).length) return 'excluded';
    const scheme = CODE_SCHEME[it.source];
    if (scheme === 'CPV' && ctx.cpv.length && !prefixMatch(it.cpvCodes, ctx.cpv)) return 'code';
    if (scheme === 'UNSPSC' && ctx.unspsc.length && !prefixMatch(it.unspscCodes, ctx.unspsc)) return 'code';
    // NAICS (SAM) is filtered server-side; codes arrive with enrichment.
    return null;
}

const ORDER = ['title', 'buyerName', 'country', 'countryName', 'noticeType', 'deadline', 'daysLeft', 'valueAmount', 'valueCurrency', 'valueUsd', 'valueEur', 'publishedAt', 'url',
    'source', 'sourceName', 'id', 'noticeId', 'noticeTypeLabel', 'status', 'category', 'procedure', 'cpvCodes', 'naicsCodes', 'pscCode', 'unspscCodes', 'gsinCodes', 'setAside',
    'buyerParent', 'buyerCity', 'buyerRegion', 'contactName', 'contactEmail', 'contactPhone', 'placeOfPerformance', 'awardedTo', 'awardDate', 'description', 'documentsUrl', 'matchedKeywords', 'matchedInTitle'];

/** Final shape: values in USD/EUR, days left, country name, description length, stable key order. */
export function finalize(it, ctx, fx) {
    const out = { ...it };
    Object.assign(out, convert(it.valueAmount, it.valueCurrency, fx));
    out.daysLeft = daysLeft(it.deadline, ctx.now);
    out.countryName = countryName(it.country) || it.countryNameRaw || null;
    const text = SOURCES[it.source]?.looseKeywordSearch && ctx.strictKeywords ? strictText(it) : `${it.title || ''}\n${it.description || ''}\n${it.buyerName || ''}`;
    let matched = matchKeywords(ctx.matchers, text);
    if (!matched.length && ctx.strictKeywords && it._matchText) matched = matchKeywords(ctx.matchers, it._matchText);
    if (!matched.length && typeof it._serverKeyword === 'string' && !ctx.strictKeywords) matched = [it._serverKeyword];
    out.matchedKeywords = matched;
    out.matchedInTitle = ctx.matchers.length ? matchKeywords(ctx.matchers, it.title || '').length > 0 : null;
    if (!ctx.includeDescription) out.description = null;
    else if (out.description && out.description.length > ctx.descriptionMaxLength) out.description = `${out.description.slice(0, ctx.descriptionMaxLength - 1).trimEnd()}…`;
    if (ctx.includeContacts && it._contact) Object.assign(out, { contactName: it._contact.name || null, contactEmail: it._contact.email || null, contactPhone: it._contact.phone || null });
    const ordered = {};
    for (const k of ORDER) if (ctx.includeContacts || !k.startsWith('contact')) ordered[k] = out[k] ?? (k.endsWith('Codes') || k === 'matchedKeywords' ? [] : null);
    for (const [k, v] of Object.entries(out)) if (!(k in ordered) && !k.startsWith('_') && v != null && k !== 'countryNameRaw' && k !== 'countryCode3') ordered[k] = v;
    ordered.fetchedAt = new Date(ctx.now).toISOString();
    return ordered;
}

// SAM notices state what is being bought at the start of the description; mentions deep inside 10-25k
// character descriptions are compliance prose ("applicable FRCS cybersecurity standards"), not the subject.
export const STRICT_WINDOW = 1500;
const strictText = (it) => `${it.title || ''}\n${stripClauses(it.description).slice(0, STRICT_WINDOW)}\n${it.buyerName || ''}`;

/** Strict keyword check for sources whose server-side search is loose (SAM.gov). Run after enrichment. */
export function keywordHit(it, ctx) {
    if (!ctx.matchers.length) return true;
    return matchKeywords(ctx.matchers, strictText(it)).length > 0;
}

/** Value filter runs after conversion. Unknown values are kept. */
export const valueTooLow = (row, ctx) => ctx.minValueUsd != null && row.valueUsd != null && row.valueUsd < ctx.minValueUsd;
