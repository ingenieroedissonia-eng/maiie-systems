import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Terminal } from "lucide-react";

/**
 * NAVBAR — MAIIE SYSTEMS
 * Global Navigation · Auditable Decision Engineering
 * Architecture-first · Honest navigation
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
            href="#framework"
            className="transition-colors hover:text-white"
          >
            Framework
          </Link>

          <Link
            href="#filosofia"
            className="transition-colors hover:text-white"
          >
            System Core
          </Link>

          <Link
            href="#roadmap"
            className="transition-colors hover:text-white"
          >
            Roadmap
          </Link>

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
