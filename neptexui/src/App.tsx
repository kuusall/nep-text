import React, { useState } from "react";
import toast, { Toaster } from "react-hot-toast";
import { Separator } from "@/components/ui/separator";

import { Header } from "@/components/Header";
import { TextInputArea } from "@/components/TextInputArea";
import { ActionButtons } from "@/components/ActionButtons";
import { SuggestionsList } from "@/components/SuggestionsList";
import { AnalysisSelector } from "@/components/AnalysisSelector";
import { AnalysisResult } from "@/components/AnalysisResult";

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [currentInput, setCurrentInput] = useState<"en" | "np">("en");
  const [selection, setSelection] = useState("sentiment");
  const [text, setText] = useState<string>("");

  const suggestions = ["khana", "khayau", "Haina", "Ea", "Hora"];

  const fetchAnalysis = async () => {
    if (!text.trim()) {
      toast.error("Please enter some text first");
      return;
    }
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000)); // mock delay
    setLoading(false);
  };

  const appendText = (word: string) => {
    setText((prev) => prev + word + " ");
  };

  const toggleLang = () => {
    setCurrentInput((prev) => (prev === "en" ? "np" : "en"));
  };

  return (
    <div className="min-h-screen bg-background text-foreground max-sm:px-4 md:px-24 px-36 space-y-4">
      <Header />
      <Separator />

      <main className="w-full space-y-4">
        <p className="py-2 capitalize">{currentInput}</p>

        <TextInputArea text={text} setText={setText} />

        <div className="flex justify-between">
          <ActionButtons text={text} toggleLang={toggleLang} />
          <SuggestionsList suggestions={suggestions} appendText={appendText} />
        </div>

        <Separator />

        <AnalysisSelector
          selection={selection}
          setSelection={setSelection}
          loading={loading}
          onAnalyze={fetchAnalysis}
        />

        <AnalysisResult loading={loading} selection={selection} />

        <Toaster position="top-center" />
      </main>
    </div>
  );
};

export default App;