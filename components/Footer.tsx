import Link from "next/link";
import { Github, Linkedin, Mail } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-black py-12">
      <div className="mx-auto flex max-w-7xl flex-col gap-10 px-6 md:flex-row md:justify-between">

        {/* BRAND & IDENTITY */}
        <div className="flex flex-col gap-2 text-center md:text-left">
          <h3 className="text-xl font-bold tracking-tight text-white">
            MAIIE <span className="text-blue-500">SYSTEMS</span>
          </h3>

          <p className="text-sm text-gray-400">
            Architectural & Intelligent Engineering Applied to Commerce.
          </p>

          <p className="mt-4 text-xs text-gray-500">
            © 2025 Edisson A.G.C. All rights reserved.
          </p>
        </div>

        {/* SOCIAL & SIGNATURE */}
        <div className="flex flex-col items-center gap-6 md:items-end">

          {/* SOCIAL ICONS */}
          <div className="flex gap-4">
            <Link
              href="https://github.com/ingenieroedissonia-eng"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 transition-colors hover:text-white"
            >
              <Github className="h-5 w-5" />
              <span className="sr-only">GitHub</span>
            </Link>

            <span className="text-gray-500 cursor-not-allowed">
              <Linkedin className="h-5 w-5" />
              <span className="sr-only">LinkedIn (coming soon)</span>
            </span>

            <Link
              href="mailto:contacto@maiie.com"
              className="text-gray-400 transition-colors hover:text-green-400"
            >
              <Mail className="h-5 w-5" />
              <span className="sr-only">Email</span>
            </Link>
          </div>

          {/* SIGNATURE & VERSE */}
          <div className="text-center text-xs font-medium leading-relaxed text-gray-500 md:text-right">
            <p>Developed | by Edisson A.G.C.</p>
            <p>AI Engineering Applied to Commerce |</p>
            <p>Elite Pro Winner Team |</p>
            <p>Eternal and Loyal |</p>

            <div className="mt-4 italic text-gray-400">
              <p>“Commit your works to the LORD,</p>
              <p>and your thoughts will be established.”</p>
              <p className="mt-1 font-bold not-italic text-blue-500">
                — Proverbs 16:3
              </p>
            </div>
          </div>

        </div>
      </div>
    </footer>
  );
}
