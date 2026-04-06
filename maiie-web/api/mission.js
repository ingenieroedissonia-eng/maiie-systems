export default async function handler(req, res) {
  const API_URL = 'https://maiie-system-247946064488.us-central1.run.app';

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-app-token');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const clientToken = req.headers['x-app-token'];
  if (!clientToken || clientToken !== process.env.APP_TOKEN) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!req.body || !req.body.orden) {
    return res.status(400).json({ error: 'Missing field: orden' });
  }

  try {
    const response = await fetch(`${API_URL}/mission`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.APP_TOKEN
      },
      body: JSON.stringify({ orden: req.body.orden }),
    });
    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (e) {
    return res.status(502).json({ error: 'Backend unreachable', detail: e.message });
  }
}
