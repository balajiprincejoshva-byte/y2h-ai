"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';

interface MoleculeViewerProps {
  pdbUrl?: string;
  proteinId?: string;
  isConceptualInteraction?: boolean;
  structureAvailable?: boolean | null;
  hasError?: boolean;
}

// Global script loading state — shared across all MoleculeViewer instances
let _3dmolLoadPromise: Promise<void> | null = null;

function load3Dmol(): Promise<void> {
  if ((window as { $3Dmol?: unknown }).$3Dmol) return Promise.resolve();
  if (_3dmolLoadPromise) return _3dmolLoadPromise;

  _3dmolLoadPromise = new Promise<void>((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://3Dmol.org/build/3Dmol-min.js';
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load 3Dmol.js'));
    document.head.appendChild(script);
  });

  return _3dmolLoadPromise;
}

export function MoleculeViewer({ pdbUrl, proteinId, isConceptualInteraction, structureAvailable, hasError }: MoleculeViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<{ clear: () => void; resize: () => void; render: () => void; addModel: (m: string, f: string) => void; setStyle: (a: object, b: object) => void; addSurface: (t: unknown, o: object) => void; zoomTo: () => void; rotate: (a: number, b: string) => void; } | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading-script' | 'loading-pdb' | 'ready' | 'error' | 'unavailable'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const activeStatus = hasError ? 'error' : (structureAvailable === false ? 'unavailable' : (structureAvailable == null || !pdbUrl ? 'idle' : status));

  useEffect(() => {
    if (!pdbUrl || structureAvailable === false || hasError) {
      return;
    }

    let cancelled = false;

    async function init() {
      try {
        // Step 1: Load the 3Dmol.js library
        setStatus('loading-script');
        await load3Dmol();
        if (cancelled) return;

        const $3Dmol = (window as { $3Dmol?: { createViewer: (e: HTMLElement, o: object) => unknown; SurfaceType: { VDW: unknown } } }).$3Dmol;
        if (!$3Dmol) {
          throw new Error('3Dmol.js failed to initialize');
        }

        // Step 2: Create viewer (or reuse existing)
        if (!containerRef.current) return;
        
        if (viewerRef.current) {
          viewerRef.current.clear();
        } else {
          // Clear the container first to avoid duplicate canvases
          containerRef.current.innerHTML = '';
          viewerRef.current = $3Dmol.createViewer(containerRef.current, {
            backgroundColor: '0x0b0f19',
            antialias: true,
          }) as unknown as typeof viewerRef.current;
        }

        const viewer = viewerRef.current;
        if (!viewer) return;

        // Step 3: Fetch and render PDB
        setStatus('loading-pdb');
        const res = await fetch(pdbUrl as string);
        if (!res.ok) throw new Error(`PDB fetch failed: ${res.status}`);
        if (cancelled) return;

        const pdbData = await res.text();
        if (cancelled) return;

        const format = pdbUrl!.toLowerCase().endsWith('.cif') ? 'cif' : 'pdb';
        viewer.addModel(pdbData, format);
        viewer.setStyle({}, { cartoon: { color: 'spectrum' } });

        if (isConceptualInteraction) {
          viewer.addSurface($3Dmol.SurfaceType.VDW, {
            opacity: 0.25,
            color: 'cyan',
          });
        }

        viewer.zoomTo();
        viewer.render();
        viewer.rotate(45, 'y');
        viewer.render();
        setStatus('ready');
      } catch (err: unknown) {
        if (!cancelled) {
          console.error('MoleculeViewer error:', err);
          setErrorMsg((err as Error).message || 'Unknown error');
          setStatus('error');
        }
      }
    }

    init();

    return () => {
      cancelled = true;
    };
  }, [pdbUrl, isConceptualInteraction, structureAvailable, hasError, proteinId]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (viewerRef.current) {
        viewerRef.current.resize();
        viewerRef.current.render();
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="w-full h-full relative" style={{ minHeight: '200px' }}>
      {/* 3Dmol viewer container — always mounted so it has dimensions */}
      <div
        ref={containerRef}
        className="absolute inset-0"
        style={{ 
          zIndex: activeStatus === 'ready' ? 1 : 0,
          opacity: activeStatus === 'ready' ? 1 : 0,
          transition: 'opacity 0.5s ease-in',
        }}
      />

      {/* Overlay states */}
      {activeStatus === 'idle' && (
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="text-gray-600 font-mono tracking-widest text-[11px] flex flex-col items-center">
            <div className="w-12 h-12 border-2 border-dashed border-gray-700 rounded-full mb-3 flex items-center justify-center text-lg opacity-50">
              🧬
            </div>
            AWAITING STRUCTURE
          </div>
        </div>
      )}

      {activeStatus === 'unavailable' && (
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="text-gray-500 font-mono tracking-widest text-[11px] text-center px-4">
            NO VALIDATED STRUCTURE AVAILABLE
          </div>
        </div>
      )}

      {(activeStatus === 'loading-script' || activeStatus === 'loading-pdb') && (
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="text-sci-cyan font-mono tracking-widest text-[11px] flex items-center">
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            {activeStatus === 'loading-script' ? 'LOADING VIEWER...' : 'FETCHING STRUCTURE...'}
          </div>
        </div>
      )}

      {activeStatus === 'error' && (
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="text-sci-red font-mono tracking-widest text-[11px] text-center px-4">
            STRUCTURE RESOLUTION UNAVAILABLE
            <div className="text-[9px] text-gray-500 mt-1">{errorMsg || "API Error"}</div>
          </div>
        </div>
      )}

      {activeStatus === 'ready' && isConceptualInteraction && (
        <div className="absolute top-3 left-3 z-20 bg-black/70 backdrop-blur-sm border border-sci-cyan/30 px-3 py-1.5 rounded">
          <span className="text-[9px] text-sci-cyan tracking-widest uppercase font-mono">
            Conceptual Interaction — Not Atomic Docking
          </span>
        </div>
      )}
    </div>
  );
}
