"use client";

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { PremiumCard } from '@/components/ui/PremiumCard';
import { TactileButton } from '@/components/ui/TactileButton';
import { StatusLamp } from '@/components/ui/StatusLamp';
import { Y2hApi, NetworkResponse, NetworkEdge, NetworkCandidateEdge, ApiError } from '@/lib/api';
import { Network as NetworkIcon, Search, Eye } from 'lucide-react';

const Network3D = dynamic(() => import('@/components/network/Network3D'), { ssr: false });

export default function NetworkExplorerPage() {
  const [query, setQuery] = useState('YFL039C');
  const [network, setNetwork] = useState<NetworkResponse | null>(null);
  const [candidates, setCandidates] = useState<NetworkCandidateEdge[]>([]);
  const [candidatesError, setCandidatesError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [selectedEdge, setSelectedEdge] = useState<NetworkEdge | null>(null);
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      setContainerSize({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight
      });
      
      const handleResize = () => {
        if (containerRef.current) {
          setContainerSize({
            width: containerRef.current.clientWidth,
            height: containerRef.current.clientHeight
          });
        }
      };
      
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, []);

  const handleSearch = async () => {
    setIsLoading(true);
    setSelectedEdge(null);
    setCandidates([]);
    try {
      const net = await Y2hApi.getKnownInteractors(query);
      setNetwork(net);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDiscover = async () => {
    if (!network) return;
    setIsDiscovering(true);
    setCandidatesError(null);
    try {
      const res = await Y2hApi.getNetworkCandidates(query, 25);
      setCandidates(res.candidates);
    } catch (e: unknown) {
      console.error(e);
      if ((e as ApiError).status === 503 || (e as { response?: { status: number } }).response?.status === 503) {
        setCandidatesError("CANDIDATE PREDICTION SERVICE UNAVAILABLE");
      } else {
        setCandidatesError("AN UNEXPECTED ERROR OCCURRED");
      }
    } finally {
      setIsDiscovering(false);
    }
  };

  // Merge known network with predicted candidates for visualization
  const displayNodes = network ? [...network.nodes] : [];
  const displayEdges = network ? [...network.edges.map(e => ({ ...e, is_predicted: false }))] : [];
  
  if (candidates.length > 0) {
    // Add missing nodes from candidates
    candidates.forEach(c => {
      const targetId = c.source === query.toUpperCase() ? c.target : c.source;
      if (!displayNodes.find(n => n.id === targetId)) {
        displayNodes.push({ id: targetId, degree: 1, is_query: false });
      }
      displayEdges.push({
        source: c.source,
        target: c.target,
        is_predicted: true,
        probability: c.probability
      });
    });
  }

  return (
    <div className="flex-1 p-6 flex flex-col max-w-[1600px] mx-auto w-full gap-6">
      
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-light tracking-widest text-white uppercase flex items-center">
            <NetworkIcon className="mr-3 w-6 h-6 text-sci-cyan" />
            3D Interaction Network
          </h1>
          <p className="text-sm text-gray-400 mt-1 tracking-wide">
            Explore local interactomes and discover candidate edges via AI inference
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
            Load Topology
          </TactileButton>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-[600px]">
        
        {/* Main 3D Viewer */}
        <PremiumCard title="Topological Representation" className="lg:col-span-3 flex flex-col p-0 overflow-hidden relative">
          <div className="absolute top-4 left-4 z-10 flex space-x-2">
            <div className="bg-black/60 backdrop-blur border border-white/10 px-3 py-1.5 rounded flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-white/20" />
              <span className="text-[10px] uppercase tracking-widest text-gray-400 font-mono">Documented Edge</span>
            </div>
            <div className="bg-black/60 backdrop-blur border border-white/10 px-3 py-1.5 rounded flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-sci-cyan/60" />
              <span className="text-[10px] uppercase tracking-widest text-sci-cyan font-mono">Predicted Edge</span>
            </div>
          </div>
          
          <div ref={containerRef} className="flex-1 w-full bg-[#0b0f19]" style={{ minHeight: '500px' }}>
            {network && (
              <Network3D 
                nodes={displayNodes}
                edges={displayEdges}
                width={containerSize.width}
                height={containerSize.height}
                onNodeClick={() => {}}
                onEdgeClick={(e) => setSelectedEdge(e as unknown as NetworkEdge)}
              />
            )}
            {!network && !isLoading && (
              <div className="absolute inset-0 flex items-center justify-center text-gray-600 font-mono tracking-widest text-sm">
                AWAITING TOPOLOGY TARGET
              </div>
            )}
          </div>
          
          {network && candidates.length === 0 && !candidatesError && (
            <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-10">
              <TactileButton variant="primary" onClick={handleDiscover} isLoading={isDiscovering}>
                Discover Candidate Edges
              </TactileButton>
            </div>
          )}
          {candidatesError && (
             <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-10 bg-sci-red/20 border border-sci-red/50 text-sci-red text-xs font-mono tracking-widest px-4 py-2 rounded uppercase">
               {candidatesError}
             </div>
          )}
        </PremiumCard>

        {/* Edge Detail / Context Panel */}
        <div className="lg:col-span-1 flex flex-col space-y-6">
          <PremiumCard title="Network Context" className="flex flex-col">
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-white/5 pb-2">
                <span className="text-xs tracking-widest text-gray-500 uppercase">Nodes</span>
                <span className="font-mono text-gray-300">{displayNodes.length}</span>
              </div>
              <div className="flex justify-between items-center border-b border-white/5 pb-2">
                <span className="text-xs tracking-widest text-gray-500 uppercase">Documented Edges</span>
                <span className="font-mono text-gray-300">{network?.edges.length || 0}</span>
              </div>
              <div className="flex justify-between items-center border-b border-white/5 pb-2">
                <span className="text-xs tracking-widest text-sci-cyan uppercase">Predicted Edges</span>
                <span className="font-mono text-sci-cyan">{candidates.length}</span>
              </div>
            </div>
          </PremiumCard>

          {selectedEdge && (
            <PremiumCard title="Edge Detail" className="flex-1 flex flex-col">
              <div className="text-center mb-6">
                <div className="flex justify-center items-center space-x-4 mb-2">
                  <span className="font-mono text-white text-lg">{(selectedEdge.source as unknown as { id: string }).id || selectedEdge.source}</span>
                  <span className="text-gray-600">→</span>
                  <span className="font-mono text-white text-lg">{(selectedEdge.target as unknown as { id: string }).id || selectedEdge.target}</span>
                </div>
                {selectedEdge.is_predicted ? (
                  <StatusLamp status="blue" label="PREDICTED CANDIDATE" size="sm" className="justify-center" />
                ) : (
                  <StatusLamp status="green" label="DOCUMENTED" size="sm" className="justify-center" />
                )}
              </div>
              
              {selectedEdge.is_predicted && selectedEdge.probability && (
                <>
                  <div className="flex flex-col items-center justify-center mb-4 bg-black/20 p-4 rounded border border-white/5">
                    <span className="text-4xl font-light tabular-nums text-sci-cyan mb-1">
                      {(selectedEdge.probability * 100).toFixed(1)}%
                    </span>
                    <span className="text-[10px] uppercase tracking-widest text-gray-500">Calibrated Probability</span>
                  </div>
                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gray-500 uppercase tracking-widest text-[9px]">Model</span>
                      <span className="font-mono text-gray-300">{(selectedEdge as unknown as NetworkCandidateEdge).model_version || "Y2H-AI RF V3"}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-gray-500 uppercase tracking-widest text-[9px]">Calibration</span>
                      <span className="font-mono text-gray-300">Isotonic</span>
                    </div>
                    <div className="flex flex-col text-xs bg-black/30 p-2 rounded border border-white/5 mt-2">
                      <span className="text-gray-500 uppercase tracking-widest text-[9px] mb-1">Documentation Status</span>
                      <span className="font-mono text-amber-500 text-[10px]">{(selectedEdge as unknown as NetworkCandidateEdge).documentation_status || "NO DOCUMENTED INTERACTION FOUND"}</span>
                    </div>
                  </div>
                </>
              )}
              
              <div className="flex-1" />
              
              <TactileButton className="w-full text-xs">
                <Eye className="w-4 h-4 mr-2" /> Inspect in Laboratory
              </TactileButton>
            </PremiumCard>
          )}
        </div>
        
      </div>
    </div>
  );
}
