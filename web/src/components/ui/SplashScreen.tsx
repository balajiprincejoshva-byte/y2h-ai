"use client";

import React, { useEffect, useState } from "react";
import { Microscope, Activity, Loader2 } from "lucide-react";
import { cn } from "@/components/ui/PremiumCard";

export function SplashScreen() {
  const [isVisible, setIsVisible] = useState(true);
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    // Start fading out after 1.2 seconds
    const fadeTimer = setTimeout(() => {
      setIsFading(true);
    }, 1200);

    // Completely remove from DOM after fade completes (1.2s + 0.5s fade)
    const removeTimer = setTimeout(() => {
      setIsVisible(false);
    }, 1700);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        "fixed inset-0 z-[9999] bg-[#0b0f19] flex flex-col items-center justify-center transition-opacity duration-500 ease-in-out",
        isFading ? "opacity-0 pointer-events-none" : "opacity-100"
      )}
    >
      <div className="relative flex flex-col items-center">
        {/* Core glowing orb */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-sci-cyan/10 rounded-full blur-3xl animate-pulse" />
        
        {/* Main Icon */}
        <div className="relative w-16 h-16 rounded-xl bg-[#0d1424] border border-sci-cyan/30 flex items-center justify-center mb-8 shadow-[0_0_30px_rgba(45,212,191,0.2)]">
          <Microscope className="w-8 h-8 text-sci-cyan animate-pulse" />
          
          {/* Orbiting element */}
          <div className="absolute inset-0 border border-sci-cyan/20 rounded-xl animate-[spin_4s_linear_infinite]" />
          <div className="absolute inset-[-4px] border border-dashed border-sci-blue/30 rounded-xl animate-[spin_8s_linear_infinite_reverse]" />
        </div>

        {/* Text sequence */}
        <div className="flex flex-col items-center space-y-3">
          <h1 className="font-mono text-xl tracking-[0.3em] text-white/90 uppercase font-bold flex items-center">
            Y2H-AI <span className="text-sci-cyan ml-2">v3</span>
          </h1>
          <div className="flex items-center space-x-2 text-xs font-mono tracking-widest text-sci-cyan/60 uppercase">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Initializing Engine...</span>
          </div>
        </div>

        {/* Progress bar line */}
        <div className="absolute -bottom-16 w-48 h-px bg-white/10 overflow-hidden">
          <div className="w-full h-full bg-sci-cyan origin-left animate-[scale-x_1.2s_ease-in-out_forwards]" />
        </div>
      </div>
      
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scale-x {
          0% { transform: scaleX(0); }
          100% { transform: scaleX(1); }
        }
      `}} />
    </div>
  );
}
