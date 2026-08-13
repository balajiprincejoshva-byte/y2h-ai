"use client";

import React, { useEffect, useState } from 'react';
import { PremiumCard } from '@/components/ui/PremiumCard';
import { Y2hApi } from '@/lib/api';
import { Activity, Loader2 } from 'lucide-react';
import PlotlyChart from '@/components/model/PlotlyChart';

export default function ModelObservatoryPage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [metrics, setMetrics] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [ablation, setAblation] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, a] = await Promise.all([
          Y2hApi.getModelMetrics(),
          Y2hApi.getModelAblation()
        ]);
        setMetrics(m);
        setAblation(a);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-sci-cyan font-mono tracking-widest text-sm">
        <Loader2 className="w-5 h-5 animate-spin mr-3" />
        INITIALIZING OBSERVATORY
      </div>
    );
  }

  if (!metrics || !ablation) {
    return <div className="p-6 text-sci-red">Failed to load scientific metrics.</div>;
  }

  // Parse Generalization Data (Random Forest)
  const splits = ['c1', 'c2', 'c3'];
  const aurocs = splits.map(s => metrics['models']['RandomForest'][s]['1to1_balanced']['auroc']);
  const auprcs = splits.map(s => metrics['models']['RandomForest'][s]['1to1_balanced']['auprc']);
  
  // Parse Imbalance Data for C1 Random Forest
  const imbModes = ['1to1_balanced', '1to10_imbalanced', '1to100_imbalanced'];
  const imbAurocs = imbModes.map(m => metrics['models']['RandomForest']['c1'][m]['auroc']);
  const imbAuprcs = imbModes.map(m => metrics['models']['RandomForest']['c1'][m]['auprc']);
  
  // Parse Ablation Data (C3)
  const classicalC3 = ablation["Classical-Only"]["c3"]["auroc"];
  const esmC3 = ablation["ESM-2-Only"]["c3"]["auroc"];
  const combinedC3 = ablation["Classical+ESM-2"]["c3"]["auroc"];

  return (
    <div className="flex-1 p-6 flex flex-col max-w-[1600px] mx-auto w-full gap-6">
      
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-light tracking-widest text-white uppercase flex items-center">
            <Activity className="mr-3 w-6 h-6 text-sci-amber" />
            Model Observatory
          </h1>
          <p className="text-sm text-gray-400 mt-1 tracking-wide">
            How the predictor behaves under increasingly difficult evaluation conditions
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* C1/C2/C3 Generalization */}
        <PremiumCard title="Generalization Trajectory (C1 → C2 → C3)">
          <div className="h-[300px]">
            <PlotlyChart 
              data={[
                {
                  x: ['C1 (Random)', 'C2 (Unseen Pair)', 'C3 (Unseen Protein)'],
                  y: aurocs,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'AUROC',
                  line: { color: '#06b6d4', width: 3 },
                  marker: { size: 10 }
                },
                {
                  x: ['C1 (Random)', 'C2 (Unseen Pair)', 'C3 (Unseen Protein)'],
                  y: auprcs,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'AUPRC',
                  line: { color: '#f59e0b', width: 3 },
                  marker: { size: 10 }
                }
              ]}
              layout={{
                yaxis: { title: 'Score', range: [0.5, 1.0] },
                showlegend: true,
                legend: { orientation: 'h', y: -0.2 }
              }}
            />
          </div>
        </PremiumCard>

        {/* Feature Ablation */}
        <PremiumCard title="Feature Ablation (C3 AUROC)">
          <div className="h-[300px]">
            <PlotlyChart 
              data={[
                {
                  x: ['Classical Only', 'ESM-2 Only', 'Classical + ESM-2'],
                  y: [classicalC3, esmC3, combinedC3],
                  type: 'bar',
                  marker: {
                    color: ['#1e293b', '#ef4444', '#06b6d4']
                  }
                }
              ]}
              layout={{
                yaxis: { title: 'C3 AUROC', range: [0.5, 0.75] }
              }}
            />
          </div>
          <div className="absolute top-4 right-4 bg-sci-red/10 border border-sci-red/30 px-3 py-2 rounded text-xs text-sci-red max-w-xs">
            <strong>SCIENTIFIC FINDING:</strong> ESM-2 did not improve C3 performance in the current experiment.
          </div>
        </PremiumCard>

        {/* Class Imbalance Lab */}
        <PremiumCard title="Class Imbalance Stress Test (C1)">
          <div className="h-[300px]">
            <PlotlyChart 
              data={[
                {
                  x: ['1:1 (Balanced)', '1:10 (Imbalanced)', '1:100 (Severe)'],
                  y: imbAurocs,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'AUROC',
                  line: { color: '#06b6d4', dash: 'dot', width: 2 }
                },
                {
                  x: ['1:1 (Balanced)', '1:10 (Imbalanced)', '1:100 (Severe)'],
                  y: imbAuprcs,
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'AUPRC',
                  line: { color: '#f59e0b', width: 3 }
                }
              ]}
              layout={{
                yaxis: { title: 'Score', range: [0, 1.0] },
                showlegend: true,
                legend: { orientation: 'h', y: -0.2 }
              }}
            />
          </div>
          <div className="mt-4 text-xs text-gray-500 font-mono tracking-widest text-center">
            SEVERE CLASS IMBALANCE CAN PRESERVE RANKING ABILITY (AUROC) WHILE SUBSTANTIALLY DEGRADING PRECISION (AUPRC).
          </div>
        </PremiumCard>

        {/* Calibration */}
        <PremiumCard title="Model Calibration (C1 Random Forest)">
          <div className="h-[300px]">
            <PlotlyChart 
              data={[
                {
                  x: [0, 1],
                  y: [0, 1],
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Perfect Calibration',
                  line: { color: 'rgba(255,255,255,0.2)', dash: 'dash' }
                },
                {
                  x: metrics['models']['RandomForest']['c1']['1to1_balanced']['calibration']['prob_pred'],
                  y: metrics['models']['RandomForest']['c1']['1to1_balanced']['calibration']['prob_true'],
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'RF Calibration',
                  line: { color: '#10b981' }
                }
              ]}
              layout={{
                xaxis: { title: 'Predicted Probability', range: [0, 1] },
                yaxis: { title: 'Observed Frequency', range: [0, 1] },
                showlegend: true,
                legend: { orientation: 'h', y: -0.2 }
              }}
            />
          </div>
        </PremiumCard>
        
      </div>
    </div>
  );
}
