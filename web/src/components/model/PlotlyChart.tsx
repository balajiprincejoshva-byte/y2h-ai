"use client";

import React from 'react';
import dynamic from 'next/dynamic';
import type { PlotParams } from 'react-plotly.js';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

export default function PlotlyChart(props: PlotParams) {
  return (
    <Plot
      {...props}
      style={{ width: '100%', height: '100%', ...props.style }}
      useResizeHandler={true}
      layout={{
        ...(props.layout || {}),
        autosize: true,
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {
          family: 'Inter, sans-serif',
          color: '#94a3b8'
        },
        margin: { t: 40, r: 20, b: 40, l: 40 },
        xaxis: {
          ...((props.layout as { xaxis?: unknown })?.xaxis || {}),
          gridcolor: 'rgba(255,255,255,0.05)',
          zerolinecolor: 'rgba(255,255,255,0.1)'
        },
        yaxis: {
          ...((props.layout as { yaxis?: unknown })?.yaxis || {}),
          gridcolor: 'rgba(255,255,255,0.05)',
          zerolinecolor: 'rgba(255,255,255,0.1)'
        }
      }}
      config={{
        displayModeBar: false,
        responsive: true,
        ...(props.config || {})
      }}
    />
  );
}
