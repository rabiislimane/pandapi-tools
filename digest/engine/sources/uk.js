// United Kingdom: Find a Tender (above-threshold, Procurement Act 2023) and Contracts Finder (below-threshold,
// England). Both publish official OCDS JSON APIs under the Open Government Licence.
import { fetchJson, cleanText, toIso, num } from '../common.js';

const STAGE = { 'pre-notice': 'planning', tender: 'tender', award: 'award' };
const TAG_TYPE = {
    planning: 'pre-notice', planningUpdate: 'pre-notice',
    tender: 'tender', tenderAmendment: 'tender', tenderUpdate: 'tender', tenderCancellation: 'tender',
    award: 'award', awardUpdate: 'award', contract: 'award', contractUpdate: 'award', contractAmendment: 'award', implementation: 'award',
};
const MAX_PAGES = 60;

// pauseMs: Find a Tender answers HTTP 429 ("try again in 2 minutes") to bursts of page calls, so it is paced.
// adaptive: Find a Tender pages get slower the deeper its cursor goes (2 s at first, 20 s by page 17), and on busy
// days every page takes 12-50 s (2026-11-17). A 7-day window is ~21 pages and took 240 s on 2026-11-16, near
// Apify's 5-minute default-run limit. Pages inside a window come oldest first, so it is read in time windows from
// newest to oldest, sized to about one page each (start at 1 h, double while a window fits in one page, halve when
// it needs more). No page starts after budgetMs and each request is capped by the time left, so a slow day costs
// the oldest notices, never the newest.
const HOUR = 3600000;
function makeSource({ id, name, url, noticeUrl, dateParam, dateFmt, stageFilter, pauseMs = 300, toParam, adaptive = false, budgetMs = 120000 }) {
    return {
        id, name, countries: ['GB'],
        async* fetchNotices(ctx) {
            const byOcid = new Map();
            // Find a Tender's stage filter drops update releases and even some new tenders (checked 2026-11-15:
            // a below-threshold tender was missing), so it is fetched unfiltered and filtered by tag here.
            const stages = stageFilter ? [...ctx.noticeTypes].map((t) => STAGE[t]).filter(Boolean) : [null];
            const started = Date.now();
            const left = () => budgetMs - (Date.now() - started);
            const from = Date.parse(ctx.fromIso);
            let stop = false;
            for (const stage of stages) {
                let to = Date.now();
                let size = HOUR;
                while (!stop) {
                    const winFrom = adaptive ? Math.max(from, to - size) : from;
                    const params = { [dateParam]: dateFmt(new Date(winFrom).toISOString()), limit: '100' };
                    if (adaptive) params[toParam] = dateFmt(new Date(to).toISOString());
                    if (stage) params.stages = stage;
                    let next = `${url}?${new URLSearchParams(params)}`;
                    let pages = 0;
                    for (; next && pages < MAX_PAGES; pages++) {
                        if (adaptive && left() < 5000) {
                            const msg = `Find a Tender was slow; notices are complete only for updates after ${new Date(to).toISOString().slice(0, 16)} UTC`;
                            ctx.log.warning(`${name}: ${msg}.`);
                            (ctx.partial ||= {})[id] = msg;
                            stop = true;
                            break;
                        }
                        let data;
                        try {
                            // A retry only when there is time for it; each try gets its share of the time left.
                            const tries = adaptive && left() < 60000 ? 1 : 2;
                            data = await fetchJson(next, {}, adaptive
                                ? { log: ctx.log, timeoutMs: Math.min(90000, Math.floor(left() / tries) - 2000), tries, maxWaitMs: Math.max(0, left() - 30000) }
                                : { log: ctx.log, timeoutMs: 90000 });
                        } catch (e) {
                            // Keep what earlier pages returned instead of losing the whole source.
                            if (!byOcid.size) throw e;
                            ctx.log.warning(`${name}: stopped after page ${pages} (${e.message.slice(0, 120)}); returning the ${byOcid.size} notices fetched so far.`);
                            (ctx.partial ||= {})[id] = adaptive
                                ? `Find a Tender was slow or unavailable; notices are complete only for updates after ${new Date(to).toISOString().slice(0, 16)} UTC`
                                : e.message.slice(0, 200);
                            stop = true;
                            break;
                        }
                        for (const r of data?.releases || []) {
                            const prev = byOcid.get(r.ocid);
                            if (!prev || (r.date || '') > (prev.date || '')) byOcid.set(r.ocid, r);
                        }
                        const n = data?.links?.next;
                        if (n || adaptive) await new Promise((r) => setTimeout(r, pauseMs));
                        next = n && (data?.releases || []).length ? n : null;
                    }
                    if (!adaptive || winFrom <= from) break;
                    to = winFrom;
                    size = pages > 1 ? Math.max(HOUR / 2, size / 2) : Math.min(24 * HOUR, size * 2);
                }
            }
            const items = [...byOcid.values()].map((r) => normalize(r, { id, name, noticeUrl })).filter((x) => x.title);
            items.sort((a, b) => (b.publishedAt || '').localeCompare(a.publishedAt || ''));
            yield* items;
        },
    };
}

