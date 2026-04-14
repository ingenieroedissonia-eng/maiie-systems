content = open('maiie-web/src/components/GraphConsole.jsx', encoding='utf-8').read()

old = """    id: sub.id, file, descripcion: sub.descripcion,
    status: sub.status || 'pending',
    x: (i % dCols) * COL_GAP + PAD_X,
    y: Math.floor(i / dCols) * ROW_GAP + PAD_Y,
    col: i % dCols, row: Math.floor(i / dCols)"""

new = """    id: sub.id, file, descripcion: sub.descripcion,
    status: sub.status || 'pending',
    feedback: sub.feedback || null,
    codigo: sub.codigo || null,
    x: (i % dCols) * COL_GAP + PAD_X,
    y: Math.floor(i / dCols) * ROW_GAP + PAD_Y,
    col: i % dCols, row: Math.floor(i / dCols)"""

content = content.replace(old, new)
open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content)
print('OK:', 'feedback: sub.feedback' in content)
