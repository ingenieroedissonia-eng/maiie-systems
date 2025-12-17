import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <nav
      className="fixed top-0 z-50 w-full border-b border-white/10
                 bg-black/50 backdrop-blur-md"
      aria-label="Main Navigation"
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        
        {/* LOGO / BRAND */}
        <Link
          href="/"
          className="flex items-center gap-2 font-bold text-xl tracking-tight hover:opacity-80 transition-opacity"
        >
          <span className="text-blue-500">⚡</span>
          <span className="text-white">MAIIE</span>
          <span className="text-gray-500">SYSTEMS</span>
        </Link>

        {/* LINKS (Desktop) */}
        <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-300">
          <Link href="#projects" className="transition-colors hover:text-white">
            Projects
          </Link>
          <Link href="#services" className="transition-colors hover:text-white">
            Services
          </Link>
          <Link href="#philosophy" className="transition-colors hover:text-white">
            Philosophy
          </Link>
        </div>

        {/* CTA BUTTON */}
        <div className="flex items-center">
          <Button
            variant="outline"
            className="border-blue-500/50 text-blue-400
                       hover:bg-blue-500/10 hover:text-blue-300
                       transition-colors cursor-pointer"
          >
            Client Zone
          </Button>
        </div>

      </div>
    </nav>
  );
}