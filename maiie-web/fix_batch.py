import sys

path_graph = r'src\components\GraphConsole.jsx'
path_app = r'src\App.jsx'

content_graph = open(path_graph, 'r', encoding='utf-8').read().replace('\r\n', '\n')
content_app = open(path_app, 'r', encoding='utf-8').read().replace('\r\n', '\n')

errors = []

# FIX 1 — Nodos verdes: cuando mision done, forzar todos los nodos a success
old1 = '''  useEffect(() => {
    if (!missionId || missionStatus?.status !== 'running') return;
    const poll = setInterval(() => {
      getSubmissions(missionId)
        .then(data => {
          const subs = data.submisiones || [];
          if (subs.length > 0) setNodes(buildLayout(subs));
          if (data.status === 'done' || data.status === 'completed') {
            clearInterval(poll);
          }
        })
        .catch(() => {});
    }, 5000);
    return () => clearInterval(poll);
  }, [missionId, missionStatus?.status]);'''

new1 = '''  useEffect(() => {
    if (!missionId || missionStatus?.status !== 'running') return;
    const poll = setInterval(() => {
      getSubmissions(missionId)
        .then(data => {
          const subs = data.submisiones || [];
          if (subs.length > 0) setNodes(buildLayout(subs));
          if (data.status === 'done' || data.status === 'completed') {
            setNodes(prev => prev.map(n => ({ ...n, status: 'done' })));
            clearInterval(poll);
          }
        })
        .catch(() => {});
    }, 5000);
    return () => clearInterval(poll);
  }, [missionId, missionStatus?.status]);

  useEffect(() => {
    if (missionStatus?.status === 'done') {
      setNodes(prev => prev.map(n => ({ ...n, status: 'done' })));
    }
  }, [missionStatus?.status]);'''

if old1.strip() in content_graph:
    content_graph = content_graph.replace(old1.strip(), new1.strip())
    print('FIX 1 OK: nodos verdes')
else:
    errors.append('FIX 1 FAIL: patron no encontrado en GraphConsole.jsx')

# FIX 2 — GET /missions 4x: centralizar en App.jsx, pasar missions como prop a HistorialView
old2 = '''function HistorialView() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMissions()
      .then(data => setMissions(data.missions || []))
      .catch(() => setMissions([]))
      .finally(() => setLoading(false));
  }, []);'''

new2 = '''function HistorialView({ missions: propMissions }) {
  const [missions, setMissions] = useState(propMissions || []);
  const [loading, setLoading] = useState(!propMissions);

  useEffect(() => {
    if (propMissions) { setMissions(propMissions); setLoading(false); return; }
    getMissions()
      .then(data => setMissions(data.missions || []))
      .catch(() => setMissions([]))
      .finally(() => setLoading(false));
  }, [propMissions]);'''

if old2.strip() in content_app:
    content_app = content_app.replace(old2.strip(), new2.strip())
    print('FIX 2a OK: HistorialView acepta prop missions')
else:
    errors.append('FIX 2a FAIL: patron HistorialView no encontrado')

old2b = '''  const [systemStats, setSystemStats] = useState(null);'''
new2b = '''  const [systemStats, setSystemStats] = useState(null);
  const [allMissions, setAllMissions] = useState(null);'''

if old2b.strip() in content_app:
    content_app = content_app.replace(old2b.strip(), new2b.strip())
    print('FIX 2b OK: estado allMissions agregado')
else:
    errors.append('FIX 2b FAIL: patron estado no encontrado')

old2c = '''      .then(data => {
        if (!cancelled) {
          const missions = data.missions || [];
          setSystemStats({ total: missions.length });
        }
      })
      .catch(() => { if (!cancelled) setSystemStats({ total: '?' }); });'''
new2c = '''      .then(data => {
        if (!cancelled) {
          const missions = data.missions || [];
          setSystemStats({ total: missions.length });
          setAllMissions(missions);
        }
      })
      .catch(() => { if (!cancelled) setSystemStats({ total: '?' }); });'''

if old2c.strip() in content_app:
    content_app = content_app.replace(old2c.strip(), new2c.strip())
    print('FIX 2c OK: allMissions poblado en fetch inicial')
else:
    errors.append('FIX 2c FAIL: patron fetch inicial no encontrado')

old2d = '''            <HistorialView />'''
new2d = '''            <HistorialView missions={allMissions} />'''

if old2d.strip() in content_app:
    content_app = content_app.replace(old2d.strip(), new2d.strip())
    print('FIX 2d OK: prop missions pasada a HistorialView')
else:
    errors.append('FIX 2d FAIL: patron HistorialView JSX no encontrado')

open(path_graph, 'w', encoding='utf-8').write(content_graph)
open(path_app, 'w', encoding='utf-8').write(content_app)

if errors:
    print()
    for e in errors: print('ERROR:', e)
    sys.exit(1)
else:
    print()
    print('TODOS LOS FIXES APLICADOS OK')
