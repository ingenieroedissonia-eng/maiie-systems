import React, { useState, useEffect, useRef } from 'react';
import { getSubmissions } from '../services/apiService';

const W = 200; const H = 70;
const COLS = 3; const COL_GAP = 260; const ROW_GAP = 160;
const PAD_X = 20; const PAD_Y = 30;

const buildLayout = (submissions) => submissions.map((sub, i) => {
  const text = sub.descripcion || '';
  let file = text;
  if (text.length > 40) {
    const cut = text.slice(0, 40);
    const lastSpace = cut.lastIndexOf(' ');
    file = (lastSpace > 0 ? cut.slice(0, lastSpace) : cut) + '...';
  }
  return { id: sub.id, file, descripcion: sub.descripcion, feedback: sub.feedback || null, codigo: sub.codigo || null, status: sub.status || 'pending',
    x: (i % COLS) * COL_GAP + PAD_X, y: Math.floor(i / COLS) * ROW_GAP + PAD_Y,
    col: i % COLS, row: Math.floor(i / COLS) };
});

const cx = n => n.x + W / 2;
const cy = n => n.y + H / 2;

const nodeStatus = (node, done) => {
  if (done || node.status === 'done') return 'success';
  if (node.status === 'running') return 'running';
  if (node.status === 'error') return 'retrying';
  return 'pending';
};

const nodeLabel = (s) => {
  if (s === 'success') return 'AUDITOR: APROBADO';
  if (s === 'running') return 'ENGINEER: IMPLEMENTANDO...';
  if (s === 'retrying') return 'AUDITOR: RECHAZADO';
  if (s === 'pending') return 'En cola...';
  return '';
};

const buildEdges = (nodes) => {
  const edges = [];
  for (let i = 0; i < nodes.length - 1; i++) {
    const a = nodes[i]; const b = nodes[i + 1];
    if (a.row === b.row) {
      edges.push({ x1: a.x+W, y1: cy(a), x2: b.x, y2: cy(b), key: a.id+'-'+b.id, bent: false });
    } else {
      const last = nodes.filter(n => n.row === a.row).slice(-1)[0];
      if (last.id === a.id) {
        const rx = a.x + W + 20;
        edges.push({ x1: a.x+W, y1: cy(a), x2: rx, y2: cy(a), x3: rx, y3: cy(b), x4: b.x, y4: cy(b), key: a.id+'-'+b.id, bent: true });
      }
    }
  }
  return edges;
};

const GraphConsole = ({ missionStatus, missionId, selectedNode, onSelectNode, onCodigoGenerado }) => {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const pollRef = useRef(null);
  const done = missionStatus?.status === 'done' || missionStatus?.status === 'error';

  useEffect(() => {
    if (!missionId) { setNodes([]); return; }
    setNodes([]); setLoading(true);
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    let stopped = false;
    const fetch = () => {
      getSubmissions(missionId).then(data => {
        if (stopped) return;
        const subs = data.submisiones || [];
        const isDone = data.status === 'done' || data.status === 'completed' || data.status === 'error';
        if (data.codigo_generado && onCodigoGenerado) onCodigoGenerado(data.codigo_generado);
        if (subs.length > 0) {
          setNodes(buildLayout(isDone ? subs.map(s => ({...s, status: 'done'})) : subs));
          setLoading(false);
        }
        if (isDone) {
          stopped = true;
          if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
          setLoading(false);
        }
      }).catch(() => setLoading(false));
    };
    fetch();
    pollRef.current = setInterval(() => { if (stopped) { clearInterval(pollRef.current); return; } fetch(); }, 3000);
    return () => { stopped = true; if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; } };
  }, [missionId]);

  useEffect(() => {
    if (done && nodes.length > 0) {
      setNodes(prev => prev.map(n => ({...n, status: 'done'})));
      if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    }
  }, [done]);

  if (!missionId) return (
    <div className="graph-area">
      <div className="graph-header"><span>Grafo de la Mision Activa: </span><span className="mission-id">--</span></div>
      <div className="graph-canvas"><div className="graph-empty"><div className="ei">O</div><p>No hay mision activa. Inicia una nueva mision.</p></div></div>
    </div>
  );

  const totalRows = nodes.length > 0 ? Math.ceil(nodes.length / COLS) : 1;
  const canvasW = Math.max(800, COLS * COL_GAP + PAD_X * 2);
  const canvasH = Math.max(400, totalRows * ROW_GAP + PAD_Y * 2 + H);
  const edges = buildEdges(nodes);

  return (
    <div className="graph-area">
      <div className="graph-header">
        <span>Grafo de la Mision Activa: </span>
        <span className="mission-id">[{missionId}]</span>
        {loading && <span style={{marginLeft:'12px',fontSize:'0.65rem',color:'var(--text-dim)'}}>Cargando...</span>}
        {nodes.length > 0 && <span style={{marginLeft:'12px',fontSize:'0.65rem',color:'var(--text-dim)'}}>{nodes.length} submision(es)</span>}
      </div>
      <div className="graph-canvas">
        {nodes.length === 0 && !loading && <div className="graph-empty"><div className="ei">O</div><p>Iniciando pipeline...</p></div>}
        {nodes.length > 0 && (
          <div style={{position:'relative',width:canvasW+'px',height:canvasH+'px',margin:'0 auto'}}>
            <svg style={{position:'absolute',top:0,left:0,width:'100%',height:'100%',overflow:'visible',pointerEvents:'none'}} viewBox={"0 0 "+canvasW+" "+canvasH}>
              <defs><marker id="arr" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto"><path d="M0,0 L0,7 L7,3.5 z" fill="#1e3050" /></marker></defs>
              {edges.map(e => e.bent ? (
                <polyline key={e.key} points={e.x1+','+e.y1+' '+e.x2+','+e.y2+' '+e.x3+','+e.y3+' '+e.x4+','+e.y4} fill="none" stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
              ) : (
                <line key={e.key} x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2} stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
              ))}
            </svg>
            {nodes.map(node => {
              const s = nodeStatus(node, done); const lbl = nodeLabel(s); const isSel = selectedNode?.id === node.id;
              return (
                <div key={node.id} className={"graph-node "+s+(isSel?" sel":"")} style={{left:node.x+"px",top:node.y+"px",width:W+"px",position:"absolute"}} onClick={() => onSelectNode({...node, status: s})}>
                  <div className="node-title" style={{fontSize:"0.72rem",lineHeight:"1.3",wordBreak:"break-word"}}>sub_{node.id}: {node.file}</div>
                  {lbl && <div className={"node-sub "+s}>{lbl}</div>}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
export default GraphConsole;