// netlify/functions/kassalapp.js

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const { endpoint, ...params } = event.queryStringParameters || {};
  if (!endpoint) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'endpoint query param is required' }) };
  }

  // Use your (non-secret) key here
  const API_KEY = 'k0DMuO9IfPaEmCAWxIrthn3QWJhJMwwxBe4gzeHX';

  const baseUrl = 'https://kassal.app/api/v1';
  const qs = new URLSearchParams(params).toString();
  const url = `${baseUrl}/${endpoint}${qs ? `?${qs}` : ''}`;

  try {
    const resp = await fetch(url, {
      method: event.httpMethod === 'POST' ? 'POST' : 'GET',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: event.httpMethod === 'POST' ? event.body : undefined
    });

    const text = await resp.text();
    return {
      statusCode: resp.status,
      headers: { ...headers, 'Cache-Control': 'public, max-age=300' },
      body: text
    };
  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Proxy error', details: err.message }) };
  }
};
