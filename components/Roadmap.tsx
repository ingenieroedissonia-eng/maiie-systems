import { Button } from "@/components/ui/button";

/**
 * ROADMAP — MAIIE SYSTEMS
 * Controlled system evolution
 */
export function Roadmap() {
  // WhatsApp CTA — AI Blueprint Express
  const whatsappLink =
    "https://wa.me/573212053974?text=Hello%2C%20I%E2%80%99ve%20reviewed%20your%20system%20roadmap%20and%20I%E2%80%99d%20like%20to%20start%20with%20Phase%201%20through%20the%20AI%20Blueprint%20Express.";

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

          {/* FINAL CTA */}
          <div className="pt-8">
            <a href={whatsappLink} target="_blank" rel="noopener noreferrer">
              <Button className="rounded-xl bg-white px-8 py-4 font-bold text-black transition-transform hover:scale-105 active:scale-95">
                Start Phase 1 with AI Blueprint Express
              </Button>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
