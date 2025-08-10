import React from "react";

type Size = "sm" | "md" | "lg";

interface LoadingSpinnerProps {
  size?: Size;
  label?: string;
  className?: string;
}

const sizeMap: Record<Size, string> = {
  sm: "h-2 w-2 border-2",
  md: "h-4 w-4 border-2",
  lg: "h-6 w-6 border-4",
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "md",
  label = "Analyzing...",
  className = "",
}) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`} role="status" aria-live="polite">
      <p className="text-sm">{label}</p>

      {/* Visual spinner */}
      <span
        className={`${sizeMap[size]} animate-spin rounded-full
                   border-current border-t-transparent border-b-transparent
                   ring-1 ring-offset-0`}
        aria-hidden="true"
      />
    </div>
  );
};

export default LoadingSpinner;