import React from "react";
import LoadingSpinner from "./Spinner";

interface AnalysisResultProps {
  loading: boolean;
  selection: string;
}

export const AnalysisResult: React.FC<AnalysisResultProps> = ({
  loading,
  selection,
}) => {
  if (loading) {
    return (
      <>
        <LoadingSpinner size="sm" />
      </>
    );
  }

  return (
    <div className="pt-4">
      <p className="text-sm text-muted-foreground">
        This shows the {selection} analysis
      </p>
      <p className="text-foreground capitalize">{selection}</p>
    </div>
  );
};
