// Weekly public tender digest (strategy v3, unit D). Runs on GitHub Actions for free, no Apify credit:
// the same open-data fetchers as the public-tenders-feed actor (engine/ is a copy of its src/, synced
// with digest/sync-engine.sh), no API keys. Writes digest/data/<slug>.json with public notice fields only:
// no contact names, emails or phones. Usage: node digest/fetch.mjs
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadFxRates, convert } from './engine/common.js';
import { SOURCES, buildContext, rejectReason, finalize, keywordHit } from './engine/pipeline.js';

const HERE = dirname(fileURLToPath(import.meta.url));
export const DIGESTS = [
    { slug: 'it-tenders', keywords: ['software', 'cloud', 'IT services', 'cybersecurity', 'data centre', 'data center'] },
];
const log = { info: (m) => console.log(m), warning: (m) => console.warn('WARN', m), debug: () => {} };
// A keyword hit alone is too loose for a public list ("cloud" in a dog-food notice), so a notice must
// also have the keyword in its title or carry an IT classification code.
const IT_CODES = { cpvCodes: ['48', '72', '302'], naicsCodes: ['5112', '5132', '5182', '5415', '518'], unspscCodes: ['4320', '4321', '4322', '4323', '8111', '8116'] };
const digits = (c) => String(c).replace(/[^0-9]/g, '');
export const isIt = (r) => r.matchedInTitle === true || /^(D3|7[A-K])/.test(r.pscCode || '')
    || Object.entries(IT_CODES).some(([k, pre]) => (r[k] || []).some((c) => pre.some((p) => digits(c).startsWith(p))));
const KEEP = ['title', 'buyerName', 'country', 'countryName', 'deadline', 'daysLeft', 'valueAmount', 'valueCurrency', 'valueUsd', 'publishedAt', 'url', 'source', 'sourceName', 'id', 'noticeType', 'matchedKeywords'];

async function collect(src, ctx) {
    const kept = []; let scanned = 0;
    const strict = ctx.strictKeywords && ctx.matchers.length && src.looseKeywordSearch && src.enrich;
    let pending = [];
    const flush = async () => {
        if (!pending.length) return;
        const batch = pending; pending = [];
        await src.enrich(batch, ctx);
        for (const it of batch) if (kept.length < ctx.maxPerSource && keywordHit(it, ctx)) kept.push(it);
    };
    for await (const it of src.fetchNotices(ctx)) {
        scanned++;
        if (rejectReason(it, ctx)) continue;
        if (strict) { pending.push(it); if (pending.length >= 25) await flush(); if (kept.length >= ctx.maxPerSource || scanned > ctx.maxPerSource * 6) break; continue; }
        kept.push(it);
        if (kept.length >= ctx.maxPerSource) break;
    }
    if (strict) await flush();
    else if (src.enrich && kept.length) await src.enrich(kept, ctx);
    return { kept, scanned };
}

const fx = await loadFxRates(log);
for (const d of DIGESTS) {
    const ctx = buildContext({ keywords: d.keywords, strictKeywordMatch: true, noticeTypes: ['tender'], postedWithinDays: 7, minDaysLeft: 1,
        maxResultsPerSource: 40, includeDescription: false, includeContacts: false });
    ctx.log = log;
    const sources = {};
    const results = await Promise.all(ctx.sources.map(async (s) => {
        const t0 = Date.now();
        try {
            const { kept, scanned } = await collect(SOURCES[s], ctx);
            sources[s] = { name: SOURCES[s].name, ok: true, kept: kept.length, scanned, seconds: Math.round((Date.now() - t0) / 1000) };
            return kept;
        } catch (e) {
            sources[s] = { name: SOURCES[s].name, ok: false, error: String(e.message).slice(0, 200) };
            return [];
        }
    }));
    const all = results.flat().map((it) => finalize(it, ctx, fx));
    const rows = all.filter(isIt).map((r) => Object.fromEntries(KEEP.map((k) => [k, r[k] ?? null])));
    rows.sort((a, b) => (a.deadline || '9999').localeCompare(b.deadline || '9999'));
    const out = { slug: d.slug, keywords: d.keywords, postedSince: ctx.fromDate, generatedAt: new Date().toISOString(), currencyRatesDate: fx.date, sources, notices: rows };
    mkdirSync(join(HERE, 'data'), { recursive: true });
    writeFileSync(join(HERE, 'data', `${d.slug}.json`), JSON.stringify(out, null, 1) + '\n');
    console.log(d.slug, rows.length, 'notices of', all.length, 'keyword hits', JSON.stringify(sources));
    if (Object.values(sources).every((s) => !s.ok)) { console.error('All sources failed'); process.exitCode = 1; }
}
