import { ShieldCheck, Workflow, Scale } from "lucide-react";

export function SystemCore() {
  const principles = [
    {
      icon: <Workflow className="h-6 w-6 text-blue-400" />,
      title: "Architecture > Code",
      desc: "Priorizing structural integrity and systemic design over raw development. Code is a commodity; architecture is an asset.",
    },
    {
      icon: <Scale className="h-6 w-6 text-emerald-400" />,
      title: "Human-in-the-loop",
      desc: "AI as an accelerator, not a black box. Our systems ensure human oversight in critical commercial decision points.",
    },
    {
      icon: <ShieldCheck className="h-6 w-6 text-purple-400" />,
      title: "Auditability First",
      desc: "Every automated outcome must be traceable and justifiable. We solve for trust and operational governance.",
    },
  ];

  return (
    <section id="filosofia" className="w-full bg-black py-24 text-white border-t border-white/5">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col lg:flex-row gap-16 items-center">
          
          {/* NARRATIVA DE FILOSOFÍA */}
          <div className="lg:w-1/2 space-y-6">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
              The <span className="text-blue-500">M.A.I.I.E.</span> Philosophy
            </h2>
            <p className="text-gray-400 text-lg leading-relaxed">
              Beyond simple AI tools, we build <strong>Decision Ecosystems</strong>. Our methodology is rooted in the belief that intelligence without governance is a liability. 
            </p>
            <div className="h-1 w-20 bg-blue-600 rounded-full" />
          </div>

          {/* TARJETAS DE PRINCIPIOS */}
          <div className="lg:w-1/2 grid gap-4">
            {principles.map((p, i) => (
              <div key={i} className="group p-6 rounded-2xl bg-zinc-900/30 border border-white/5 hover:border-blue-500/20 transition-all">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-lg bg-zinc-800/50 group-hover:bg-blue-500/10 transition-colors">
                    {p.icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-white mb-1">{p.title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{p.desc}</p>
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