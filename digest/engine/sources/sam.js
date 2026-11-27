// SAM.gov (United States federal contract opportunities). Uses the public JSON API behind sam.gov search
// (no API key, no login). Details (NAICS, set-aside, place of performance, full description) come from
// the public opportunity endpoint, fetched only for notices that survive the filters.
import { fetchJson, cleanText, toIso, num, mapLimit } from '../common.js';

export const id = 'sam';
export const name = 'SAM.gov (US federal)';
export const countries = ['US'];
// SAM's `q` also matches attachments and FAR/DFARS clause text, so results are re-checked after enrich().
export const looseKeywordSearch = true;

const SEARCH = 'https://sam.gov/api/prod/sgs/v1/search/';
const DETAIL = 'https://sam.gov/api/prod/opps/v2/opportunities/';

const TYPE_CODES = { tender: ['o', 'k'], 'pre-notice': ['p', 'r'], award: ['a'], other: ['s', 'g', 'i', 'u'] };
const CODE_TO_TYPE = Object.fromEntries(Object.entries(TYPE_CODES).flatMap(([t, cs]) => cs.map((c) => [c, t])));

export async function* fetchNotices(ctx) {
    const codes = [...ctx.noticeTypes].flatMap((t) => TYPE_CODES[t] || []);
    if (!codes.length) return;
    // One search per keyword (SAM's q is AND-of-words); empty keyword list = one unfiltered search.
    const queries = ctx.keywords.length ? ctx.keywords : [null];
    const seen = new Set();
    for (const q of queries) {
        for (let page = 0; page < 100; page++) {
            const p = new URLSearchParams({
                index: 'opp', mode: 'search', sort: '-modifiedDate', is_active: 'true',
                page: String(page), size: '100', notice_type: codes.join(','),
                'publish_date.from': `${ctx.fromIso.slice(0, 19)}-00:00`,
            });
            if (q) { p.set('q', q); p.set('qMode', 'ALL'); }
            if (ctx.naics.length) p.set('naics', ctx.naics.join(','));
            const data = await fetchJson(`${SEARCH}?${p}`, {}, { log: ctx.log });
            const rows = data?._embedded?.results || [];
            for (const r of rows) {
                if (seen.has(r._id)) continue;
                seen.add(r._id);
                yield normalize(r, q);
            }
            const pg = data?.page || {};
            if (!rows.length || page + 1 >= (pg.totalPages || 0) || (page + 1) * 100 >= (pg.maxAllowedRecords || 10000)) break;
        }
    }
}

export function normalize(r, keyword) {
    const orgs = [...(r.organizationHierarchy || [])].sort((a, b) => a.level - b.level);
    const office = orgs[orgs.length - 1];
    const typeCode = r.type?.code;
    return {
        id: `sam:${r._id}`,
        source: id,
        sourceName: name,
        noticeId: r.solicitationNumber || r._id,
        title: cleanText(r.title),
        description: cleanText(r.descriptions?.[0]?.content),
        noticeType: CODE_TO_TYPE[typeCode] || 'other',
        noticeTypeLabel: r.type?.value || null,
        status: r.isCanceled ? 'cancelled' : (r.isActive ? 'active' : 'inactive'),
        buyerName: office?.name || null,
        buyerParent: orgs.length > 1 ? orgs[0].name : null,
        buyerCity: office?.address?.city || null,
        buyerRegion: office?.address?.state || null,
        country: 'US',
        publishedAt: toIso(r.publishDate),
        deadline: toIso(r.responseDate),
        valueAmount: null,
        valueCurrency: null,
        url: `https://sam.gov/opp/${r._id}/view`,
        documentsUrl: `https://sam.gov/opp/${r._id}/view#attachments-links`,
        _samId: r._id,
        _serverKeyword: keyword || null,
    };
}

/** Add NAICS, PSC, set-aside, place of performance, award and full description from the detail endpoint. */
export async function enrich(items, ctx) {
    await mapLimit(items, 4, async (it) => {
        try {
            const d = await fetchJson(`${DETAIL}${it._samId}`, {}, { tries: 3, log: ctx.log });
            applyDetail(it, d);
        } catch (e) {
            ctx.log.debug(`SAM detail failed for ${it._samId}: ${e.message}`);
        }
    });
}

export function applyDetail(it, d) {
    const x = d?.data2 || {};
    const naics = (x.naics || []).flatMap((n) => n.code || []);
    if (naics.length) it.naicsCodes = [...new Set(naics)];
    if (x.classificationCode) it.pscCode = x.classificationCode;
    if (x.solicitation?.setAside) it.setAside = x.solicitation.setAside;
    const pop = x.placeOfPerformance;
    if (pop) it.placeOfPerformance = [pop.city?.name, pop.state?.code || pop.state?.name, pop.zip, pop.country?.code].filter(Boolean).join(', ') || null;
    const body = d?.description?.[0]?.body;
    if (body) it.description = cleanText(body);
    const aw = x.award;
    if (aw && (aw.amount || aw.awardee?.name)) {
        it.awardedTo = aw.awardee?.name ? [aw.awardee.name] : null;
        const amt = num(aw.amount);
        if (amt != null) { it.valueAmount = amt; it.valueCurrency = 'USD'; }
        if (aw.date) it.awardDate = toIso(aw.date);
    }
    const poc = (x.pointOfContact || [])[0];
    if (poc) it._contact = { name: poc.fullName || null, email: poc.email || null, phone: poc.phone || null };
}
