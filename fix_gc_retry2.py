content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = '''      .catch(() => setNodes([]))
      .finally(() => setLoading(false));
  }, [missionId]);

  useEffect(() => {
    if (!missionId || nodes.length === 0) return;'''

new = '''      .catch(() => setNodes([]))
      .finally(() => setLoading(false));
  }, [missionId]);

  useEffect(() => {
    if (!missionId || nodes.length > 0) return;
    const retry = setInterval(() => {
      getSubmissions(missionId)
        .then(data => {
          const subs = data.submisiones || [];
          if (subs.length > 0) {
            setNodes(buildLayout(subs));
            clearInterval(retry);
          }
        })
        .catch(() => {});
    }, 3000);
    return () => clearInterval(retry);
  }, [missionId, nodes.length]);

  useEffect(() => {
    if (!missionId || nodes.length === 0) return;'''

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK retry added')
else:
    print('NO MATCH')
