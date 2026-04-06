content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = '''  useEffect(() => {
    if (!missionId || nodes.length === 0) return;
    if (missionStatus?.status === 'done' || missionStatus?.status === 'running') {
      getSubmissions(missionId)
        .then(data => {
          const subs = data.submisiones || [];
          if (subs.length > 0) setNodes(buildLayout(subs));
        })
        .catch(() => {});
    }
  }, [missionStatus?.status]);'''

new = '''  useEffect(() => {
    if (!missionId || missionStatus?.status !== 'running') return;
    const poll = setInterval(() => {
      getSubmissions(missionId)
        .then(data => {
          const subs = data.submisiones || [];
          if (subs.length > nodes.length) setNodes(buildLayout(subs));
        })
        .catch(() => {});
    }, 5000);
    return () => clearInterval(poll);
  }, [missionId, missionStatus?.status]);'''

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK GraphConsole polling')
else:
    print('NO MATCH')
