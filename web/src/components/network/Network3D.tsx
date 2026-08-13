"use client";

import React, { useCallback, useRef, useEffect } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import { NetworkNode, NetworkEdge } from '@/lib/api';

interface Network3DProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  onNodeClick: (node: NetworkNode) => void;
  onEdgeClick: (edge: NetworkEdge) => void;
  width: number;
  height: number;
}

export default function Network3D({ nodes, edges, onNodeClick, onEdgeClick, width, height }: Network3DProps) {
  const fgRef = useRef<{
    scene: () => THREE.Scene;
    d3Force: (forceName: string) => { strength: (val: number) => void } | undefined;
  } | null>(null);


  const glowTexture = React.useMemo(() => {
    if (typeof document === 'undefined') return null;
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
      gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
      gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.8)');
      gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.2)');
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 64, 64);
      
      return new THREE.CanvasTexture(canvas);
    }
    return null;
  }, []);

  const getEdgeColor = useCallback((edge: NetworkEdge) => {
    if (edge.is_predicted) {
      return 'rgba(6, 182, 212, 0.7)';
    }
    return 'rgba(255, 255, 255, 0.15)';
  }, []);
  
  const getEdgeWidth = useCallback((edge: NetworkEdge) => {
    return edge.is_predicted ? (edge.probability ? edge.probability * 3 : 2) : 1;
  }, []);

  const nodeThreeObject = useCallback((node: NetworkNode) => {
    const group = new THREE.Group();
    
    // Size scales logarithmically with degree
    const baseSize = 3 + Math.log1p(node.degree || 1) * 2;
    
    const geometry = new THREE.SphereGeometry(baseSize, 32, 32);
    
    const color = node.is_query ? 0x06b6d4 : 0x1e293b;
    const emissive = node.is_query ? 0x004455 : 0x000000;
    
    const material = new THREE.MeshPhysicalMaterial({
      color: color,
      emissive: emissive,
      transparent: true,
      opacity: node.is_query ? 0.95 : 0.8,
      roughness: 0.1,
      metalness: 0.2,
      transmission: 0.7,
      ior: 1.5,
    });
    
    const sphere = new THREE.Mesh(geometry, material);
    group.add(sphere);
    
    if (glowTexture) {
      const spriteMaterial = new THREE.SpriteMaterial({ 
        map: glowTexture, 
        color: node.is_query ? 0x06b6d4 : 0x475569, 
        transparent: true, 
        blending: THREE.AdditiveBlending,
        opacity: node.is_query ? 0.8 : 0.4
      });
      const sprite = new THREE.Sprite(spriteMaterial);
      const scale = baseSize * 3;
      sprite.scale.set(scale, scale, 1);
      group.add(sprite);
    }
    
    return group;
  }, [glowTexture]);

  useEffect(() => {
    if (fgRef.current) {
      const scene = fgRef.current.scene();
      
      const lights = scene.children.filter((c: THREE.Object3D) => (c as THREE.Light).isLight);
      lights.forEach((l: THREE.Object3D) => scene.remove(l));
      
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);
      
      const pointLight1 = new THREE.PointLight(0x06b6d4, 400, 1000);
      pointLight1.position.set(200, 200, 200);
      scene.add(pointLight1);
      
      const pointLight2 = new THREE.PointLight(0xffffff, 200, 1000);
      pointLight2.position.set(-200, -200, -200);
      scene.add(pointLight2);
      
      const chargeForce = fgRef.current.d3Force('charge');
      if (chargeForce) {
        chargeForce.strength(-200);
      }
    }
  }, []);

  return (
    <ForceGraph3D
      // @ts-expect-error - external lib ref type mismatch
      ref={fgRef}
      graphData={{ nodes, links: edges }}
      nodeId="id"
      nodeLabel="id"
      nodeThreeObject={nodeThreeObject}
      linkSource="source"
      linkTarget="target"
      linkColor={getEdgeColor}
      linkWidth={getEdgeWidth}
      onNodeClick={(node) => onNodeClick(node as NetworkNode)}
      onLinkClick={(link) => onEdgeClick(link as NetworkEdge)}
      backgroundColor="#0b0f19"
      width={width}
      height={height}
      linkDirectionalParticles={(edge: NetworkEdge) => edge.is_predicted ? 4 : 0}
      linkDirectionalParticleSpeed={0.01}
      linkDirectionalParticleWidth={2}
      linkDirectionalParticleColor={() => '#ffffff'}
      showNavInfo={false}
    />
  );
}
