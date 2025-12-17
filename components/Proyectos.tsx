import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Github, ExternalLink } from "lucide-react";

export function Proyectos() {
  const projects = [
    {
      title: "SmartROI v2.0",
      description:
        "Advanced financial calculator for imports. Automates profitability analysis and commercial decision-making logic.",
      tags: ["Python", "Streamlit", "Finance"],
      status: "Deployed",
      // TUS ENLACES REALES AQUÍ
      demoUrl: "https://smartroi-project-zvdkq2ndmah7mpd9nbgqol.streamlit.app/",
      repoUrl: "https://github.com/ingenieroedissonia-eng/SmartROI-Project",
    },
    {
      title: "EdiMentor AI",
      description:
        "Multi-agent chatbot for technical mentorship. Integrates specialized roles (Architect, Engineer, Auditor) in a unified ecosystem.",
      tags: ["GenAI", "LLMs", "Multi-Agent"],
      status: "In Development",
      demoUrl: "#",
      repoUrl: "https://github.com/ingenieroedissonia-eng",
    },
    {
      title: "MAIIE Systems Core",
      description:
        "Central engineering platform and professional portfolio. Scalable modern architecture built with Next.js 15.",
      tags: ["Next.js 15", "React 19", "Tailwind v4"],
      status: "Online",
      demoUrl: "#",
      repoUrl: "#",
    },
  ];

  return (
    <section id="proyectos" className="w-full bg-black py-24 text-white">
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="mb-16 text-center text-3xl font-bold tracking-tight">
          Technological Arsenal <span className="text-blue-500">_</span>
        </h2>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {projects.map((project) => (
            <Card
              key={project.title}
              className="group flex flex-col justify-between border-white/10 bg-zinc-900/50 transition-all hover:border-blue-500/50 hover:bg-zinc-900/80"
            >
              <CardHeader>
                <div className="mb-4 flex justify-between">
                  <Badge
                    variant="outline"
                    className={`w-fit border-blue-500/30 text-blue-400 ${
                      project.status === "In Development"
                        ? "border-yellow-500/30 text-yellow-400"
                        : ""
                    }`}
                  >
                    {project.status}
                  </Badge>
                </div>
                <CardTitle className="text-xl font-bold text-white">
                  {project.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="mb-6 text-gray-400">{project.description}</p>
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag) => (
                    <Badge
                      key={tag}
                      className="bg-zinc-800 text-gray-300 hover:bg-zinc-700"
                    >
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="flex gap-3 pt-2">
                
                {/* BOTÓN 1: LIVE DEMO (Prioridad Alta) */}
                <Button 
                  asChild 
                  className="flex-1 bg-white text-black hover:bg-gray-200 transition-colors font-semibold"
                >
                  <Link href={project.demoUrl} target="_blank">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Live Demo
                  </Link>
                </Button>

                {/* BOTÓN 2: CÓDIGO (Secundario) */}
                <Button 
                  asChild 
                  variant="outline"
                  className="bg-transparent border-zinc-700 text-gray-300 hover:bg-zinc-800 hover:text-white"
                >
                  <Link href={project.repoUrl} target="_blank">
                    <Github className="h-4 w-4" />
                  </Link>
                </Button>

              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}