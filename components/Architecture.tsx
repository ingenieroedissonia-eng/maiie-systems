import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Database, BrainCircuit, ShieldAlert, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * ARCHITECTURE — MAIIE SYSTEMS
 * End-to-end decision architecture
 * Data → Intelligence → Governance → Action
 */
export function Architecture() {
  const steps = [
    {
      icon: <Database className="h-8 w-8 text-blue-400" />,
      title: "1. Data Ingestion",
      desc: "Structured and unstructured data ingestion from sources such as PDFs, spreadsheets, and APIs. Normalization pipelines designed for high-variance commercial environments (e.g., Fintech, Logistics).",
    },
    {
      icon: <BrainCircuit className="h-8 w-8 text-purple-400" />,
      title: "2. Neural Processing",
      desc: "Retrieval-Augmented Generation (RAG) architecture with vector-based context grounding. Ensures every inference is anchored in validated organizational knowledge.",
    },
    {
      icon: <ShieldAlert className="h-8 w-8 text-emerald-400" />,
      title: "3. Governance Layer",
      desc: "Dedicated validation layer enforcing logical consistency, mathematical correctness, and policy compliance before any output is approved.",
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-400" />,
      title: "4. Actionable Output",
      desc: "Deterministic, auditable outputs delivered as structured reports or machine-consumable artifacts (JSON). Zero tolerance for hallucinations in critical business decisions.",
    },
  ];

  // WhatsApp CTA — AI Blueprint Express
  const whatsappLink =
    "https://wa.me/573212053974?text=Hello%2C%20I%E2%80%99ve%20reviewed%20the%20M.A.I.I.E.%20architecture%20and%20I%E2%80%99d%20like%20to%20apply%20it%20to%20my%20business%20through%20the%20AI%20Blueprint%20Express.";

  return (
    <section
      id="metodologia"
      className="w-full border-t border-white/5 bg-zinc-950 py-24 text-white"
    >
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-16 text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
            The <span className="text-blue-500">M.A.I.I.E.</span> Architecture
          </h2>
          <p className="mt-4 text-lg text-gray-400">
            How raw information is transformed into auditable decision-ready business assets.
          </p>
        </div>

        <div className="relative grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div className="absolute left-0 top-12 -z-10 hidden h-0.5 w-full bg-gradient-to-r from-blue-500/0 via-blue-500/20 to-blue-500/0 lg:block" />

          {steps.map((step, index) => (
            <Card
              key={index}
              className="border-white/10 bg-zinc-900/50 transition-all hover:-translate-y-2 hover:border-blue-500/30"
            >
              <CardHeader>
                <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl border border-white/5 bg-zinc-800/50 shadow-inner">
                  {step.icon}
                </div>
                <CardTitle className="text-xl font-bold text-white">
                  {step.title}
                </CardTitle>
              </CardHeader>

              <CardContent>
                <p className="text-sm leading-relaxed text-gray-400">
                  {step.desc}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* SECTION CTA */}
        <div className="mt-20 text-center">
          <p className="mb-6 text-lg text-gray-400">
            This architecture is delivered through a structured engagement.
          </p>
          <a href={whatsappLink} target="_blank" rel="noopener noreferrer">
            <Button className="rounded-xl bg-white px-8 py-4 font-bold text-black transition-transform hover:scale-105 active:scale-95">
              Apply via AI Blueprint Express
            </Button>
          </a>
        </div>
      </div>
    </section>
  );
}
