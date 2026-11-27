// Shared helpers: HTTP with retries, dates, text cleanup, countries, currencies, filters.

export const UA = 'public-tenders-feed/1.0 (Apify actor; official open-data APIs)';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** Fetch with retries on network errors, 429 and 5xx. Returns the Response (ok) or throws. */
/** Milliseconds a 429 response asks us to wait (Retry-After seconds/date, or "try again in N minutes"), or null. */
export function retryAfterMs(header, body = '') {
    if (header) {
        const secs = Number(header);
        if (Number.isFinite(secs)) return Math.max(0, secs * 1000);
        const t = Date.parse(header);
        if (!Number.isNaN(t)) return Math.max(0, t - Date.now());
    }
    const m = /try again in (\d+)\s*(second|minute)/i.exec(body || '');
    if (m) return Number(m[1]) * (/minute/i.test(m[2]) ? 60000 : 1000);
    return null;
}

const RATE_LIMITED_HOSTS = new Set();

/** Longest rate-limit wait we accept: 150 s, but never past the run's timeout (minus 30 s to save results). */
function waitBudgetMs() {
    const end = Date.parse(process.env.ACTOR_TIMEOUT_AT || '');
    return Number.isNaN(end) ? 150000 : Math.min(150000, end - Date.now() - 30000);
}

export async function fetchRetry(url, opts = {}, { tries = 4, timeoutMs = 60000, maxWaitMs, log } = {}) {
    let lastErr;
    for (let attempt = 1; attempt <= tries; attempt++) {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), timeoutMs);
        try {
            const res = await fetch(url, { ...opts, signal: ctrl.signal, headers: { 'user-agent': UA, accept: 'application/json, text/csv, */*', ...(opts.headers || {}) } });
            if (res.ok) return res;
            const body = await res.text().catch(() => '');
            lastErr = new Error(`HTTP ${res.status} from ${new URL(url).host}: ${body.slice(0, 200)}`);
            if (res.status < 500 && res.status !== 429) throw Object.assign(lastErr, { fatal: true });
            if (res.status === 429 && attempt < tries) {
                // Rate limited: wait as long as the server asks (Retry-After or "try again in N minutes"), up to maxWaitMs.
                const wait = retryAfterMs(res.headers.get('retry-after'), body);
                const host = new URL(url).host;
                if (wait != null) {
                    // Wait at most once per host and run: a second 429 means we'd keep the user waiting for nothing.
                    if (wait > (maxWaitMs ?? waitBudgetMs()) || RATE_LIMITED_HOSTS.has(host)) throw lastErr;
                    RATE_LIMITED_HOSTS.add(host);
                    log?.info?.(`${host} is rate limiting us; waiting ${Math.ceil(wait / 1000)} s as it asks.`);
                    await sleep(wait + 500);
                    continue;
                }
            }
        } catch (e) {
            if (e.fatal) throw e;
            lastErr = e.name === 'AbortError' ? new Error(`Timeout after ${timeoutMs / 1000}s: ${url}`) : e;
        } finally {
            clearTimeout(timer);
        }
        if (attempt < tries) {
            log?.debug?.(`Retry ${attempt} for ${url}: ${lastErr.message}`);
            await sleep(1000 * 2 ** attempt);
        }
    }
    throw lastErr;
}

export async function fetchJson(url, opts, cfg) {
    const res = await fetchRetry(url, opts, cfg);
    return res.json();
}

/** Run async fn over items with limited concurrency. */
export async function mapLimit(items, limit, fn) {
    const out = new Array(items.length);
    let i = 0;
    const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
        while (i < items.length) {
            const idx = i++;
            out[idx] = await fn(items[idx], idx);
        }
    });
    await Promise.all(workers);
    return out;
}

// ---------- text ----------

const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', rsquo: '’', lsquo: '‘', rdquo: '”', ldquo: '“', ndash: '–', mdash: '—', hellip: '…', eacute: 'é', egrave: 'è', ecirc: 'ê', agrave: 'à', acirc: 'â', ccedil: 'ç', ocirc: 'ô', icirc: 'î', ucirc: 'û', ugrave: 'ù', euml: 'ë', iuml: 'ï', Eacute: 'É', bull: '•', middot: '·', deg: '°', reg: '®', copy: '©', trade: '™' };

const ACCENTS = { acute: '\u0301', grave: '\u0300', circ: '\u0302', uml: '\u0308', tilde: '\u0303', cedil: '\u0327', ring: '\u030a' };

