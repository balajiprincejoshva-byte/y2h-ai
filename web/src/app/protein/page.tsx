"use client";

import React, { useState } from 'react';
import { PremiumCard } from '@/components/ui/PremiumCard';
import { TactileButton } from '@/components/ui/TactileButton';
import { MoleculeViewer } from '@/components/laboratory/MoleculeViewer';
import { Y2hApi, ProteinStructureResponse, NetworkResponse } from '@/lib/api';
import { FlaskConical, Search } from 'lucide-react';

export default function ProteinObservatoryPage() {
  const [query, setQuery] = useState('YFL039C');
  const [structure, setStructure] = useState<ProteinStructureResponse | null>(null);
  const [network, setNetwork] = useState<NetworkResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const [str, net] = await Promise.all([
        Y2hApi.getProteinStructure(query),
        Y2hApi.getKnownInteractors(query)
      ]);
      setStructure(str);
      setNetwork(net);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 p-6 flex flex-col max-w-[1600px] mx-auto w-full gap-6">
      
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-light tracking-widest text-white uppercase flex items-center">
            <FlaskConical className="mr-3 w-6 h-6 text-sci-cyan" />
            Protein Observatory
          </h1>
          <p className="text-sm text-gray-400 mt-1 tracking-wide">
            Detailed structural and topological metadata for specific yeast open reading frames
          </p>
        </div>
        
        <div className="flex space-x-4">
          <input 
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="bg-black/40 border border-white/10 rounded px-4 py-2 font-mono text-sm text-white focus:outline-none focus:border-sci-cyan/50"
            placeholder="Target ORF (e.g. YFL039C)"
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
          />
          <TactileButton variant="primary" onClick={handleSearch} isLoading={isLoading}>
            <Search className="w-4 h-4 mr-2" />
            Analyze Protein
          </TactileButton>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-[500px]">
        
        {/* Left: 3D Structure */}
        <PremiumCard title="Structural Conformation" className="flex flex-col p-4">
          {structure ? (
            <div className="flex-1 relative border border-white/5 bg-black/20 rounded-lg overflow-hidden">
              <MoleculeViewer 
                pdbUrl={structure.pdb_url} 
                proteinId={structure.protein_id} 
                structureAvailable={structure.structure_available}
              />
              <div className="absolute bottom-4 left-0 w-full text-center">
                <span className="bg-black/60 backdrop-blur px-3 py-1 rounded text-[10px] text-gray-400 font-mono">
                  SOURCE: {structure.source || "None"}
                </span>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-600 font-mono tracking-widest text-sm">
              NO STRUCTURE LOADED
            </div>
          )}
        </PremiumCard>

        {/* Right: Instrument Data Panel */}
        <div className="flex flex-col space-y-6">
          <PremiumCard title="Identity & Context" className="flex flex-col">
            <div className="space-y-4 font-mono text-sm">
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-gray-500">ORF / IDENTIFIER</span>
                <span className="text-white">{structure?.protein_id || "—"}</span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-gray-500">STRUCTURE STATUS</span>
                <span className={structure?.structure_available ? "text-sci-green" : "text-sci-amber"}>
                  {structure ? (structure.structure_available ? "RESOLVED" : "SEQUENCE ONLY") : "—"}
                </span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-gray-500">KNOWN DEGREE (BIOGRID)</span>
                <span className="text-white">{network?.nodes.find(n => n.id === query.toUpperCase())?.degree || 0}</span>
              </div>
              <div className="flex justify-between border-b border-white/5 pb-2">
                <span className="text-gray-500">NEIGHBORHOOD SIZE</span>
                <span className="text-white">{network ? network.nodes.length : 0} nodes</span>
              </div>
            </div>
          </PremiumCard>
          
          <PremiumCard title="Topological Preview" className="flex-1">
             <div className="text-xs text-gray-500 tracking-wide leading-relaxed">
               For detailed 3D topological visualization and candidate edge discovery, please transfer this query to the Interaction Network.
             </div>
          </PremiumCard>
        </div>

      </div>
    </div>
  );
}
