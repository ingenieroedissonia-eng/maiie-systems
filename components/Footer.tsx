import Link from "next/link";
import { Github, Linkedin, Mail } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-black py-12">
      <div className="mx-auto flex max-w-7xl flex-col gap-10 px-6 md:flex-row md:justify-between">
        
        {/* COLUMNA 1: MARCA (En Inglés) */}
        <div className="flex flex-col gap-2 text-center md:text-left">
          <h3 className="text-xl font-bold tracking-tight text-white">
            MAIIE <span className="text-blue-500">SYSTEMS</span>
          </h3>
          <p className="text-sm text-gray-400">
            Intelligent Architecture & Engineering Applied to Commerce.
          </p>
          <p className="text-xs text-gray-500 mt-4">
            © 2025 Edisson A.G.C. All rights reserved.
          </p>
        </div>

        {/* COLUMNA 2: REDES + SELLO VERTICAL */}
        <div className="flex flex-col items-center gap-6 md:items-end">
          
          {/* ICONOS */}
          <div className="flex gap-4">
            <Link
              href="https://github.com/ingenieroedissonia-eng"
              target="_blank"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <Github className="h-5 w-5" />
              <span className="sr-only">GitHub</span>
            </Link>
            <Link
              href="#"
              className="text-gray-400 hover:text-blue-400 transition-colors"
            >
              <Linkedin className="h-5 w-5" />
              <span className="sr-only">LinkedIn</span>
            </Link>
            <Link
              href="mailto:contacto@maiie.com"
              className="text-gray-400 hover:text-green-400 transition-colors"
            >
              <Mail className="h-5 w-5" />
              <span className="sr-only">Email</span>
            </Link>
          </div>

          {/* TU SELLO + VERSÍCULO (Alineación Vertical Estricta) */}
          <div className="text-center text-xs font-medium leading-relaxed text-gray-500 md:text-right">
            <p>Developed | by Edisson A.G.C.</p>
            <p>AI Engineering Applied to Commerce |</p>
            <p>Elite Pro Winner Team |</p>
            <p>Eternal and Loyal |</p>

            <div className="mt-4 italic text-gray-400">
              <p>“Commit your works to the LORD,</p>
              <p>and your thoughts will be established.”</p>
              <p className="font-bold not-italic text-blue-500 mt-1">
                — Proverbs 16:3
              </p>
            </div>
          </div>

        </div>
      </div>
    </footer>
  );
}