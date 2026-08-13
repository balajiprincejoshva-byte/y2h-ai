import React from 'react';
import { cn } from './PremiumCard';

export type LampStatus = 'green' | 'amber' | 'red' | 'blue' | 'off';

interface StatusLampProps extends React.HTMLAttributes<HTMLDivElement> {
  status: LampStatus;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

const colorMap = {
  green: 'bg-sci-green shadow-[0_0_10px_#10b981]',
  amber: 'bg-sci-amber shadow-[0_0_10px_#f59e0b]',
  red: 'bg-sci-red shadow-[0_0_10px_#ef4444]',
  blue: 'bg-sci-cyan shadow-[0_0_10px_#06b6d4]',
  off: 'bg-gray-600 shadow-none',
};

const sizeMap = {
  sm: 'w-2 h-2',
  md: 'w-3 h-3',
  lg: 'w-4 h-4',
};

export function StatusLamp({ status, label, size = 'md', className, ...props }: StatusLampProps) {
  return (
    <div className={cn('flex items-center space-x-2', className)} {...props}>
      <div
        className={cn(
          'rounded-full border border-black/20',
          sizeMap[size],
          colorMap[status]
        )}
      />
      {label && (
        <span className="text-xs font-semibold tracking-wider uppercase text-gray-300">
          {label}
        </span>
      )}
    </div>
  );
}
