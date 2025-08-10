import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";

interface AnalysisSelectorProps {
  selection: string;
  setSelection: (val: string) => void;
  loading: boolean;
  onAnalyze: () => void;
}

export const AnalysisSelector: React.FC<AnalysisSelectorProps> = ({
  setSelection,
  loading,
  onAnalyze,
}) => (
  <div className="flex items-center justify-start space-x-2">
    <div className="flex w-full">
      <Select onValueChange={(value) => setSelection(value)}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select Analysis" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="sentiment">Sentiment</SelectItem>
          <SelectItem value="summary">Summary</SelectItem>
          <SelectItem value="emotion">Emotion Analysis</SelectItem>
        </SelectContent>
      </Select>
    </div>

    <Button onClick={onAnalyze} disabled={loading}>
      Analyze
    </Button>
  </div>
);
