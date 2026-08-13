"use client";

import React from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { cn } from '../ui/PremiumCard';

const STAGES = [
  "BIOGRID",
  "SEQUENCE",
  "FEATURES",
  "MODEL",
  "CALIBRATION",
  "REFERENCE CHECK",
  "ASSESSMENT"
];

interface EvidenceRailProps {
  currentStage: number; // 0 to STAGES.length
}

export function EvidenceRail({ currentStage }: EvidenceRailProps) {
  return (
    <div className="w-full bg-[#0f1524] border border-white/5 rounded-lg p-4 flex items-center justify-between overflow-x-auto shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)]">
      {STAGES.map((stage, idx) => {
        const isComplete = currentStage > idx;
        const isActive = currentStage === idx;
        const isPending = currentStage < idx;

        return (
          <React.Fragment key={stage}>
            <div className={cn(
              "flex items-center space-x-2 shrink-0 transition-opacity duration-300",
              isPending ? "opacity-30" : "opacity-100"
            )}>
              <div className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center border text-[10px]",
                isComplete ? "bg-sci-green/20 border-sci-green text-sci-green" :
                isActive ? "bg-sci-cyan/20 border-sci-cyan text-sci-cyan animate-pulse" :
                "bg-black/50 border-gray-600 text-gray-500"
              )}>
                {isComplete ? <CheckCircle2 className="w-4 h-4" /> : (idx + 1)}
              </div>
              <span className={cn(
                "text-xs font-mono tracking-widest uppercase",
                isComplete ? "text-gray-300" :
                isActive ? "text-sci-cyan" :
                "text-gray-600"
              )}>
                {stage}
              </span>
            </div>
            
            {idx < STAGES.length - 1 && (
              <ArrowRight className={cn(
                "w-4 h-4 shrink-0 mx-2",
                isComplete ? "text-gray-500" : "text-gray-800"
              )} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
