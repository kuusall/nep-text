import React, { useCallback } from "react";
import { cn } from "@/lib/utils";

interface SpotlightProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: React.ElementType;
}

const Spotlight: React.FC<SpotlightProps> = ({ as: Comp = "div", className, children, ...props }) => {
  const handleMove = useCallback<React.MouseEventHandler<HTMLDivElement>>((e) => {
    const target = e.currentTarget as HTMLElement;
    const rect = target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    target.style.setProperty("--x", `${x}px`);
    target.style.setProperty("--y", `${y}px`);
  }, []);

  return (
    <Comp
      className={cn("with-spotlight", className)}
      onMouseMove={handleMove}
      {...props}
    >
      {children}
    </Comp>
  );
};

export default Spotlight;
