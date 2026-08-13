"use client";

import React, { useState } from 'react';
import { PremiumCard } from '@/components/ui/PremiumCard';
import { TactileButton } from '@/components/ui/TactileButton';
import { StatusLamp } from '@/components/ui/StatusLamp';
import { ProteinSearchInput } from '@/components/ui/ProteinSearchInput';
import { MoleculeViewer } from '@/components/laboratory/MoleculeViewer';
import { PredictionConsole } from '@/components/laboratory/PredictionConsole';
import { EvidenceRail } from '@/components/laboratory/EvidenceRail';
import { Y2hApi, PredictResponse, ProteinStructureResponse } from '@/lib/api';
import { Network } from 'lucide-react';

type StructureState =
  | { status: "loading" }
  | { status: "available"; data: ProteinStructureResponse }
  | { status: "unavailable"; data: ProteinStructureResponse }
  | { status: "error"; message: string };

export default function LaboratoryPage() {
  const [protA, setProtA] = useState('YFL039C');
  const [protB, setProtB] = useState('YAL001C');
  
  const [structA, setStructA] = useState<StructureState | null>(null);
  const [structB, setStructB] = useState<StructureState | null>(null);
  
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [stage, setStage] = useState(7); // default to end if nothing running
  const [showConceptual, setShowConceptual] = useState(false);

  const handleAnalyze = async () => {
    setIsRunning(true);
    setPrediction(null);
    setStructA({ status: "loading" });
    setStructB({ status: "loading" });
    setShowConceptual(false);
    
    // Simulate realistic pipeline stages for the UI
    setStage(0);
    await new Promise(r => setTimeout(r, 400)); // BIOGRID
    setStage(1);
    await new Promise(r => setTimeout(r, 400)); // SEQUENCE
    setStage(2);
    await new Promise(r => setTimeout(r, 800)); // FEATURES (takes longer)
    setStage(3);
    
    try {
      // Fetch structures independently (catch prevents breaking prediction)
      const pA = Y2hApi.getProteinStructure(protA).catch(e => ({ isApiError: true, message: e.message }));
      const pB = Y2hApi.getProteinStructure(protB).catch(e => ({ isApiError: true, message: e.message }));
      
      let predResult = null;
      let predError: Error & { isApiError?: boolean; status?: number } | null = null;
      try {
        predResult = await Y2hApi.predictPair({ protein_a: protA, protein_b: protB });
      } catch (e: unknown) {
        predError = e as Error & { isApiError?: boolean; status?: number };
      }
      
      const sA = await pA;
      const sB = await pB;
      
      setStage(4);
      await new Promise(r => setTimeout(r, 300)); // CALIBRATION
      setStage(5);
      await new Promise(r => setTimeout(r, 300)); // REFERENCE CHECK
      setStage(6);
      
      if (predError) {
        if (predError.isApiError) {
          if (predError.status === 503) {
            setPrediction({ error: "MODEL_UNAVAILABLE", _apiError: predError } as unknown as PredictResponse);
          } else if (predError.status === 400) {
            setPrediction({ error: "INVALID_REQUEST", _apiError: predError } as unknown as PredictResponse);
          } else if (predError.status === 404) {
            setPrediction({ error: "NOT_FOUND", _apiError: predError } as unknown as PredictResponse);
          } else {
            setPrediction({ error: predError.message, _apiError: predError } as unknown as PredictResponse);
          }
        } else {
          setPrediction({ error: "UNKNOWN_ERROR" } as unknown as PredictResponse);
        }
      } else {
        setPrediction(predResult);
      }
      
      if ('isApiError' in sA) {
        setStructA({ status: "error", message: sA.message as string });
      } else {
        setStructA({ status: sA.structure_available ? "available" : "unavailable", data: sA as ProteinStructureResponse });
      }
      
      if ('isApiError' in sB) {
        setStructB({ status: "error", message: sB.message as string });
      } else {
        setStructB({ status: sB.structure_available ? "available" : "unavailable", data: sB as ProteinStructureResponse });
      }
      
      setStage(7); // ASSESSMENT Complete
    } catch (error: unknown) {
      console.error("Critical analysis pipeline failure", error);
      setStage(7);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="flex-1 p-6 flex flex-col max-w-[1600px] mx-auto w-full gap-6">
      
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-light tracking-widest text-white uppercase flex items-center">
            <Network className="mr-3 w-6 h-6 text-sci-cyan" />
            Interaction Laboratory
          </h1>
          <p className="text-sm text-gray-400 mt-1 tracking-wide">
            Computational assessment of protein–protein interaction hypotheses
          </p>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
        
        {/* LEFT: Input Instrument */}
        <div className="lg:col-span-3 flex flex-col space-y-6">
          <PremiumCard title="Target Sequence A" className="flex-1 flex flex-col justify-center">
            <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-2 block">Standard Name / ORF</label>
            <div className="mb-4">
              <ProteinSearchInput 
                value={protA}
                onChange={setProtA}
                placeholder="Search canonical registry (e.g. YFL039C)"
              />
            </div>
            {structA && structA.status !== "loading" && structA.status !== "error" && (
              <StatusLamp 
                status={structA.status === "available" ? 'green' : 'amber'} 
                label={structA.status === "available" ? 'Structure Resolved' : 'Sequence Only'} 
                size="sm" 
              />
            )}
          </PremiumCard>

          <PremiumCard title="Target Sequence B" className="flex-1 flex flex-col justify-center">
            <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-2 block">Standard Name / ORF</label>
            <div className="mb-4">
              <ProteinSearchInput 
                value={protB}
                onChange={setProtB}
                placeholder="Search canonical registry (e.g. YAL001C)"
              />
            </div>
            {structB && structB.status !== "loading" && structB.status !== "error" && (
              <StatusLamp 
                status={structB.status === "available" ? 'green' : 'amber'} 
                label={structB.status === "available" ? 'Structure Resolved' : 'Sequence Only'} 
                size="sm" 
              />
            )}
          </PremiumCard>

          <TactileButton 
            variant="primary" 
            className="w-full py-4 text-sm"
            onClick={handleAnalyze}
            isLoading={isRunning}
          >
            Run Interaction Analysis
          </TactileButton>
        </div>

        {/* CENTER: 3D Viewport */}
        <div className="lg:col-span-6 flex flex-col">
          <PremiumCard title="Molecular Viewport" className="flex-1 flex flex-col p-4 relative">
            
            {/* Viewport controls */}
            <div className="absolute top-4 right-4 z-20 flex space-x-2">
              <button 
                onClick={() => setShowConceptual(!showConceptual)}
                disabled={!prediction}
                className={`text-[10px] uppercase tracking-widest px-3 py-1.5 rounded border transition-colors ${
                  showConceptual ? 'bg-sci-cyan/20 border-sci-cyan text-sci-cyan' : 'bg-black/40 border-white/10 text-gray-400 hover:text-white'
                } disabled:opacity-30 disabled:cursor-not-allowed`}
              >
                Hypothesis Field
              </button>
            </div>

            <div className="flex-1 w-full bg-black/20 rounded-lg overflow-hidden border border-white/5 relative flex flex-col" style={{ minHeight: '500px' }}>
              {/* Top half: Protein A */}
              <div className="h-1/2 border-b border-white/5 relative">
                <div className="absolute top-2 left-2 z-10 text-[10px] font-mono text-gray-500">PROTEIN A: {protA}</div>
                <MoleculeViewer 
                  proteinId={protA} 
                  pdbUrl={structA && 'data' in structA ? structA.data.pdb_url : undefined} 
                  structureAvailable={structA && 'data' in structA ? structA.data.structure_available : undefined}
                  hasError={structA?.status === "error"}
                  isConceptualInteraction={showConceptual} 
                />
              </div>
              {/* Bottom half: Protein B */}
              <div className="h-1/2 relative">
                <div className="absolute top-2 left-2 z-10 text-[10px] font-mono text-gray-500">PROTEIN B: {protB}</div>
                <MoleculeViewer 
                  proteinId={protB} 
                  pdbUrl={structB && 'data' in structB ? structB.data.pdb_url : undefined} 
                  structureAvailable={structB && 'data' in structB ? structB.data.structure_available : undefined}
                  hasError={structB?.status === "error"}
                  isConceptualInteraction={false} 
                />
              </div>
            </div>
            
            {((structA && 'data' in structA && structA.data.source) || (structB && 'data' in structB && structB.data.source)) && (
              <div className="mt-4 text-[10px] text-gray-600 font-mono tracking-widest text-center">
                STRUCTURAL SOURCE: {(structA && 'data' in structA ? structA.data.source : '') || (structB && 'data' in structB ? structB.data.source : '')}
              </div>
            )}
          </PremiumCard>
        </div>

        {/* RIGHT: Console */}
        <div className="lg:col-span-3">
          <PredictionConsole result={prediction} />
        </div>
      </div>

      {/* BOTTOM: Evidence Rail */}
      <EvidenceRail currentStage={stage} />
      
    </div>
  );
}