export function cleanText(s, { maxLength } = {}) {
    if (s == null) return null;
    let t = String(s)
        .replace(/<\s*(br|\/p|\/div|\/li|\/h\d)\s*\/?>/gi, '\n')
        .replace(/<li[^>]*>/gi, '\n• ')
        .replace(/<[^>]+>/g, '')
        .replace(/&#x([0-9a-f]+);/gi, (_, x) => String.fromCodePoint(parseInt(x, 16)))
        .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
        .replace(/&([A-Za-z])(acute|grave|circ|uml|tilde|cedil|ring);/g, (m, l, k) => `${l}${ACCENTS[k]}`.normalize('NFC'))
        .replace(/&([a-z]+);/gi, (m, n) => ENTITIES[n] ?? m)
        .replace(/\r/g, '')
        .replace(/[ \t ]+/g, ' ')
        .replace(/ *\n */g, '\n')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
    if (maxLength && t.length > maxLength) t = `${t.slice(0, maxLength - 1).trimEnd()}…`;
    return t || null;
}

// ---------- dates ----------

/** Parse many date shapes to ISO string (UTC) or null. Handles TED "2026-12-10+02:00", WB "11-Nov-2026". */
export function toIso(d, time) {
    if (!d) return null;
    let s = String(d).trim();
    let m = s.match(/^(\d{4}-\d{2}-\d{2})([+-]\d{2}:\d{2}|Z)$/); // date with offset (TED)
    if (m) s = `${m[1]}T${time ? time.replace(/([+-]\d{2}:\d{2}|Z)$/, '') : '00:00:00'}${m[2]}`;
    m = s.match(/^(\d{1,2})-([A-Za-z]{3})-(\d{4})$/); // 11-Nov-2026
    if (m) s = `${m[1]} ${m[2]} ${m[3]} 00:00:00 UTC`;
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) s = `${s}T${time || '00:00:00'}Z`;
    const t = Date.parse(s);
    return Number.isNaN(t) ? null : new Date(t).toISOString();
}

export const ymd = (date) => date.toISOString().slice(0, 10);

export function daysLeft(deadlineIso, now = Date.now()) {
    if (!deadlineIso) return null;
    return Math.floor((Date.parse(deadlineIso) - now) / 86400000);
}

// ---------- countries ----------

const REGION_NAMES = new Intl.DisplayNames(['en'], { type: 'region' });
export const countryName = (iso2) => {
    if (!iso2) return null;
    try { return REGION_NAMES.of(iso2.toUpperCase()); } catch { return null; }
};

// ISO 3166 alpha-3 -> alpha-2 for countries that publish on TED (EU, EEA, candidates, neighbours) and a few others.
const A3 = {
    AUT: 'AT', BEL: 'BE', BGR: 'BG', HRV: 'HR', CYP: 'CY', CZE: 'CZ', DNK: 'DK', EST: 'EE', FIN: 'FI', FRA: 'FR', DEU: 'DE', GRC: 'GR', HUN: 'HU', IRL: 'IE', ITA: 'IT', LVA: 'LV', LTU: 'LT', LUX: 'LU', MLT: 'MT', NLD: 'NL', POL: 'PL', PRT: 'PT', ROU: 'RO', SVK: 'SK', SVN: 'SI', ESP: 'ES', SWE: 'SE',
    NOR: 'NO', ISL: 'IS', LIE: 'LI', CHE: 'CH', GBR: 'GB', MKD: 'MK', SRB: 'RS', MNE: 'ME', ALB: 'AL', BIH: 'BA', XKX: 'XK', MDA: 'MD', UKR: 'UA', GEO: 'GE', ARM: 'AM', TUR: 'TR', USA: 'US', CAN: 'CA', AUS: 'AU',
    BLR: 'BY', AZE: 'AZ', MAR: 'MA', TUN: 'TN', EGY: 'EG', ISR: 'IL', JOR: 'JO', LBN: 'LB', PSE: 'PS', SEN: 'SN', KEN: 'KE', ETH: 'ET', NGA: 'NG', ZAF: 'ZA', IND: 'IN', CHN: 'CN', JPN: 'JP', BRA: 'BR', MEX: 'MX',
};
const A2_TO_A3 = Object.fromEntries(Object.entries(A3).map(([a3, a2]) => [a2, a3]));
export const iso3to2 = (a3) => (a3 ? A3[a3.toUpperCase()] ?? null : null);
export const iso2to3 = (a2) => (a2 ? A2_TO_A3[a2.toUpperCase()] ?? null : null);

