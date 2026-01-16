import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, LineChart, Code2 } from "lucide-react";

/**
 * STRATEGIC CAPABILITIES — MAIIE SYSTEMS
 * What we are able to design, build, and operate.
 * Capabilities, not generic services.
 */
export function Services() {
  const capabilities = [
    {
      title: "AI Engineering & Intelligent Agents",
      description:
        "Design and implementation of autonomous agents, Retrieval-Augmented Generation (RAG) systems, and custom LLM-based solutions. Focused on traceability, governance, and real business decision support.",
      icon: <Brain className="mb-4 h-10 w-10 text-blue-500" />,
    },
    {
      title: "Commercial Intelligence & Decision Automation",
      description:
        "Architecture of financial and commercial intelligence systems (e.g., SmartROI) that transform raw operational data into deterministic, auditable decision outputs.",
      icon: <LineChart className="mb-4 h-10 w-10 text-purple-500" />,
    },
    {
      title: "Scalable System Architecture",
      description:
        "Design of robust, secure, and scalable full-stack systems using the Next.js ecosystem. Emphasis on performance, long-term maintainability, and production-grade reliability.",
      icon: <Code2 className="mb-4 h-10 w-10 text-green-500" />,
    },
  ];

  return (
    <section
      id="services"
      className="w-full border-t border-white/5 bg-zinc-950 py-24"
    >
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="mb-16 text-center text-3xl font-bold tracking-tight text-white">
          Strategic Capabilities <span className="text-purple-500">_</span>
        </h2>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {capabilities.map((capability) => (
            <Card
              key={capability.title}
              className="group border-zinc-800 bg-black/50 text-white transition-all duration-300 hover:-translate-y-1 hover:border-purple-500/40 hover:bg-zinc-900/80"
            >
              <CardHeader>
                {capability.icon}
                <CardTitle className="text-xl font-bold">
                  {capability.title}
                </CardTitle>
              </CardHeader>

              <CardContent>
                <p className="leading-relaxed text-gray-400">
                  {capability.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
