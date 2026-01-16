import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Terminal, Menu, X } from "lucide-react";

/**
 * NAVBAR — MAIIE SYSTEMS
 * Responsive · Honest · Contractor-grade
 */
export function Navbar() {
  const [open, setOpen] = useState(false);

  const links = [
    { href: "#proyectos", label: "Business Cases" },
    { href: "#metodologia", label: "Architecture" },
    { href: "#framework", label: "Framework" },
    { href: "#filosofia", label: "System Core" },
    { href: "#roadmap", label: "Roadmap" },
  ];

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-white/10 bg-black/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

        {/* BRAND */}
        <Link href="/" className="flex items-center gap-2 text-xl font-bold text-white">
          <Terminal className="h-6 w-6 text-blue-500" />
          MAIIE <span className="text-gray-500">SYSTEMS</span>
        </Link>

        {/* DESKTOP NAV */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-white">
              {l.label}
            </Link>
          ))}
        </div>

        {/* DESKTOP CTA */}
        <div className="hidden md:block">
          <Button
            variant="outline"
            className="border-blue-500/30 font-mono text-xs text-blue-400
                       hover:border-blue-400 hover:bg-blue-500/10 hover:text-blue-300"
          >
            Initiate Protocol
          </Button>
        </div>

        {/* MOBILE TOGGLE */}
        <button
          className="md:hidden text-white"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X /> : <Menu />}
        </button>
      </div>

      {/* MOBILE MENU */}
      {open && (
        <div className="md:hidden border-t border-white/10 bg-black">
          <div className="flex flex-col gap-4 px-6 py-4 text-sm text-gray-300">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className="hover:text-white"
              >
                {l.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
