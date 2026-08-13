import { PremiumCard } from "@/components/ui/PremiumCard";
import { Beaker, FlaskConical, Network, Activity, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="relative flex-1 flex flex-col items-center justify-center min-h-[calc(100vh-6rem)]">
      
      {/* Decorative Abstract Molecular Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-sci-cyan rounded-full mix-blend-screen filter blur-[128px] animate-pulse" />
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-sci-amber rounded-full mix-blend-screen filter blur-[128px] opacity-60" />
      </div>

      <div className="z-10 text-center max-w-4xl mx-auto px-6 mb-16">
        <h1 className="text-6xl font-light tracking-widest text-white mb-6 uppercase flex flex-col">
          <span className="font-bold text-sci-cyan mb-2">Y2H-AI</span>
          Molecular Observatory
        </h1>
        <p className="text-xl text-white/60 tracking-wide font-light max-w-2xl mx-auto">
          AI-assisted exploration of yeast protein–protein interaction hypotheses.
        </p>
      </div>

      <div className="z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto px-6">
        <Link href="/laboratory" className="group">
          <PremiumCard className="h-full flex flex-col group-hover:-translate-y-1 transition-transform duration-300">
            <div className="w-12 h-12 rounded-lg bg-sci-cyan/10 border border-sci-cyan/30 flex items-center justify-center mb-6">
              <Beaker className="w-6 h-6 text-sci-cyan" />
            </div>
            <h2 className="text-lg font-semibold tracking-wide uppercase text-white mb-2">
              Interaction Laboratory
            </h2>
            <p className="text-sm text-white/50 mb-6 flex-1">
              Analyze a protein pair. View prediction hypotheses and 3D molecular representations.
            </p>
            <div className="flex items-center text-sci-cyan text-sm font-semibold tracking-wide">
              ENTER LAB <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </div>
          </PremiumCard>
        </Link>

        <Link href="/protein" className="group">
          <PremiumCard className="h-full flex flex-col group-hover:-translate-y-1 transition-transform duration-300">
            <div className="w-12 h-12 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:bg-white/10 transition-colors">
              <FlaskConical className="w-6 h-6 text-white/80" />
            </div>
            <h2 className="text-lg font-semibold tracking-wide uppercase text-white mb-2">
              Protein Observatory
            </h2>
            <p className="text-sm text-white/50 mb-6 flex-1">
              Explore a single protein in depth. Review known networks, sequences, and structural metadata.
            </p>
            <div className="flex items-center text-white/70 text-sm font-semibold tracking-wide">
              EXPLORE PROTEIN <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </div>
          </PremiumCard>
        </Link>

        <Link href="/network" className="group">
          <PremiumCard className="h-full flex flex-col group-hover:-translate-y-1 transition-transform duration-300">
            <div className="w-12 h-12 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:bg-white/10 transition-colors">
              <Network className="w-6 h-6 text-white/80" />
            </div>
            <h2 className="text-lg font-semibold tracking-wide uppercase text-white mb-2">
              Interaction Network
            </h2>
            <p className="text-sm text-white/50 mb-6 flex-1">
              Explore 3D interaction neighborhoods and discover predicted candidate edges visually.
            </p>
            <div className="flex items-center text-white/70 text-sm font-semibold tracking-wide">
              VIEW NETWORK <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </div>
          </PremiumCard>
        </Link>

        <Link href="/model" className="group">
          <PremiumCard className="h-full flex flex-col group-hover:-translate-y-1 transition-transform duration-300">
            <div className="w-12 h-12 rounded-lg bg-sci-amber/10 border border-sci-amber/30 flex items-center justify-center mb-6">
              <Activity className="w-6 h-6 text-sci-amber" />
            </div>
            <h2 className="text-lg font-semibold tracking-wide uppercase text-white mb-2">
              Model Observatory
            </h2>
            <p className="text-sm text-white/50 mb-6 flex-1">
              Inspect model reliability under increasingly difficult scientific evaluation conditions.
            </p>
            <div className="flex items-center text-sci-amber text-sm font-semibold tracking-wide">
              INSPECT METRICS <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
            </div>
          </PremiumCard>
        </Link>
      </div>
    </div>
  );
}
