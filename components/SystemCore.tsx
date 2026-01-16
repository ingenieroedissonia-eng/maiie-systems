import { ShieldCheck, Workflow, Scale } from "lucide-react";

/**
 * SYSTEM CORE — MAIIE SYSTEMS
 * Philosophical & Architectural Principles
 * Architecture-first · Governance-driven · Human-centered
 */
export function SystemCore() {
  const principles = [
    {
      icon: <Workflow className="h-6 w-6 text-blue-400" />,
      title: "Architecture > Code",
      desc: "We prioritize structural integrity and systemic design over raw development. Code is a commodity; architecture is a long-term asset.",
    },
    {
      icon: <Scale className="h-6 w-6 text-emerald-400" />,
      title: "Human-in-the-loop",
      desc: "AI is an accelerator, not a black box. Every critical commercial decision preserves human oversight and accountability.",
    },
    {
      icon: <ShieldCheck className="h-6 w-6 text-purple-400" />,
      title: "Auditability First",
      desc: "Every automated outcome must be traceable, explainable, and justifiable. We design systems that optimize for trust and operational governance.",
    },
  ];

  return (
    <section
      id="filosofia"
      className="w-full border-t border-white/5 bg-black py-24 text-white"
    >
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col items-center gap-16 lg:flex-row">

          {/* PHILOSOPHY NARRATIVE */}
          <div className="space-y-6 lg:w-1/2">
            <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
              The <span className="text-blue-500">M.A.I.I.E.</span> Philosophy
            </h2>

            <p className="text-lg leading-relaxed text-gray-400">
              Beyond isolated AI tools, we design <strong>Decision Ecosystems</strong>.
              Our methodology assumes that intelligence without governance is not innovation,
              but operational risk.
            </p>

            <div className="h-1 w-20 rounded-full bg-blue-600" />
          </div>

          {/* PRINCIPLES CARDS */}
          <div className="grid gap-4 lg:w-1/2">
            {principles.map((principle, index) => (
              <div
                key={index}
                className="group rounded-2xl border border-white/5 bg-zinc-900/30 p-6 transition-all hover:border-blue-500/20"
              >
                <div className="flex items-start gap-4">
                  <div className="rounded-lg bg-zinc-800/50 p-3 transition-colors group-hover:bg-blue-500/10">
                    {principle.icon}
                  </div>

                  <div>
                    <h3 className="mb-1 font-bold text-white">
                      {principle.title}
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-500">
                      {principle.desc}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>
    </section>
  );
}
