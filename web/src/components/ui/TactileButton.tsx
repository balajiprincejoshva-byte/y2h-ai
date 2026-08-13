import React from 'react';
import { cn } from './PremiumCard';
import { Loader2 } from 'lucide-react';

interface TactileButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}

export function TactileButton({
  children,
  isLoading,
  variant = 'secondary',
  className,
  disabled,
  ...props
}: TactileButtonProps) {
  
  const baseStyle = "neumorphic-button relative overflow-hidden font-semibold tracking-wide uppercase px-6 py-3 flex items-center justify-center transition-all duration-150";
  
  const variantStyles = {
    primary: "text-sci-cyan border-sci-cyan/20",
    secondary: "text-gray-300",
    danger: "text-sci-red border-sci-red/20",
  };
  
  return (
    <button
      className={cn(
        baseStyle,
        variantStyles[variant],
        (disabled || isLoading) ? "opacity-50 cursor-not-allowed pointer-events-none" : "",
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}
