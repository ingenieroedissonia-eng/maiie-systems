import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Proyectos() {
  const projects = [
    {
      title: "SmartROI v2.0",
      description:
        "Advanced financial calculator for imports. Automates profitability analysis and commercial decision-making logic.",
      tags: ["Python", "Streamlit", "Finance"],
      status: "Deployed",
    },
    {
      title: "EdiMentor AI",
      description:
        "Multi-agent chatbot for technical mentorship. Integrates specialized roles (Architect, Engineer, Auditor) in a unified ecosystem.",
      tags: ["GenAI", "LLMs", "Multi-Agent"],
      status: "In Development",
    },
    {
      title: "MAIIE Systems Core",
      description:
        "Central engineering platform and professional portfolio. Scalable modern architecture built with Next.js 15.",
      tags: ["Next.js 15", "React 19", "Tailwind v4"],
      status: "Online",
    },
  ];

  return (
    <section
      id="projects"
      className="w-full bg-black py-24 border-t border-white/10"
      aria-labelledby="proyectos-title"
    >
      <div className="mx-auto max-w-7xl px-6">
        <h2
          id="proyectos-title"
          className="mb-12 text-center text-3xl font-bold tracking-tight text-white"
        >
          Technological Arsenal <span className="text-blue-500">_</span>
        </h2>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {projects.map((project) => (
            <Card
              key={project.title}
              className="group bg-zinc-900/50 border-zinc-800 text-white
                         transition-all duration-300
                         hover:border-blue-500/50
                         hover:shadow-lg hover:shadow-blue-500/10"
            >
              <CardHeader>
                <div className="mb-4 flex justify-between items-start">
                  <Badge
                    variant="outline"
                    className="border-blue-400/30 text-blue-400"
                  >
                    {project.status}
                  </Badge>
                </div>

                <CardTitle className="text-xl font-bold">
                  {project.title}
                </CardTitle>

                <CardDescription className="mt-2 text-gray-400">
                  {project.description}
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded border border-zinc-700 bg-zinc-800
                                 px-2 py-1 text-xs text-gray-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </CardContent>

              <CardFooter>
                <Button
                  className="w-full bg-white text-black font-bold
                             hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  View Details
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}