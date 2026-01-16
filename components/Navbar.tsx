import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Terminal } from "lucide-react";

/**
 * NAVBAR — MAIIE SYSTEMS
 * Global Navigation · Auditable Decision Engineering
 * Architecture-first · Content later
 */
export function Navbar() {
  return (
    <nav
      className="fixed top-0 z-50 w-full border-b border-white/10
                 bg-black/80 backdrop-blur-md supports-[backdrop-filter]:bg-black/50"
      aria-label="Main Navigation"
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

        {/* BRAND / SYSTEM IDENTITY */}
        <Link
          href="/"
          className="flex items-center gap-2 text-xl font-bold tracking-tight
                     transition-opacity hover:opacity-80"
        >
          <Terminal className="h-6 w-6 text-blue-500" />
          <span className="text-white">MAIIE</span>
          <span className="text-gray-500">SYSTEMS</span>
        </Link>

        {/* NAVIGATION LINKS (DESKTOP) */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">

          {/* CURRENT / ACTIVE SECTIONS */}
          <Link
            href="#proyectos"
            className="transition-colors hover:text-white"
          >
            Business Cases
          </Link>

          <Link
            href="#metodologia"
            className="transition-colors hover:text-white"
          >
            Architecture
          </Link>

          <Link
            href="#filosofia"
            className="transition-colors hover:text-white"
          >
            System Core
          </Link>

          {/* FUTURE STRUCTURE — DECLARED, NOT IMPLEMENTED */}
          <div className="relative group cursor-default">
            <span className="transition-colors hover:text-white">
              MAIIE Framework
            </span>

            <div
              className="invisible absolute left-0 top-6 min-w-[220px]
                         rounded-md border border-white/10 bg-black/90
                         p-2 text-xs text-gray-400 opacity-0
                         backdrop-blur-md transition-all
                         group-hover:visible group-hover:opacity-100"
            >
              <div className="px-2 py-1">System Modules</div>
              <div className="px-2 py-1">Decision Layers</div>
              <div className="px-2 py-1">Governance</div>
              <div className="px-2 py-1 text-gray-500 italic">
                (Structure declared)
              </div>
            </div>
          </div>

          <div className="relative group cursor-default">
            <span className="transition-colors hover:text-white">
              Roadmap
            </span>

            <div
              className="invisible absolute left-0 top-6 min-w-[200px]
                         rounded-md border border-white/10 bg-black/90
                         p-2 text-xs text-gray-400 opacity-0
                         backdrop-blur-md transition-all
                         group-hover:visible group-hover:opacity-100"
            >
              <div className="px-2 py-1">v1 · Foundation</div>
              <div className="px-2 py-1">v2 · Expansion</div>
              <div className="px-2 py-1">v3 · Scale</div>
              <div className="px-2 py-1 text-gray-500 italic">
                (Coming later)
              </div>
            </div>
          </div>

        </div>

        {/* PRIMARY CTA */}
        <div className="flex items-center">
          <Button
            variant="outline"
            className="border-blue-500/30 font-mono text-xs text-blue-400
                       transition-all hover:border-blue-400 hover:bg-blue-500/10
                       hover:text-blue-300"
          >
            Initiate Protocol
          </Button>
        </div>

      </div>
    </nav>
  );
}
