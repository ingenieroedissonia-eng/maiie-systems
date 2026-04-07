content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()

old = '''const buildEdges = (nodes) => {
  const edges = [];
  for (let i = 0; i < nodes.length - 1; i++) {
    const a = nodes[i];
    const b = nodes[i + 1];
    const sameRow = a.row === b.row;
    if (sameRow) {
      edges.push({ x1: a.x + W, y1: cy(a), x2: b.x, y2: cy(b), key: a.id + '-' + b.id });
    } else {
      const lastInRow = nodes.filter(n => n.row === a.row).slice(-1)[0];
      if (lastInRow.id === a.id) {
        edges.push({ x1: cx(a), y1: a.y + H, x2: cx(b), y2: b.y, key: a.id + '-' + b.id });
      }
    }
  }
  return edges;
};'''

new = '''const buildEdges = (nodes) => {
  const edges = [];
  for (let i = 0; i < nodes.length - 1; i++) {
    const a = nodes[i];
    const b = nodes[i + 1];
    const sameRow = a.row === b.row;
    if (sameRow) {
      edges.push({ x1: a.x + W, y1: cy(a), x2: b.x, y2: cy(b), key: a.id + '-' + b.id, bent: false });
    } else {
      const lastInRow = nodes.filter(n => n.row === a.row).slice(-1)[0];
      if (lastInRow.id === a.id) {
        const midY = a.y + H + (b.y - a.y - H) / 2;
        edges.push({ x1: cx(a), y1: a.y + H, x2: cx(a), y2: midY, x3: cx(b), y3: midY, x4: cx(b), y4: b.y, key: a.id + '-' + b.id, bent: true });
      }
    }
  }
  return edges;
};'''

if old in content:
    open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK buildEdges')
else:
    print('NO MATCH')
