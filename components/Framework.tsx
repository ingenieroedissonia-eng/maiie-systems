import { Button } from "@/components/ui/button";

/**
 * FRAMEWORK — MAIIE SYSTEMS
 * Decision-first engineering methodology
 */

export function Framework() {
  // WhatsApp CTA — AI Blueprint Express
  const whatsappLink =
    "https://wa.me/573212053974?text=Hello%2C%20I%E2%80%99ve%20reviewed%20the%20M.A.I.I.E.%20Framework%20and%20I%E2%80%99d%20like%20to%20start%20with%20the%20AI%20Blueprint%20Express.";

  return (
    <section
      id="framework"
      className="w-full border-t border-white/5 bg-black py-24 text-white"
    >
      <div className="mx-auto max-w-7xl px-6">

        <div className="max-w-3xl space-y-8">

          {/* TITLE */}
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
            The <span className="text-blue-500">M.A.I.I.E.</span> Framework
          </h2>

          {/* INTRO */}
          <p className="text-lg text-gray-400 leading-relaxed">
            A decision-first engineering methodology designed to transform
            complex AI opportunities into auditable, economically sound
            decision systems.
          </p>

          {/* FRAMEWORK STEPS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-400">

            <div>
              <p className="text-white font-semibold">M — Map the Opportunity</p>
              <p>Identify the decision surface where AI can create measurable value.</p>
            </div>

            <div>
              <p className="text-white font-semibold">A — Architect the System</p>
              <p>Design governance, risk control, and system structure before code.</p>
            </div>

            <div>
              <p className="text-white font-semibold">I — Integrate Intelligence</p>
              <p>Connect models, data, and workflows into a coherent decision engine.</p>
            </div>

            <div>
              <p className="text-white font-semibold">I — Implement Control</p>
              <p>Introduce monitoring, traceability, and operational safeguards.</p>
            </div>

            <div>
              <p className="text-white font-semibold">E — Evaluate Impact</p>
              <p>Measure outcomes against economic and operational objectives.</p>
            </div>

          </div>

          {/* PRINCIPLES */}
          <div className="pt-4 space-y-2 text-gray-400 text-sm">
            <p>• Architecture before code</p>
            <p>• Governance by design</p>
            <p>• Decisions measured by impact</p>
          </div>

          {/* CTA */}
          <div className="pt-8">
            <a
              href={whatsappLink}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Start AI Blueprint Express consultation"
            >
              <Button className="rounded-xl bg-white px-8 py-4 font-bold text-black transition-transform hover:scale-105 active:scale-95">
                Start with AI Blueprint Express
              </Button>
            </a>
          </div>

        </div>
      </div>
    </section>
  );
}