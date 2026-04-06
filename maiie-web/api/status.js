export default async function handler(req, res) {
  const token = req.headers['x-app-token'];
  if (token !== process.env.APP_TOKEN) {
    return res.status(401).json({ error: 'No autorizado' });
  }
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
  const { id } = req.query;
  try {
    const response = await fetch(`${process.env.VITE_API_URL}/mission/${id}/status`, {
      headers: { 'X-API-Key': process.env.VITE_API_KEY },
    });
    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
