"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Y2hApi } from '@/lib/api';

interface SearchResult {
  protein_id: string;
  standard_name: string;
  sgdid: string;
  description: string;
}

interface ProteinSearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function ProteinSearchInput({ value, onChange, placeholder }: ProteinSearchInputProps) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const fetchResults = async () => {
      if (!isOpen) return;
      setIsLoading(true);
      try {
        const res = await Y2hApi.searchProteins(value);
        setResults(res.results || []);
      } catch (err) {
        console.error(err);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    const debounce = setTimeout(() => {
      fetchResults();
    }, 300);

    return () => clearTimeout(debounce);
  }, [value, isOpen]);

  return (
    <div className="relative w-full" ref={wrapperRef}>
      <input
        type="text"
        className="w-full bg-black/40 border border-white/10 rounded px-4 py-2 font-mono text-sm text-white focus:outline-none focus:border-sci-cyan/50 transition-colors"
        value={value}
        placeholder={placeholder}
        onFocus={() => setIsOpen(true)}
        onChange={(e) => {
          onChange(e.target.value);
          setIsOpen(true);
        }}
      />
      
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 max-h-60 overflow-y-auto bg-gray-900 border border-white/10 rounded-md shadow-2xl backdrop-blur-xl">
          {isLoading ? (
            <div className="p-3 text-xs text-sci-cyan animate-pulse">Scanning registry...</div>
          ) : results.length > 0 ? (
            <ul className="py-1">
              {results.map(r => (
                <li 
                  key={r.protein_id}
                  className="px-3 py-2 cursor-pointer hover:bg-white/5 transition-colors border-b border-white/5 last:border-0"
                  onClick={() => {
                    onChange(r.protein_id);
                    setIsOpen(false);
                  }}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-mono text-white">{r.protein_id}</span>
                    {r.standard_name && (
                      <span className="text-xs font-mono text-sci-cyan">{r.standard_name}</span>
                    )}
                  </div>
                  <div className="text-[10px] text-gray-500 truncate">{r.description || r.sgdid}</div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-3 text-xs text-gray-500">No canonical matches found.</div>
          )}
        </div>
      )}
    </div>
  );
}
