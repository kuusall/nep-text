import { useState } from "react";
import Spotlight from "@/components/Spotlight";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { Copy, Languages, Search, MessageSquare, ArrowLeft } from "lucide-react";

const sampleText = "k gardai hunuhunxa? Ma aash garxu hjur ko khabar thikai xa hola";
const sampleChips = ["vanerw", "vanney", "hajur"]; 

const Index = () => {
  const [text, setText] = useState<string>(sampleText);
  const [mode, setMode] = useState<string>("sentiment");
  const [result, setResult] = useState<{ label: string; explanation: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!text.trim()) {
      toast("Please paste some Nepali text first.");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setResult({
        label: "Binamra samanya bhawa",
        explanation:
          "Tipanni ley maitripurna swar ra samanya kalyan lai byaktha garxa.",
      });
      setLoading(false);
    }, 700);
  };

  const copyText = () => {
    navigator.clipboard.writeText(text).then(() => toast("Copied to clipboard"));
  };

  const translateText = () => {
    toast("Pretend translated to English (demo)");
  };

  return (
    <main className="min-h-screen w-full flex items-center justify-center p-6">
      <div className="w-full max-w-[480px]">
        <Spotlight className="glass rounded-lg">
          <Card className="glass rounded-lg">
            <CardHeader className="py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <img
                    src="/uploads/4bf81b54-5fff-444d-80e4-93b52ed0ebcf.png"
                    alt="NepText chat logo"
                    className="h-7 w-7 rounded-md object-contain"
                    loading="lazy"
                  />
                  <h1 className="text-sm font-semibold tracking-tight">NepText</h1>
                </div>
                
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <label htmlFor="nepali-text" className="sr-only">
                Nepali text input
              </label>
              <Textarea
                id="nepali-text"
                placeholder={sampleText}
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="rounded-xl p-3 text-sm shadow-none"
              />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="soft" size="sm" onClick={copyText} aria-label="Copy">
                          <Copy />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Copy</TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="soft" size="sm" onClick={translateText} aria-label="Translate">
                          <Languages />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Translate</TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <div className="flex items-center gap-2">
                  {sampleChips.map((c) => (
                    <Button key={c} variant="chip" size="sm">
                      {c}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Select value={mode} onValueChange={setMode}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Sentiment" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sentiment">Sentiment</SelectItem>
                    <SelectItem value="Emotion">Emotion</SelectItem>
                    <SelectItem value="summary">Summary</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={analyze} variant="hero" size="lg" className="rounded-full px-5" aria-label="Analyze">
                  <Search />
                </Button>
              </div>

              {result && (
                <section aria-live="polite" className="mt-2">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm text-muted-foreground">{mode[0].toUpperCase() + mode.slice(1)}</p>
                    <Button variant="ghost" size="sm" onClick={() => setResult(null)}>
                      <ArrowLeft className="mr-1" /> Back
                    </Button>
                  </div>
                  <div className="flex flex-col gap-3">
                    <div>
                      <Badge className="text-sm px-3 py-1 rounded-full" variant="secondary">
                        {result.label}
                      </Badge>
                    </div>
                    <div className="rounded-xl border p-4 bg-card">
                      <p className="text-base font-semibold leading-relaxed">
                        {result.explanation}
                      </p>
                    </div>
                  </div>
                </section>
              )}

              {loading && (
                <p className="text-sm text-muted-foreground">Analyzing…</p>
              )}
            </CardContent>
          </Card>
        </Spotlight>

        <h1 className="sr-only">NepText — Nepali Text Sentiment Analyzer</h1>
      </div>
    </main>
  );
};

export default Index;
