export default async function handler(req, res) {
  const API_URL = 'https://maiie-system-247946064488.us-central1.run.app';
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-app-token');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
  try {
    const response = await fetch(API_URL + '/system/metrics', {
      headers: { 'X-API-Key': process.env.APP_TOKEN },
    });
    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (e) {
    return res.status(502).json({ error: 'Backend unreachable', detail: e.message });
  }
}
