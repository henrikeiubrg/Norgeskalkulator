// netlify/functions/styringsrente.js
// Proxy for Norges Bank policy rate (styringsrente) with CORS + simple JSON shape
export async function handler(event) {
  // CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Vary': 'Origin',
      },
    };
  }

  try {
    const q = new URLSearchParams(event.queryStringParameters || {});
    const start = q.get('startdate') || '2024-10-10';
    const stop  = q.get('stopdate')  || new Date().toISOString().slice(0,10);

    // Primary: Querybuilder API (same as your link)
    const qb = new URL('https://app.norges-bank.no/query/api/interest');
    qb.searchParams.set('interesttype', 'KPRA');
    qb.searchParams.set('frequency', 'B');
    qb.searchParams.set('startdate', start);
    qb.searchParams.set('stopdate',  stop);

    // Helper: normalize various response shapes to [{date, value}]
    const normalizeRows = (arr) => {
      const tryDate = (o) => {
        for (const k of ['date','Date','obstime','TIME_PERIOD','time','dato']) {
          if (o?.[k]) { const d = new Date(o[k]); if (!isNaN(+d)) return d; }
        }
        for (const [k,v] of Object.entries(o||{})) {
          if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}/.test(v)) {
            const d = new Date(v); if (!isNaN(+d)) return d;
          }
        }
        return null;
      };
      const tryVal = (o) => {
        for (const k of ['value','Value','OBS_VALUE','rate','Rate','KPRA','OBSERVATION_VALUE']) {
          if (typeof o?.[k] === 'number') return o[k];
          if (typeof o?.[k] === 'string' && !isNaN(parseFloat(o[k]))) return parseFloat(o[k]);
        }
        for (const [k,v] of Object.entries(o||{})) {
          if (typeof v === 'number') return v;
          if (typeof v === 'string' && !isNaN(parseFloat(v))) return parseFloat(v);
        }
        return NaN;
      };
      return (arr || [])
        .map(r => ({ date: tryDate(r)?.toISOString().slice(0,10), value: tryVal(r) }))
        .filter(x => x.date && Number.isFinite(x.value))
        .sort((a,b) => a.date.localeCompare(b.date));
    };

    // Try primary JSON
    let rows = [];
    try {
      const r = await fetch(qb.toString(), { headers: { 'Accept': 'application/json' } });
      if (r.ok) {
        const j = await r.json();
        const arr = Array.isArray(j) ? j : (Array.isArray(j?.data) ? j.data : []);
        rows = normalizeRows(arr);
      }
    } catch { /* fall through */ }

    // Fallback: SDMX IR dataset (KPRA), B then D
    if (!rows.length) {
      const base = 'https://data.norges-bank.no/api/data/IR/';
      const combos = [
        `?contentType=sdmx-json&format=sdmx-json&locale=no&FREQ=B&INSTRUMENT_TYPE=KPRA&startPeriod=${start}&endPeriod=${stop}`,
        `?contentType=sdmx-json&format=sdmx-json&locale=no&FREQ=D&INSTRUMENT_TYPE=KPRA&startPeriod=${start}&endPeriod=${stop}`,
      ];
      for (const c of combos) {
        const r = await fetch(base + c, { headers: { 'Accept': 'application/json' } });
        if (!r.ok) continue;
        const j = await r.json();

        // Parse SDMX → rows
        const ds = j?.data?.datasets?.[0];
        const series = ds?.series || {};
        const obsDim = j?.data?.structure?.dimensions?.observation?.find(d => d.id === 'TIME_PERIOD');
        const times = obsDim?.values || [];
        const out = [];
        for (const key in series) {
          const obs = series[key]?.observations || {};
          for (const idx in obs) {
            const t = times[idx];
            const d = (t?.id || t?.name);
            const v = obs[idx]?.[0];
            if (d != null && v != null) {
              const num = typeof v === 'string' ? parseFloat(v) : v;
              if (Number.isFinite(num)) out.push({ date: d, value: num });
            }
          }
        }
        if (out.length) {
          rows = out.sort((a,b)=>a.date.localeCompare(b.date));
          break;
        }
      }
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 's-maxage=300, stale-while-revalidate=86400',
        'Vary': 'Origin',
      },
      body: JSON.stringify({ source: rows.length ? 'ok' : 'empty', start, stop, data: rows }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Vary': 'Origin',
      },
      body: JSON.stringify({ error: 'proxy_failed', message: String(err) }),
    };
  }
}
