import { Button } from "@/components/ui/button";

/**
 * ROADMAP — MAIIE SYSTEMS
 * Controlled system evolution
 * Validation-first growth model
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

          {/* TITLE */}
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
            System <span className="text-blue-500">Roadmap</span>
          </h2>

          {/* INTRO */}
          <p className="text-lg text-gray-400 leading-relaxed">
            A controlled evolution plan designed to validate architecture,
            stabilize decision systems, and scale responsibly over time.
          </p>

          {/* PHASES */}
          <ul className="mt-8 space-y-6 text-gray-400">

            <li>
              <strong className="text-white">
                Phase 1 — Foundation
              </strong>
              <p className="mt-1">
                Architecture definition, system identity, and operational
                baseline for decision infrastructure.
              </p>
            </li>

            <li>
              <strong className="text-white">
                Phase 2 — Validation
              </strong>
              <p className="mt-1">
                Real-world implementation, feedback loops, and measurable
                decision traceability.
              </p>
            </li>

            <li>
              <strong className="text-white">
                Phase 3 — Scale
              </strong>
              <p className="mt-1">
                Selective expansion, automation hardening, and governance
                maturity across systems.
              </p>
            </li>

          </ul>

          {/* FINAL CTA */}
          <div className="pt-10">
            <a
              href={whatsappLink}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Start Phase 1 with AI Blueprint Express"
            >
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