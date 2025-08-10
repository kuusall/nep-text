import React from "react";
import { Button } from "@/components/ui/button";

interface SuggestionsListProps {
  suggestions: string[];
  appendText: (word: string) => void;
}

export const SuggestionsList: React.FC<SuggestionsListProps> = ({
  suggestions,
  appendText,
}) => (
  <div className="flex flex-col items-end space-y-2">
    <div className="flex flex-wrap gap-2">
      {suggestions.slice(0, 3).reverse().map((s) => (
        <Button key={s} variant="outline" onClick={() => appendText(s)}>
          {s}
        </Button>
      ))}
    </div>
    <p className="text-sm text-muted-foreground">Suggestions</p>
  </div>
);