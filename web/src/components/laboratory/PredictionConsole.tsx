"use client";

import React from 'react';
import { PremiumCard } from '../ui/PremiumCard';
import { StatusLamp } from '../ui/StatusLamp';
import { PredictResponse } from '@/lib/api';

export function PredictionConsole({ result }: { result: PredictResponse | null }) {
  if (!result) {
    return (
      <PremiumCard title="Interaction Assessment" className="h-full flex flex-col justify-center items-center opacity-50">
        <div className="font-mono text-xs text-gray-500 uppercase tracking-widest text-center">
          Awaiting Analysis...
        </div>
      </PremiumCard>
    );
  }

  if (result.error === "MODEL_UNAVAILABLE") {
    return (
      <PremiumCard title="Interaction Assessment" className="h-full flex flex-col justify-center items-center p-6 text-center border-sci-red/30">
        <div className="w-12 h-12 rounded-full border border-sci-red/30 flex items-center justify-center mb-4 text-sci-red">
          !
        </div>
        <div className="text-sm font-semibold text-sci-red tracking-widest uppercase mb-2">
          Model Service Unavailable
        </div>
        <div className="text-xs text-gray-400 mb-6 max-w-[200px] leading-relaxed">
          The validated prediction model could not be loaded. No prediction was generated.
        </div>
        <div className="flex space-x-2 w-full justify-center">
          <button className="text-[10px] bg-sci-red/10 border border-sci-red/30 text-sci-red uppercase tracking-widest px-3 py-1.5 rounded hover:bg-sci-red/20 transition-colors">
            Retry Analysis
          </button>
          <button className="text-[10px] bg-black/40 border border-white/10 text-gray-400 uppercase tracking-widest px-3 py-1.5 rounded hover:text-white transition-colors">
            View Diagnostics
          </button>
        </div>
      </PremiumCard>
    );
  }

  if (result.error === "INVALID_REQUEST") {
    const reason = (result as { _apiError?: { message: string } })._apiError?.message || "Invalid input provided.";
    return (
      <PremiumCard title="Interaction Assessment" className="h-full flex flex-col justify-center items-center p-6 text-center border-amber-500/30">
        <div className="w-12 h-12 rounded-full border border-amber-500/30 flex items-center justify-center mb-4 text-amber-500">
          !
        </div>
        <div className="text-sm font-semibold text-amber-500 tracking-widest uppercase mb-2">
          Analysis Request Invalid
        </div>
        <div className="text-xs text-gray-400 mb-6 max-w-[200px] leading-relaxed">
          The protein pair could not be processed by the analysis service.
          <br/><br/>
          Reason: {reason}
        </div>
        <div className="flex space-x-2 w-full justify-center">
          <button className="text-[10px] bg-black/40 border border-white/10 text-gray-400 uppercase tracking-widest px-3 py-1.5 rounded hover:text-white transition-colors" onClick={() => window.location.reload()}>
            Reset
          </button>
        </div>
      </PremiumCard>
    );
  }

  if (result.error) {
    const reason = (result as { _apiError?: { message: string } })._apiError?.message || result.error;
    return (
      <PremiumCard title="Interaction Assessment" className="h-full flex flex-col justify-center items-center p-6 text-center border-sci-red/30">
        <div className="w-12 h-12 rounded-full border border-sci-red/30 flex items-center justify-center mb-4 text-sci-red">
          X
        </div>
        <div className="text-sm font-semibold text-sci-red tracking-widest uppercase mb-2">
          Prediction Failed
        </div>
        <div className="text-xs text-gray-400 mb-6 max-w-[200px] leading-relaxed">
          An unexpected error occurred during prediction.
          <br/><br/>
          Reason: {reason}
        </div>
      </PremiumCard>
    );
  }

  const prob = (result.calibrated_probability * 100).toFixed(1);
  const isDocumented = result.documentation.status !== "No documented interaction found";
  
  let lampStatus: 'green' | 'amber' | 'blue' = 'amber';
  if (isDocumented) lampStatus = 'green';
  else if (result.calibrated_probability < 0.5) lampStatus = 'blue';

  return (
    <PremiumCard title="Interaction Assessment" className="h-full flex flex-col">
      <div className="flex-1 flex flex-col justify-center items-center mb-8">
        <div className="text-6xl font-light tracking-tight text-white tabular-nums mb-2">
          {prob}%
        </div>
        <div className="text-xs font-mono text-sci-cyan uppercase tracking-widest">
          Calibrated Probability
        </div>
      </div>

      <div className="space-y-4">
        <div className="p-3 bg-black/20 rounded border border-white/5">
          <div className="flex justify-between items-start mb-1">
            <div className="text-[10px] text-gray-500 uppercase tracking-widest">Documentation Status</div>
            <div className="text-[9px] text-gray-600 font-mono" title={result.documentation.source}>SRC</div>
          </div>
          <StatusLamp status={lampStatus} label={result.documentation.status} size="sm" />
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-black/20 rounded border border-white/5">
            <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Model</div>
            <div className="text-xs font-mono text-gray-300" title={result.model.feature_version}>{result.model.version}</div>
          </div>
          <div className="p-3 bg-black/20 rounded border border-white/5">
            <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Calibration</div>
            <div className="text-xs font-mono text-gray-300 truncate" title={result.calibration.method}>{result.calibration.method}</div>
          </div>
        </div>

        <div className="p-3 bg-black/20 rounded border border-white/5">
          <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Prediction ID</div>
          <div className="text-xs font-mono text-gray-400 truncate" title={result.prediction_id}>
            {result.prediction_id}
          </div>
        </div>
      </div>
    </PremiumCard>
  );
}
