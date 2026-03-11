import Link from "next/link";

import { Navbar } from "@/components/Navbar";
import { Proyectos } from "@/components/Proyectos";
import { Architecture } from "@/components/Architecture";
import { Framework } from "@/components/Framework";
import { SystemCore } from "@/components/SystemCore";
import { Roadmap } from "@/components/Roadmap";
import { Footer } from "@/components/Footer";

/**
 * HOME — MAIIE SYSTEMS
 * Auditable Decision Engineering
 * Author: Edisson A.G.C.
 */

export default function Home() {
  return (
    <main className="min-h-screen bg-black pt-16 text-white selection:bg-blue-500/30">

      {/* 1. GLOBAL NAVIGATION */}
      <Navbar />

      {/* HERO — STRATEGIC POSITIONING */}
      <section className="relative flex min-h-[calc(100dvh-4rem)] w-full items-center justify-center px-6 pt-12 md:pt-0 text-center overflow-hidden">

        {/* Background */}
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-900/10 via-black to-black" />

        <div className="max-w-4xl space-y-8">

          {/* System identity */}
          <header className="space-y-2">
            <p className="text-sm uppercase tracking-widest text-blue-400">
              M.A.I.I.E. Decision Architecture System · Active
            </p>

            <h1 className="text-4xl sm:text-5xl md:text-7xl font-extrabold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-white to-emerald-400 leading-tight">
              Auditable Decision Engineering
            </h1>
          </header>

          {/* Value proposition */}
          <p className="mx-auto max-w-2xl text-lg sm:text-xl md:text-2xl text-gray-400 leading-relaxed">
            I design AI decision systems that transform operational uncertainty into{" "}
            <span className="text-white font-medium">
              measurable business assets
            </span>{" "}
            through architecture, governance, and multi-agent orchestration.
          </p>

          {/* Authority signal */}
          <p className="text-sm text-gray-500 tracking-wide">
            Executive Technical Assessments · Architecture Reviews · Multi-Phase Stabilization Roadmaps
          </p>

          {/* Authority pillars */}
          <div className="flex flex-wrap justify-center gap-3 pt-4">

            <span className="rounded-full border border-blue-500/30 bg-blue-500/5 px-4 py-1.5 text-xs font-semibold text-blue-400 backdrop-blur-sm">
              🛡️ Multi-Model Governance
            </span>

            <span className="rounded-full border border-emerald-500/30 bg-emerald-500/5 px-4 py-1.5 text-xs font-semibold text-emerald-400 backdrop-blur-sm">
              📈 ROI-Driven Decisions
            </span>

          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">

            <Link
              href="https://wa.me/573212053974"
              className="w-full sm:w-auto rounded-xl bg-white px-8 py-4 font-bold text-black transition-transform hover:scale-105 active:scale-95 text-center"
            >
              Talk to an AI Systems Architect
            </Link>

            <Link
              href="#metodologia"
              className="w-full sm:w-auto rounded-xl border border-gray-800 px-8 py-4 font-bold text-gray-400 transition-colors hover:bg-gray-900 hover:text-white text-center"
            >
              Explore Architecture
            </Link>

          </div>

        </div>
      </section>


      {/* WHY ARCHITECTURE FIRST */}
      <section className="w-full border-t border-gray-900 py-12 text-center">
        <p className="mx-auto max-w-3xl text-sm text-gray-500 tracking-wide">
          Architecture-first AI engineering. Every system is designed for auditability,
          governance, and measurable business impact before a single model is deployed.
        </p>
      </section>


      {/* BUSINESS CASES */}
      <Proyectos />


      {/* TRUSTED ARCHITECTURE PRINCIPLES */}
      <section className="w-full border-t border-gray-900 py-16 text-center">

        <div className="mx-auto max-w-4xl space-y-10">

          <h2 className="text-sm uppercase tracking-widest text-gray-500">
            Trusted Architecture Principles
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-sm text-gray-400">

            <div className="space-y-2">
              <p className="text-white font-semibold">Auditability</p>
              <p>
                Every system decision must be traceable, explainable, and reviewable.
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-white font-semibold">Governance</p>
              <p>
                AI systems require control layers, risk management, and operational clarity.
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-white font-semibold">Business Impact</p>
              <p>
                Architecture must convert uncertainty into measurable operational value.
              </p>
            </div>

          </div>

        </div>

      </section>


      {/* ARCHITECTURE */}
      <Architecture />

      {/* MAIIE FRAMEWORK */}
      <Framework />

      {/* SYSTEM CORE */}
      <SystemCore />

      {/* ROADMAP */}
      <Roadmap />

      {/* FOOTER */}
      <Footer />

    </main>
  );
}