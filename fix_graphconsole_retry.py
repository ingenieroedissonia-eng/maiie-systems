content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = '''        .catch(() => setNodes([]))
        .finally(() => setLoading(false));
  }, [missionId]);'''

new = '''        .catch(() => setNodes([]))
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
  }, [missionId, nodes.length]);'''

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK retry submissions')
else:
    print('NO MATCH')
