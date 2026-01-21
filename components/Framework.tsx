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
        <div className="max-w-3xl space-y-6">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
            The <span className="text-blue-500">M.A.I.I.E.</span> Framework
          </h2>

          <p className="text-lg text-gray-400 leading-relaxed">
            A decision-first system designed to transform complexity into
            auditable, economically sound outcomes.
          </p>

          <ul className="mt-6 space-y-2 text-gray-400">
            <li>• Architecture before code</li>
            <li>• Governance by design</li>
            <li>• Decisions measured by impact</li>
          </ul>

          {/* SECTION CTA */}
          <div className="pt-6">
            <a href={whatsappLink} target="_blank" rel="noopener noreferrer">
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
