import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import WhatsAppButton from "../components/WhatsAppButton";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://maiie-systems.vercel.app"),

  title: "MAIIE Systems | Auditable AI Decision Architecture",

  description:
    "MAIIE Systems is an architecture-first engineering platform focused on auditable AI decision systems, governance, risk control, and measurable business impact.",

  keywords: [
    "AI architecture",
    "AI decision systems",
    "AI governance",
    "AI engineering",
    "AI architecture consulting",
    "LLM systems architecture",
    "AI decision engineering",
    "MAIIE Systems",
  ],

  openGraph: {
    title: "MAIIE Systems | Auditable AI Decision Architecture",
    description:
      "Architecture-first engineering for auditable AI decision systems, governance, and scalable real-world deployments.",
    url: "https://maiie-systems.vercel.app",
    siteName: "MAIIE Systems",
    type: "website",
  },

  twitter: {
    card: "summary_large_image",
    title: "MAIIE Systems | Auditable AI Decision Architecture",
    description:
      "Architecture-first engineering for auditable AI decision systems and scalable AI governance.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="google" content="notranslate" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <WhatsAppButton />
      </body>
    </html>
  );
}