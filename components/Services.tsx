import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, LineChart, Code2 } from "lucide-react";

export function Services() {
  const services = [
    {
      title: "AI Engineering & Intelligent Agents",
      description:
        "Design and deployment of autonomous agents, RAG systems (Retrieval-Augmented Generation), and custom LLM solutions using Vertex AI and OpenAI to solve real business problems.",
      icon: <Brain className="mb-4 h-10 w-10 text-blue-500" />,
    },
    {
      title: "Commercial Intelligence & Automation",
      description:
        "Advanced data analysis and financial automation (SmartROI), transforming raw commercial data into actionable insights for strategic decision-making.",
      icon: <LineChart className="mb-4 h-10 w-10 text-purple-500" />,
    },
    {
      title: "Scalable Full-Stack Architecture",
      description:
        "Robust and secure web application development using the Next.js ecosystem (React, Tailwind, TypeScript), focused on performance, scalability, and long-term maintainability.",
      icon: <Code2 className="mb-4 h-10 w-10 text-green-500" />,
    },
  ];

  return (
    <section
      id="services"
      className="w-full border-t border-white/5 bg-zinc-950 py-24"
    >
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="mb-16 text-center text-3xl font-bold tracking-tight text-white">
          Strategic Capabilities <span className="text-purple-500">_</span>
        </h2>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {services.map((service) => (
            <Card
              key={service.title}
              className="group bg-black/50 border-zinc-800 text-white transition-all duration-300 hover:-translate-y-1 hover:border-purple-500/40 hover:bg-zinc-900/80"
            >
              <CardHeader>
                {service.icon}
                <CardTitle className="text-xl font-bold">
                  {service.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="leading-relaxed text-gray-400">
                  {service.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}