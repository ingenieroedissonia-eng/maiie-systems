content = open('src/App.jsx', 'r', encoding='utf-8').read()

old = '''  useEffect(() => {
    getMissions()
      .then(data => {
        const missions = data.missions || [];
        setSystemStats({ total: missions.length });
      })
      .catch(() => setSystemStats({ total: '?' }));
  }, []);'''

new = '''  useEffect(() => {
    let cancelled = false;
    getMissions()
      .then(data => {
        if (!cancelled) {
          const missions = data.missions || [];
          setSystemStats({ total: missions.length });
        }
      })
      .catch(() => { if (!cancelled) setSystemStats({ total: '?' }); });
    return () => { cancelled = true; };
  }, []);'''

if old in content:
    open('src/App.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NO MATCH')
