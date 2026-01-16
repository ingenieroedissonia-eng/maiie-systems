export function Roadmap() {
  return (
    <section
      id="roadmap"
      className="w-full border-t border-white/5 bg-zinc-950 py-24 text-white"
    >
      <div className="mx-auto max-w-7xl px-6">
        <div className="max-w-3xl space-y-6">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
            System <span className="text-blue-500">Roadmap</span>
          </h2>

          <p className="text-lg text-gray-400 leading-relaxed">
            A controlled evolution plan focused on validation, stability, and
            long-term system integrity.
          </p>

          <ul className="mt-8 space-y-4 text-gray-400">
            <li>
              <strong className="text-white">Phase 1 — Foundation</strong>
              <br />
              Architecture definition, system identity, and execution baseline.
            </li>

            <li>
              <strong className="text-white">Phase 2 — Validation</strong>
              <br />
              Real-world application, feedback loops, and decision traceability.
            </li>

            <li>
              <strong className="text-white">Phase 3 — Scale</strong>
              <br />
              Selective expansion, automation hardening, and governance maturity.
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
