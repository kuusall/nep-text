import React from "react";
import { Copy, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import toast from "react-hot-toast";

interface ActionButtonsProps {
  text: string;
  toggleLang: () => void;
}

export const ActionButtons: React.FC<ActionButtonsProps> = ({
  text,
  toggleLang,
}) => {
  const handleCopy = () => {
    if (!text.trim()) {
      toast.error("Nothing to copy!");
      return;
    }
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="flex space-x-2">
      <Button variant="outline" size="icon" onClick={handleCopy}>
        <Copy className="text-foreground" />
      </Button>
      <Button variant="outline" size="icon" onClick={toggleLang}>
        <Languages className="text-foreground" />
      </Button>
    </div>
  );
};