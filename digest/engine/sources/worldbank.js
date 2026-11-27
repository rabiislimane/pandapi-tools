// World Bank procurement notices for projects it finances (worldwide), official public search API.
import { fetchJson, cleanText, toIso, countryFromName } from '../common.js';

export const id = 'worldbank';
export const name = 'World Bank (projects worldwide)';
export const countries = null;

const API = 'https://search.worldbank.org/api/v2/procnotices';
const ROWS = 200;

export function typeOf(label) {
    const l = (label || '').toLowerCase();
    if (l.includes('award')) return 'award';
    if (l.includes('expression of interest') || l.includes('general procurement') || l.includes('prequalification')) return 'pre-notice';
    if (l.includes('bid') || l.includes('proposal') || l.includes('quotation') || l.includes('invitation')) return 'tender';
    return 'other';
}

export async function* fetchNotices(ctx) {
    const from = ctx.fromIso.slice(0, 10);
    for (let page = 0; page < 50; page++) {
        const p = new URLSearchParams({ format: 'json', rows: String(ROWS), os: String(page * ROWS), srt: 'submission_date', order: 'desc' });
        const data = await fetchJson(`${API}?${p}`, {}, { log: ctx.log });
        const rows = data?.procnotices || [];
        let older = 0;
        for (const r of rows) {
            const it = normalize(r);
            if (it.publishedAt && it.publishedAt.slice(0, 10) < from) { older++; continue; }
            if (!ctx.noticeTypes.has(it.noticeType)) continue;
            yield it;
        }
        if (rows.length < ROWS || older === rows.length) break;
    }
}

export function normalize(r) {
    const countryNameStr = r.project_ctry_name || r.contact_ctry_name || null;
    const deadline = r.submission_deadline_date
        ? toIso(`${r.submission_deadline_date.slice(0, 10)}T${(r.submission_deadline_time || '00:00').padEnd(5, '0').slice(0, 5)}:00Z`)
        : null;
    return {
        id: `worldbank:${r.id}`,
        source: id,
        sourceName: name,
        noticeId: r.bid_reference_no || r.id,
        title: cleanText(r.bid_description || r.project_name),
        description: cleanText(r.notice_text),
        noticeType: typeOf(r.notice_type),
        noticeTypeLabel: r.notice_type || null,
        status: r.notice_status || null,
        buyerName: cleanText(r.contact_organization) || r.project_name || null,
        buyerParent: 'World Bank-financed project',
        buyerCity: null,
        country: countryFromName(countryNameStr),
        countryNameRaw: countryNameStr,
        publishedAt: toIso(r.noticedate) || toIso(r.submission_date),
        deadline,
        valueAmount: null,
        valueCurrency: null,
        category: { GO: 'goods', CW: 'works', CS: 'consulting services', NC: 'services' }[r.procurement_group] || r.procurement_group || null,
        procedure: r.procurement_method_name || null,
        projectId: r.project_id || null,
        projectName: r.project_name || null,
        language: r.notice_lang_name || null,
        url: `https://projects.worldbank.org/en/projects-operations/procurement-detail/${r.id}`,
        documentsUrl: null,
        _contact: r.contact_email || r.contact_name ? { name: r.contact_name?.trim() || null, email: r.contact_email || null, phone: r.contact_phone_no || null } : null,
    };
}
