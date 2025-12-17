export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white flex items-center justify-center px-6">
      <section
        className="flex flex-col items-center text-center gap-6 max-w-3xl"
        aria-labelledby="maiie-title"
      >
        {/* TÍTULO PRINCIPAL */}
        <h1
          id="maiie-title"
          className="text-5xl md:text-6xl font-extrabold tracking-tight
                     text-transparent bg-clip-text
                     bg-gradient-to-r from-blue-400 to-purple-600"
        >
          MAIIE SYSTEMS
        </h1>

        {/* SUBTÍTULO / PROPÓSITO */}
        <p className="text-lg md:text-xl text-gray-400">
          Arquitectura & Ingeniería Inteligente
        </p>

        {/* ESTADO DEL SISTEMA */}
        <div
          className="mt-6 px-6 py-3 rounded-full border border-gray-700
                     text-sm md:text-base flex items-center gap-2
                     bg-black/40 backdrop-blur"
        >
          <span className="text-green-400">●</span>
          Sistema Operativo: ONLINE
        </div>

        {/* BLOQUE ESCALABLE FUTURO */}
        {/*
          Aquí crecerá el ecosistema:
          - Cards de Proyectos
          - KPIs
          - Status API
          - Enlaces a GitHub / LinkedIn
        */}
      </section>
    </main>
  );
}