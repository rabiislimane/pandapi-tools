// CanadaBuys: Government of Canada open tender notices, official open-data CSV (Open Government Licence - Canada).
import { fetchRetry, cleanText, toIso } from '../common.js';

export const id = 'canadabuys';
export const name = 'CanadaBuys (Canada federal)';
export const countries = ['CA'];

const CSV_URL = 'https://canadabuys.canada.ca/opendata/pub/openTenderNotice-ouvertAvisAppelOffres.csv';

const TYPE = (label) => {
    const l = (label || '').toLowerCase();
    if (!l || l === 'not applicable') return 'tender';
    if (l.includes('information')) return 'pre-notice';
    if (l.includes('advance contract award') || l.includes('directed')) return 'other';
    return 'tender';
};
const CATEGORY = { '*SRV': 'services', '*GD': 'goods', '*CNST': 'works', '*SRVTGD': 'services' };

/** Minimal RFC 4180 CSV parser (quoted fields, escaped quotes, newlines inside quotes). */
export function parseCsv(text) {
    const rows = [];
    let row = []; let field = ''; let q = false;
    for (let i = 0; i < text.length; i++) {
        const c = text[i];
        if (q) {
            if (c === '"') {
                if (text[i + 1] === '"') { field += '"'; i++; } else q = false;
            } else field += c;
        } else if (c === '"') q = true;
        else if (c === ',') { row.push(field); field = ''; }
        else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
        else if (c !== '\r') field += c;
    }
    if (field || row.length) { row.push(field); rows.push(row); }
    const header = (rows.shift() || []).map((h) => h.replace(/^﻿/, ''));
    return rows.filter((r) => r.length > 1).map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ''])));
}

const list = (s) => (s || '').split('\n').map((x) => x.replace(/^\*/, '').trim()).filter(Boolean);
// Canadian notices list local Ottawa time without an offset; treat as Eastern Time.
const eastern = (s) => {
    if (!s) return null;
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return toIso(`${s}T00:00:00-05:00`);
    return toIso(/[+-]\d{2}:\d{2}$|Z$/.test(s) ? s : `${s}-05:00`);
};

export async function* fetchNotices(ctx) {
    const wanted = new Set(ctx.noticeTypes);
    if (!['tender', 'pre-notice', 'other'].some((t) => wanted.has(t))) return; // awards are a separate dataset
    const res = await fetchRetry(CSV_URL, {}, { log: ctx.log, timeoutMs: 120000 });
    const rows = parseCsv(await res.text());
    const items = rows.map(normalize).filter((x) => x.title && x.publishedAt && x.publishedAt.slice(0, 10) >= ctx.fromDate);
    items.sort((a, b) => (b.publishedAt || '').localeCompare(a.publishedAt || ''));
    yield* items;
}

export function normalize(r) {
    const ref = r['referenceNumber-numeroReference'];
    const amend = r['amendmentNumber-numeroModification'];
    const label = r['noticeType-avisType-eng'];
    const unspsc = list(r.unspsc);
    const cat = list(r['procurementCategory-categorieApprovisionnement']).map((c) => CATEGORY[`*${c}`]).filter(Boolean);
    return {
        id: `canadabuys:${ref}`,
        source: id,
        sourceName: name,
        noticeId: r['solicitationNumber-numeroSollicitation'] || ref,
        title: cleanText(r['title-titre-eng'] || r['title-titre-fra']),
        description: cleanText(r['tenderDescription-descriptionAppelOffres-eng'] || r['tenderDescription-descriptionAppelOffres-fra']),
        noticeType: TYPE(label),
        noticeTypeLabel: label || null,
        status: r['tenderStatus-appelOffresStatut-eng'] || null,
        buyerName: r['contractingEntityName-nomEntitContractante-eng'] || null,
        buyerCity: r['contractingEntityAddressCity-entiteContractanteAdresseVille-eng'] || null,
        buyerRegion: r['contractingEntityAddressProvince-entiteContractanteAdresseProvince-eng'] || null,
        country: 'CA',
        publishedAt: eastern(r['publicationDate-datePublication'] || r['amendmentDate-dateModification']),
        deadline: eastern(r['tenderClosingDate-appelOffresDateCloture']),
        valueAmount: null,
        valueCurrency: null,
        category: [...new Set(cat)].join(', ') || null,
        procedure: r['procurementMethod-methodeApprovisionnement-eng'] || null,
        unspscCodes: unspsc,
        gsinCodes: list(r['gsin-nibs']),
        tradeAgreements: list(r['tradeAgreements-accordsCommerciaux-eng']),
        regionsOfDelivery: list(r['regionsOfDelivery-regionsLivraison-eng']),
        amendmentNumber: amend && amend !== '000' ? amend : null,
        // Notices hosted on CanadaBuys itself have no URL in the feed: link to a CanadaBuys search for the reference.
        url: r['noticeURL-URLavis-eng'] || `https://canadabuys.canada.ca/en/tender-opportunities?search_filter=${encodeURIComponent(ref)}`,
        documentsUrl: list(r['attachment-piecesJointes-eng'])[0] || null,
        _contact: r['contactInfoEmail-informationsContactCourriel'] || r['contactInfoName-informationsContactNom']
            ? { name: r['contactInfoName-informationsContactNom'] || null, email: r['contactInfoEmail-informationsContactCourriel'] || null, phone: r['contactInfoPhone-contactInfoTelephone'] || null }
            : null,
    };
}
