import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { FlaskConical, Network, Microscope, Activity, Beaker, Github, Linkedin, Globe } from "lucide-react";
import Link from "next/link";
import { cn } from "@/components/ui/PremiumCard";
import { StatusLamp } from "@/components/ui/StatusLamp";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "Y2H-AI | Molecular Observatory",
  description: "AI-assisted exploration of yeast protein–protein interaction hypotheses.",
};

function TopNav() {
  return (
    <nav className="h-16 border-b border-white/5 bg-[#0b0f19]/80 backdrop-blur-md sticky top-0 z-50 flex items-center justify-between px-6">
      <div className="flex items-center space-x-8">
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-8 h-8 rounded-md bg-sci-cyan/10 border border-sci-cyan/30 flex items-center justify-center group-hover:bg-sci-cyan/20 transition-colors">
            <Microscope className="w-5 h-5 text-sci-cyan" />
          </div>
          <span className="font-bold tracking-widest uppercase text-white/90">Y2H-AI</span>
        </Link>
        <div className="h-6 w-px bg-white/10" />
        <div className="flex space-x-6 text-sm font-medium tracking-wide uppercase text-white/60">
          <Link href="/laboratory" className="hover:text-white transition-colors flex items-center">
            <Beaker className="w-4 h-4 mr-2" /> Laboratory
          </Link>
          <Link href="/protein" className="hover:text-white transition-colors flex items-center">
            <FlaskConical className="w-4 h-4 mr-2" /> Observatory
          </Link>
          <Link href="/network" className="hover:text-white transition-colors flex items-center">
            <Network className="w-4 h-4 mr-2" /> Network
          </Link>
          <Link href="/model" className="hover:text-white transition-colors flex items-center">
            <Activity className="w-4 h-4 mr-2" /> Models
          </Link>
        </div>
      </div>
      
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-3 text-xs tracking-widest text-white/40 uppercase">
          <span>Workspace: S. cerevisiae</span>
        </div>
        <StatusLamp status="green" label="System Ready" size="sm" />
      </div>
    </nav>
  );
}

import { SplashScreen } from "@/components/ui/SplashScreen";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={cn(
          inter.variable,
          jetbrainsMono.variable,
          "antialiased min-h-screen flex flex-col"
        )}
      >
        <SplashScreen />
        <TopNav />
        <main className="flex-1 flex flex-col relative z-0">
          {children}
        </main>
        
        <footer className="h-10 border-t border-white/5 bg-[#0b0f19] flex items-center justify-between px-6 text-[10px] tracking-widest uppercase text-white/40 z-50">
          <div className="flex space-x-8">
            <span>DATA: BioGRID</span>
            <span>MODEL: Random Forest V3</span>
          </div>
          
          <div className="flex items-center space-x-4 bg-sci-cyan/5 px-4 py-1.5 rounded-full border border-sci-cyan/10">
            <span className="text-white/60">Engineered by <strong className="text-sci-cyan">Balaji Muthukumar</strong></span>
            <div className="w-px h-3 bg-white/10" />
            <div className="flex items-center space-x-3">
              <a href="https://github.com/balajiprincejoshva-byte" target="_blank" rel="noopener noreferrer" className="hover:text-sci-cyan transition-colors">
                <Github className="w-3.5 h-3.5" />
              </a>
              <a href="https://in.linkedin.com/in/balaji-muthukumar-6445a5383" target="_blank" rel="noopener noreferrer" className="hover:text-sci-cyan transition-colors">
                <Linkedin className="w-3.5 h-3.5" />
              </a>
              <a href="https://my-portfolio-one-plum-69.vercel.app" target="_blank" rel="noopener noreferrer" className="hover:text-sci-cyan transition-colors">
                <Globe className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <div className="flex space-x-8">
            <span className="text-sci-amber/70">STATUS: RESEARCH / HYPOTHESIS</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
