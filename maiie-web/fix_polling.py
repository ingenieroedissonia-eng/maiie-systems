import sys

old = '''  useEffect(() => {
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

new = '''  useEffect(() => {
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

path = r'src\components\GraphConsole.jsx'
content = open(path, 'r', encoding='utf-8').read()
if old.strip() not in content.replace('\r\n', '\n'):
    print('ERROR: patron no encontrado')
    sys.exit(1)
content = content.replace('\r\n', '\n').replace(old.strip(), new.strip())
open(path, 'w', encoding='utf-8').write(content)
print('OK: polling fix aplicado')
