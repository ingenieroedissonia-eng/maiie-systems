import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  Github,
  ExternalLink,
  TrendingUp,
  ShieldCheck,
  Cpu,
} from "lucide-react";

export function Proyectos() {
  /**
   * BUSINESS ASSET MATRIX
   * Structure: Business Problem → Architectural Solution → Measurable Outcome
   */
  const projects = [
    {
      title: "SmartROI v2.0",
      category: "Fintech Decision Engine",
      description:
        "Transforms manual financial analysis (≈45 minutes per iteration) into deterministic projections in under 0.5 seconds. A decision engine that eliminates human error in ROI, compound interest, and import viability calculations.",
      tags: ["Vectorized Python", "Streamlit Cloud", "Financial Logic"],
      status: "Production",
      demoUrl:
        "https://smartroi-project-zvdkq2ndmah7mpd9nbgqol.streamlit.app/",
      repoUrl: "https://github.com/ingenieroedissonia-eng/SmartROI-Project",
      icon: <TrendingUp className="h-5 w-5 text-emerald-400" />,
    },
    {
      title: "EdiMentor AI",
      category: "Enterprise RAG Audit System",
      description:
        "Technical decision-auditing system designed to mitigate technical debt through multi-agent orchestration. Integrates specialized roles (Architect, Auditor, Engineer) to reduce code review cycles by ~40% with full traceability.",
      tags: ["Vertex AI", "RAG Architecture", "Multi-Agent Systems"],
      status: "Deployed",
      demoUrl: "https://edimentor-ai-official.vercel.app",
      repoUrl: "https://github.com/ingenieroedissonia-eng/edimentor-ai-official",
      icon: <ShieldCheck className="h-5 w-5 text-blue-400" />,
    },
    {
      title: "MAIIE Systems Core",
      category: "Operational Architecture Backbone",
      description:
        "Central engineering platform designed for scalability and authority. Implements edge-first optimization and hybrid rendering to guarantee sub-100ms load times, serving as the conversion and credibility hub of the ecosystem.",
      tags: ["Next.js 15", "React 19 RC", "Tailwind CSS v4"],
      status: "Online",
      demoUrl: "#",
      repoUrl: "https://github.com/ingenieroedissonia-eng/maiie-systems",
      icon: <Cpu className="h-5 w-5 text-purple-400" />,
    },
  ];

  return (
    <section
      id="proyectos"
      className="w-full bg-black py-24 text-white selection:bg-emerald-500/30"
    >
      <div className="mx-auto max-w-7xl px-6">
        {/* SECTION HEADER */}
        <div className="mb-16 text-center space-y-4">
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight">
            Portfolio of{" "}
            <span className="text-blue-500">Business Cases</span>
          </h2>

          <p className="mx-auto max-w-2xl text-lg text-gray-400">
            Evidence of structured engineering decisions applied to real-world
            problems of latency, scalability, and operational risk.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {projects.map((project) => (
            <Card
              key={project.title}
              className="group flex flex-col justify-between border-white/10 bg-zinc-900/50 transition-all duration-300 hover:border-blue-500/50 hover:bg-zinc-900/80 hover:shadow-2xl hover:shadow-blue-900/10"
            >
              <CardHeader className="space-y-4">
                <div className="flex items-start justify-between">
                  <Badge
                    variant="outline"
                    className={`w-fit border-opacity-30 px-3 py-1 ${
                      ["Production", "Online", "Deployed"].includes(
                        project.status
                      )
                        ? "border-emerald-500 bg-emerald-500/10 text-emerald-400"
                        : "border-yellow-500 text-yellow-400"
                    }`}
                  >
                    <span className="mr-2 h-1.5 w-1.5 rounded-full bg-current animate-pulse" />
                    {project.status}
                  </Badge>
                  {project.icon}
                </div>

                <div className="space-y-1">
                  <p className="font-mono text-xs uppercase tracking-wider text-blue-400">
                    {project.category}
                  </p>

                  <CardTitle className="text-2xl font-bold text-white transition-colors group-hover:text-blue-400">
                    {project.title}
                  </CardTitle>
                </div>
              </CardHeader>

              <CardContent>
                <p className="mb-6 text-sm leading-relaxed text-gray-400">
                  {project.description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag) => (
                    <Badge
                      key={tag}
                      className="border border-zinc-700 bg-zinc-800 text-gray-300 transition-colors hover:bg-zinc-700 hover:text-white"
                    >
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>

              <CardFooter className="flex gap-3 border-t border-white/5 pt-4">
                <Button
                  asChild
                  className="flex-1 bg-white font-bold text-black transition-all hover:bg-gray-200"
                >
                  <Link
                    href={project.demoUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    View Demo / ROI
                  </Link>
                </Button>

                <Button
                  asChild
                  variant="outline"
                  className="border-zinc-700 bg-transparent text-gray-400 transition-all hover:border-white hover:bg-zinc-800 hover:text-white"
                >
                  <Link
                    href={project.repoUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Github className="h-5 w-5" />
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