export function normalize(r, src) {
    const t = r.tender || {};
    const parties = r.parties || [];
    const buyer = parties.find((p) => p.id === r.buyer?.id) || parties.find((p) => (p.roles || []).includes('buyer'));
    const tag = (r.tag || [])[0];
    const cls = [t.classification, ...(t.items || []).flatMap((i) => [i.classification, ...(i.additionalClassifications || [])])].filter(Boolean);
    const cpv = [...new Set(cls.filter((c) => /cpv/i.test(c.scheme || '')).map((c) => String(c.id)))];
    const awards = r.awards || [];
    const isAward = TAG_TYPE[tag] === 'award';
    const aVal = awards.map((a) => a.value).find((v) => v?.amount != null);
    const val = isAward && aVal ? aVal : (t.value?.amount != null ? t.value : t.minValue);
    const winners = [...new Set(awards.flatMap((a) => (a.suppliers || []).map((s) => s.name)).filter(Boolean))];
    const contactParty = parties.find((p) => (p.roles || []).includes('processContactPoint')) || buyer;
    const cp = contactParty?.contactPoint || buyer?.contactPoint;
    const docUrl = (t.documents || []).map((d) => d.url).find((u) => u && /\/Notice\//i.test(u));
    return {
        id: `${src.id}:${r.ocid}`,
        source: src.id,
        sourceName: src.name,
        noticeId: r.id || r.ocid,
        ocid: r.ocid,
        title: cleanText(t.title || awards[0]?.title),
        description: cleanText(t.description || awards[0]?.description),
        noticeType: TAG_TYPE[tag] || 'other',
        noticeTypeLabel: t.procurementMethodDetails ? `${tag} (${t.procurementMethodDetails})` : tag || null,
        status: t.status || null,
        buyerName: buyer?.name || r.buyer?.name || null,
        buyerCity: buyer?.address?.locality || null,
        buyerRegion: buyer?.address?.region || null,
        country: (buyer?.address?.country || 'GB').toUpperCase().slice(0, 2),
        publishedAt: toIso(t.datePublished || r.date),
        deadline: toIso(t.tenderPeriod?.endDate),
        valueAmount: num(val?.amount),
        valueCurrency: val?.currency || null,
        category: t.mainProcurementCategory || null,
        procedure: t.procurementMethodDetails || t.procurementMethod || null,
        cpvCodes: cpv,
        awardedTo: winners.length ? winners : null,
        url: docUrl || src.noticeUrl(r),
        documentsUrl: (t.documents || []).map((d) => d.url).find((u) => u && u !== docUrl) || null,
        _contact: cp ? { name: cp.name || null, email: cp.email || null, phone: cp.telephone || null } : null,
    };
}

export const fts = makeSource({
    id: 'uk-fts',
    name: 'Find a Tender (UK)',
    url: 'https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages',
    noticeUrl: (r) => `https://www.find-tender.service.gov.uk/Notice/${r.id}`,
    dateParam: 'updatedFrom',
    dateFmt: (iso) => iso.slice(0, 19),
    stageFilter: false,
    pauseMs: 1200,
    toParam: 'updatedTo',
    adaptive: true,
});

export const cf = makeSource({
    id: 'uk-cf',
    name: 'Contracts Finder (UK)',
    url: 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search',
    noticeUrl: (r) => `https://www.contractsfinder.service.gov.uk/Notice/${String(r.id).replace(/-\d+$/, '')}`,
    dateParam: 'publishedFrom',
    dateFmt: (iso) => iso.slice(0, 10),
    stageFilter: true,
});
