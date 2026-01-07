import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Database, BrainCircuit, ShieldAlert, Zap } from "lucide-react";

export function Architecture() {
  const steps = [
    {
      icon: <Database className="h-8 w-8 text-blue-400" />,
      title: "1. Data Ingestion",
      desc: "Raw data extraction from unstructured sources such as PDFs, spreadsheets, and APIs. Normalization pipelines designed for Fintech and Logistics environments.",
    },
    {
      icon: <BrainCircuit className="h-8 w-8 text-purple-400" />,
      title: "2. Neural Processing",
      desc: "Retrieval-Augmented Generation (RAG) architecture. Context grounding through Vector Databases to ensure responses are anchored in organizational knowledge.",
    },
    {
      icon: <ShieldAlert className="h-8 w-8 text-emerald-400" />,
      title: "3. Governance Layer",
      desc: "Dedicated audit layer that validates logical consistency, mathematical accuracy, and compliance before any result is released.",
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-400" />,
      title: "4. Actionable Output",
      desc: "Deterministic outputs delivered as structured reports or JSON artifacts. Zero tolerance for hallucinations in critical business decisions.",
    },
  ];

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
            How raw information is transformed into auditable business assets.
          </p>
        </div>

        <div className="relative grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div className="absolute left-0 top-12 hidden h-0.5 w-full bg-gradient-to-r from-blue-500/0 via-blue-500/20 to-blue-500/0 lg:block -z-10" />

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
      </div>
    </section>
  );
}
