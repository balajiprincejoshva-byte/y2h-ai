import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface PremiumCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  variant?: 'raised' | 'inset';
}

export function PremiumCard({
  title,
  variant = 'raised',
  className,
  children,
  ...props
}: PremiumCardProps) {
  return (
    <div
      className={cn(
        variant === 'raised' ? 'neumorphic-panel' : 'neumorphic-inset',
        'p-6 relative overflow-hidden',
        className
      )}
      {...props}
    >
      {title && (
        <h3 className="text-sm font-semibold tracking-wider text-muted-foreground uppercase mb-4 opacity-80">
          {title}
        </h3>
      )}
      <div className="relative z-10 flex-1 flex flex-col min-h-0">{children}</div>
    </div>
  );
}
