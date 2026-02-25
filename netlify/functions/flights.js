// fly-informasjon/netlify/functions/flights.js
exports.handler = async (event) => {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: cors, body: '' };
  }

  try {
    const { airport, timeFrom, timeTo, direction, lastUpdate } = event.queryStringParameters || {};

    if (!airport) {
      return { statusCode: 400, headers: cors, body: 'Missing airport' };
    }
    // direction is optional on your UI; when omitted Avinor returns both A and D
    const params = new URLSearchParams({
      airport: String(airport).toUpperCase(),
      TimeFrom: timeFrom || '1',
      TimeTo: timeTo || '7',
    });
    if (direction) params.set('direction', String(direction).toUpperCase()); // 'A' or 'D'
    if (lastUpdate) params.set('lastUpdate', lastUpdate);

    const url = `https://asrv.avinor.no/XmlFeed/v1.0?${params.toString()}`;

    const resp = await fetch(url, {
      headers: {
        'Accept': 'application/xml,text/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'NetlifyFunction/1.0',
      },
    });

    if (!resp.ok) {
      return { statusCode: resp.status, headers: cors, body: `Avinor error ${resp.status}` };
    }

    const xml = await resp.text();
    return { statusCode: 200, headers: { ...cors, 'Content-Type': 'application/xml; charset=utf-8' }, body: xml };
  } catch (err) {
    return { statusCode: 500, headers: cors, body: `Server error: ${err.message}` };
  }
};
