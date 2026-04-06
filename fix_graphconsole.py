content = '''import React, { useState, useEffect } from 'react';
import { getSubmissions } from '../services/apiService';

const W = 165; const H = 62;

const buildLayout = (submisiones) => {
  const cols = 3;
  return submisiones.map((sub, i) => ({
    id: sub.id,
    file: sub.descripcion.length > 28 ? sub.descripcion.slice(0, 28) + '...' : sub.descripcion,
    descripcion: sub.descripcion,
    status: sub.status || 'pending',
    x: (i % cols) * 280 + 15,
    y: Math.floor(i / cols) * 200 + 30,
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
  if (s === 'pending') return 'Pending dependency';
  return '';
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
    if (!missionId || nodes.length === 0) return;
    if (missionStatus?.status === 'done' || missionStatus?.status === 'running') {
      getSubmissions(missionId)
        .then(data => {
          const subs = data.submisiones || [];
          if (subs.length > 0) setNodes(buildLayout(subs));
        })
        .catch(() => {});
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

  const canvasW = Math.max(760, nodes.length > 0 ? (Math.min(nodes.length, 3) * 280 + 30) : 760);
  const canvasH = Math.max(520, Math.ceil(nodes.length / 3) * 200 + 80);

  return (
    <div className="graph-area">
      <div className="graph-header">
        <span>Grafo de la Mision Activa: </span>
        <span className="mission-id">[{missionId}]</span>
        {loading && <span style={{marginLeft:'12px',fontSize:'0.65rem',color:'var(--text-dim)'}}>Cargando submisiones...</span>}
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
              {nodes.slice(0, -1).map((node, i) => {
                const next = nodes[i + 1];
                if (!next) return null;
                const sameRow = Math.floor(i / 3) === Math.floor((i + 1) / 3);
                return (
                  <line key={node.id + '-' + next.id}
                    x1={sameRow ? node.x + W : cx(node)}
                    y1={sameRow ? cy(node) : node.y + H}
                    x2={sameRow ? next.x : cx(next)}
                    y2={sameRow ? cy(next) : next.y}
                    stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />
                );
              })}
            </svg>
            {nodes.map((node) => {
              const s = nodeStatus(node, missionStatus);
              const lbl = nodeLabel(s);
              const isSel = selectedNode?.id === node.id;
              return (
                <div
                  key={node.id}
                  className={"graph-node " + s + (isSel ? ' sel' : '')}
                  style={{left:node.x+'px',top:node.y+'px',width:W+'px',position:'absolute'}}
                  onClick={() => onSelectNode({...node, status: s})}
                >
                  <div className="node-title">sub_{node.id}: {node.file}</div>
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
export default GraphConsole;'''
open('maiie-web/src/components/GraphConsole.jsx', 'w', encoding='utf-8').write(content)
print('OK')
