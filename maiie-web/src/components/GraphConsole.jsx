import React, { useState, useEffect } from 'react';
import { getSubmissions } from '../services/apiService';

const W = 200; const H = 70;
const COLS = 3;
const COL_GAP = 260;
const ROW_GAP = 160;
const PAD_X = 20;
const PAD_Y = 30;

const buildLayout = (submisiones) => {
  return submisiones.map((sub, i) => ({
    id: sub.id,
    file: sub.descripcion.length > 40 ? sub.descripcion.slice(0, sub.descripcion.lastIndexOf(' ', 40)) + '...' : sub.descripcion,
    descripcion: sub.descripcion,
    status: sub.status || 'pending',
    x: (i % COLS) * COL_GAP + PAD_X,
    y: Math.floor(i / COLS) * ROW_GAP + PAD_Y,
    col: i % COLS,
    row: Math.floor(i / COLS),
  }));
};

const cx = n => n.x + W / 2;
const cy = n => n.y + H / 2;

const nodeStatus = (node, missionStatus) => {
  if (!missionStatus) return 'idle';
  if (node.status === 'done') return 'success';
  if (node.status === 'running') return 'running';
  if (node.status === 'error') return 'retrying';
  if (missionStatus.status === 'done') return 'success';
  if (missionStatus.status === 'running') return 'pending';
  return 'idle';
};

const nodeLabel = (s) => {
  if (s === 'success') return 'AUDITOR: APROBADO';
  if (s === 'running') return 'ENGINEER: IMPLEMENTANDO...';
  if (s === 'retrying') return 'AUDITOR: RECHAZADO';
  if (s === 'pending') return 'Pending';
  return '';
};

const buildEdges = (nodes) => {
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
};

const GraphConsole = ({ missionStatus, missionId, selectedNode, onSelectNode }) => {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!missionId) { setNodes([]); return; }
    setLoading(true);
    getSubmissions(missionId)
      .then(data => {
        const subs = data.submisiones || [];
        if (subs.length > 0) {
          setNodes(buildLayout(subs));
        } else {
          setNodes([]);
        }
      })
      .catch(() => setNodes([]))
      .finally(() => setLoading(false));
  }, [missionId]);

  useEffect(() => {
    if (!missionId || nodes.length !== 0) return;
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
  }, [missionStatus?.status]);

  if (!missionId) return (
    <div className="graph-area">
      <div className="graph-header">
        <span>Grafo de la Mision Activa: </span>
        <span className="mission-id">—</span>
      </div>
      <div className="graph-canvas">
        <div className="graph-empty">
          <div className="ei">⬡</div>
          <p>No hay mision activa. Inicia una nueva mision.</p>
        </div>
      </div>
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
        {nodes.length === 0 && !loading && (
          <div className="graph-empty">
            <div className="ei">⬡</div>
            <p>Iniciando pipeline...</p>
          </div>
        )}
        {nodes.length > 0 && (
          <div style={{position:'relative',width:canvasW+'px',height:canvasH+'px',margin:'0 auto'}}>
            <svg style={{position:'absolute',top:0,left:0,width:'100%',height:'100%',overflow:'visible',pointerEvents:'none'}} viewBox={"0 0 "+canvasW+" "+canvasH}>
              <defs>
                <marker id="arr" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
                  <path d="M0,0 L0,7 L7,3.5 z" fill="#1e3050" />
                </marker>
              </defs>
              {edges.map(e => e.bent ? (
                <polyline key={e.key}
                  points={e.x1+','+e.y1+' '+e.x2+','+e.y2+' '+e.x3+','+e.y3+' '+e.x4+','+e.y4}
                  fill="none" stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
              ) : (
                <line key={e.key} x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
                  stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
              ))}
            </svg>
            {nodes.map((node) => {
              const s = nodeStatus(node, missionStatus);
              const lbl = nodeLabel(s);
              const isSel = selectedNode?.id === node.id;
              return (
                <div
                  key={node.id}
                  className={"graph-node " + s + (isSel ? " sel" : "")}
                  style={{left:node.x+"px",top:node.y+"px",width:W+"px",position:"absolute"}}
                  onClick={() => onSelectNode({...node, status: s})}
                >
                  <div className="node-title" style={{fontSize:"0.72rem",lineHeight:"1.3",wordBreak:"break-word"}}>sub_{node.id}: {node.file}</div>
                  {lbl && <div className={"node-sub " + s}>{lbl}</div>}
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