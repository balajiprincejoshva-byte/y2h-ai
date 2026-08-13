"use client";

import React, { useEffect, useState } from 'react';
import { PremiumCard } from '@/components/ui/PremiumCard';
import { StatusLamp } from '@/components/ui/StatusLamp';
import { Y2hApi, ProvenanceManifest } from '@/lib/api';
import { Database, Loader2 } from 'lucide-react';

const RenderHash = ({ label, hash }: { label: string, hash: string }) => (
  <div className="flex flex-col border-b border-white/5 pb-3">
    <span className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">{label}</span>
    <span className="font-mono text-xs text-sci-cyan break-all">{hash}</span>
  </div>
);

export default function ProvenancePage() {
  const [manifest, setManifest] = useState<ProvenanceManifest | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const m = await Y2hApi.getProvenance();
        setManifest(m);
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
        RETRIEVING PROVENANCE ARCHIVE
      </div>
    );
  }

  if (!manifest) {
    return <div className="p-6 text-sci-red">Failed to load provenance data.</div>;
  }

  return (
    <div className="flex-1 p-6 flex flex-col max-w-[1200px] mx-auto w-full gap-6">
      
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-light tracking-widest text-white uppercase flex items-center">
            <Database className="mr-3 w-6 h-6 text-sci-cyan" />
            Evidence & Provenance
          </h1>
          <p className="text-sm text-gray-400 mt-1 tracking-wide">
            Cryptographic tracing of scientific dataset and model generation
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <PremiumCard title="Run Environment" className="flex flex-col space-y-4">
          <RenderHash label="Run ID" hash={manifest.run_id} />
          <RenderHash label="Timestamp" hash={manifest.timestamp} />
          <RenderHash label="Python Version" hash={manifest.python_version} />
          <RenderHash label="Dependency Lock Hash" hash={manifest.dependency_lock_hash} />
          <div className="flex items-center space-x-2 mt-2">
            <StatusLamp status="green" size="sm" />
            <span className="text-xs uppercase tracking-widest text-gray-400">Environment Verified</span>
          </div>
        </PremiumCard>

        <PremiumCard title="Dataset & Features" className="flex flex-col space-y-4">
          <RenderHash label="Dataset Hash (BioGRID + Negatome)" hash={manifest.dataset_hash} />
          <RenderHash label="Feature Hash (Classical + ESM-2)" hash={manifest.feature_hash} />
          <div className="flex items-center space-x-2 mt-2">
            <StatusLamp status="green" size="sm" />
            <span className="text-xs uppercase tracking-widest text-gray-400">Data Cryptographically Immutable</span>
          </div>
        </PremiumCard>

        <PremiumCard title="Model Generation Config" className="flex flex-col space-y-4">
          <div className="flex flex-col border-b border-white/5 pb-3">
            <span className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Model Version</span>
            <span className="font-mono text-xs text-white">{manifest.model_version}</span>
          </div>
          <div className="flex flex-col border-b border-white/5 pb-3">
            <span className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Feature Extraction</span>
            <span className="font-mono text-xs text-white">{manifest.feature_version}</span>
          </div>
          <div className="flex flex-col border-b border-white/5 pb-3">
            <span className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Evaluation Split</span>
            <span className="font-mono text-xs text-white">{manifest.evaluation_version}</span>
          </div>
        </PremiumCard>

        <PremiumCard title="Determinism Seeds" className="flex flex-col space-y-4">
           <div className="grid grid-cols-3 gap-4">
              <div className="bg-black/20 border border-white/5 p-4 rounded text-center">
                 <div className="text-2xl font-mono text-sci-cyan mb-1">{manifest.split_seed}</div>
                 <div className="text-[10px] uppercase tracking-widest text-gray-500">Split Seed</div>
              </div>
              <div className="bg-black/20 border border-white/5 p-4 rounded text-center">
                 <div className="text-2xl font-mono text-sci-cyan mb-1">{manifest.model_seed}</div>
                 <div className="text-[10px] uppercase tracking-widest text-gray-500">Model Seed</div>
              </div>
              <div className="bg-black/20 border border-white/5 p-4 rounded text-center">
                 <div className="text-2xl font-mono text-sci-cyan mb-1">{manifest.negative_sampling_seed}</div>
                 <div className="text-[10px] uppercase tracking-widest text-gray-500">Negative Seed</div>
              </div>
           </div>
        </PremiumCard>
        
      </div>
    </div>
  );
}