let nameMap;
/** Country name (English) -> ISO2, using ICU names plus World Bank spellings. */
export function countryFromName(name) {
    if (!name) return null;
    if (!nameMap) {
        nameMap = new Map();
        for (let a = 65; a <= 90; a++) for (let b = 65; b <= 90; b++) {
            const code = String.fromCharCode(a, b);
            let n;
            try { n = REGION_NAMES.of(code); } catch { continue; }
            if (n && n !== code) nameMap.set(norm(n), code);
        }
        const extra = {
            'congo, democratic republic of': 'CD', 'congo, republic of': 'CG', 'egypt, arab republic of': 'EG', 'yemen, republic of': 'YE', 'iran, islamic republic of': 'IR',
            'korea, republic of': 'KR', 'lao people\'s democratic republic': 'LA', 'gambia, the': 'GM', 'bahamas, the': 'BS', 'micronesia, federated states of': 'FM', 'venezuela, republica bolivariana de': 'VE',
            'kyrgyz republic': 'KG', 'slovak republic': 'SK', 'turkiye': 'TR', 'turkey': 'TR', 'cote d\'ivoire': 'CI', 'west bank and gaza': 'PS', 'syrian arab republic': 'SY', 'st. lucia': 'LC', 'st. vincent and the grenadines': 'VC',
            'st. kitts and nevis': 'KN', 'sao tome and principe': 'ST', 'timor-leste': 'TL', 'cabo verde': 'CV', 'eswatini': 'SZ', 'north macedonia': 'MK', 'kosovo': 'XK', 'myanmar': 'MM', 'czech republic': 'CZ', 'russian federation': 'RU', 'viet nam': 'VN', 'vietnam': 'VN',
        };
        for (const [k, v] of Object.entries(extra)) nameMap.set(norm(k), v);
    }
    return nameMap.get(norm(name)) ?? null;
}
function norm(s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[’`]/g, "'").replace(/\s+/g, ' ').trim(); }

// ---------- currencies (ECB daily reference rates, EUR base) ----------

export async function loadFxRates(log) {
    try {
        const res = await fetchRetry('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml', {}, { tries: 3, timeoutMs: 20000, log });
        const xml = await res.text();
        const rates = { EUR: 1 };
        for (const m of xml.matchAll(/currency=['"]([A-Z]{3})['"]\s+rate=['"]([\d.]+)['"]/g)) rates[m[1]] = Number(m[2]);
        const date = xml.match(/time=['"](\d{4}-\d{2}-\d{2})['"]/)?.[1] ?? null;
        if (!rates.USD) throw new Error('no USD rate');
        return { rates, date };
    } catch (e) {
        log?.warning?.(`Currency rates unavailable (${e.message}); valueEur/valueUsd will be empty.`);
        return { rates: null, date: null };
    }
}

export function convert(amount, currency, fx) {
    if (amount == null || !currency || !fx?.rates) return { valueEur: null, valueUsd: null };
    const r = fx.rates[currency.toUpperCase()];
    if (!r) return { valueEur: null, valueUsd: null };
    const eur = amount / r;
    return { valueEur: Math.round(eur), valueUsd: Math.round(eur * fx.rates.USD) };
}

export const num = (v) => {
    if (v == null || v === '') return null;
    const n = Number(String(v).replace(/[, ]/g, ''));
    return Number.isFinite(n) ? n : null;
};

// ---------- keyword matching ----------

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
/**
 * US federal notices (SAM.gov) repeat FAR/DFARS clause lists in nearly every description, e.g.
 * "NOTICE OF CYBERSECURITY MATURITY MODEL CERTIFICATION LEVEL REQUIREMENTS (NOV 2025)" or
 * "252.204-7012 Safeguarding Covered Defense Information". Remove them before keyword matching.
 */
const MONTHS = '(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\\.?';
const CLAUSE_TITLE = new RegExp(`[A-Z0-9][A-Z0-9 ,.'’/&\\-–—:]{8,}?(?:\\s*\\((?:DEV(?:IATION)?|ALT(?:ERNATE)?)[^)]{0,40}\\))*\\s*\\((?:[A-Z ]{0,15})?${MONTHS}\\s*\\d{4}\\)`, 'g');
const CLAUSE_NUMBER = /\b(?:52|252|552|1852|5352|3052)\.\d{3}-\d{1,4}[A-Za-z]?(?:\s*(?:\([a-z0-9]+\))*)?[^|\n;.]{0,160}/g;
// Compliance requirements that appear in most DoD notices whatever is being bought.
const COMPLIANCE_PHRASES = /cyber\s*security\s+maturity\s+model\s+certification(?:\s*\(CMMC\))?|\bCMMC\b|cyber\s*security\s+supply\s+chain\s+risk\s+management|\bC-SCRM\b|NIST\s+SP\s+800-171/gi;
export function stripClauses(text) {
    return String(text || '').replace(CLAUSE_TITLE, ' ').replace(CLAUSE_NUMBER, ' ').replace(COMPLIANCE_PHRASES, ' ').replace(/\s+/g, ' ');
}

export function keywordMatchers(keywords) {
    return (keywords || []).map((k) => String(k).trim()).filter(Boolean).map((k) => ({
        keyword: k,
        re: new RegExp(`(^|[^\\p{L}\\p{N}])${escapeRe(k.normalize('NFC')).replace(/\s+/g, '\\s+')}`, 'iu'),
    }));
}
export function matchKeywords(matchers, text) {
    if (!matchers.length) return [];
    const t = (text || '').normalize('NFC');
    return matchers.filter((m) => m.re.test(t)).map((m) => m.keyword);
}

/** CPV/NAICS/UNSPSC prefix: "72000000" -> "72", "541511" -> "541511", "7220" -> "7220". */
export function codePrefix(code, scheme) {
    const c = String(code).replace(/[^0-9]/g, '');
    if (!c) return null;
    if (scheme === 'CPV') return c.slice(0, 8).replace(/0+$/, '').padEnd(2, '0');
    if (scheme === 'UNSPSC') return c.replace(/(00)+$/, '') || c;
    return c;
}
