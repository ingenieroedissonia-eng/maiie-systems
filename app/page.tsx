import { Proyectos } from "@/components/Proyectos";

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white">
      {/* HERO SECTION */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
        <h1 className="mb-6 text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
          MAIIE SYSTEMS
        </h1>

        <p className="mb-10 max-w-2xl text-xl text-gray-400">
          Intelligent Architecture & Engineering Applied to Commerce
        </p>

        <div className="flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-6 py-2 text-sm font-medium text-green-400">
          <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
          System Status: ONLINE
        </div>
      </section>

      {/* PROJECTS SECTION */}
      <Proyectos />
    </main>
  );
}