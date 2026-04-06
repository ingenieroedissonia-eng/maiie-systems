import React from 'react';

const W = 165; const H = 62;
const NODES = [
  { id: 'sub_1', file: 'models.py',          x: 15,  y: 30  },
  { id: 'sub_2', file: 'services.py',         x: 290, y: 30  },
  { id: 'sub_3', file: 'exceptions.py',       x: 565, y: 30  },
  { id: 'sub_4', file: 'routes.py',           x: 130, y: 220 },
  { id: 'sub_5', file: 'document_router.py',  x: 450, y: 220 },
  { id: 'sub_6', file: 'test_services.py',    x: 130, y: 420 },
  { id: 'sub_7', file: 'deploy_run.sh',       x: 450, y: 420 },
];
const cx = n => n.x + W / 2;
const cy = n => n.y + H / 2;
const EDGES = [
  ['sub_1','sub_4'], ['sub_2','sub_4'], ['sub_3','sub_5'],
  ['sub_4','sub_5'], ['sub_4','sub_6'], ['sub_5','sub_7'],
];

const nodeStatus = (i, ms) => {
  if (!ms) return 'idle';
  if (ms.status === 'done') return ms.aprobado ? 'success' : (i > 3 ? 'retrying' : 'success');
  if (ms.status === 'running') return i < 2 ? 'success' : i === 2 ? 'running' : 'pending';
  return 'idle';
};

const nodeLabel = (s) => {
  if (s === 'success') return '✓ AUDITOR: APROBADO';
  if (s === 'running') return 'ENGINEER: IMPLEMENTANDO...';
  if (s === 'retrying') return 'AUDITOR: RECHAZADO, RETRYING...';
  if (s === 'pending') return 'Pending dependency';
  return '';
};

const edgePts = (a, b) => {
  const nmap = Object.fromEntries(NODES.map(n => [n.id, n]));
  const A = nmap[a]; const B = nmap[b];
  if (B.y > A.y + 40) return { x1: cx(A), y1: A.y + H, x2: cx(B), y2: B.y };
  return { x1: A.x + W, y1: cy(A), x2: B.x, y2: cy(B) };
};

const GraphConsole = ({ missionStatus, missionId, selectedNode, onSelectNode }) => {
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

  return (
    <div className="graph-area">
      <div className="graph-header">
        <span>Grafo de la Mision Activa: </span>
        <span className="mission-id">[{missionId}]</span>
      </div>
      <div className="graph-canvas">
        <div style={{position:'relative',width:'760px',height:'520px',margin:'0 auto'}}>
          <svg style={{position:'absolute',top:0,left:0,width:'100%',height:'100%',overflow:'visible',pointerEvents:'none'}} viewBox="0 0 760 520">
            <defs>
              <marker id="arr" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
                <path d="M0,0 L0,7 L7,3.5 z" fill="#1e3050" />
              </marker>
            </defs>
            {EDGES.map(([a, b]) => {
              const p = edgePts(a, b);
              return <line key={a+b} x1={p.x1} y1={p.y1} x2={p.x2} y2={p.y2} stroke="#1e3050" strokeWidth="1.5" markerEnd="url(#arr)" />;
            })}
          </svg>
          {NODES.map((node, i) => {
            const s = nodeStatus(i, missionStatus);
            const lbl = nodeLabel(s);
            const isSel = selectedNode?.id === node.id;
            return (
              <div
                key={node.id}
                className={`graph-node ${s}${isSel ? ' sel' : ''}`}
                style={{left:node.x+'px',top:node.y+'px',width:W+'px',position:'absolute'}}
                onClick={() => onSelectNode({...node, status: s})}
              >
                <div className="node-title">{node.id}: {node.file}</div>
                {lbl && <div className={`node-sub ${s}`}>{lbl}</div>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default GraphConsole;
