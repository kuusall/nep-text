import React from "react";
import { Textarea } from "@/components/ui/textarea";

interface TextInputAreaProps {
  text: string;
  setText: React.Dispatch<React.SetStateAction<string>>;
  placeholder?: string;
}

export const TextInputArea: React.FC<TextInputAreaProps> = ({
  text,
  setText,
  placeholder,
}) => (
  <Textarea
    placeholder={placeholder || "Type something..."}
    className="bg-card text-card-foreground flex-1"
    value={text}
    onChange={(e) => setText(e.target.value)}
    onKeyDown={(e) => e.key === "Enter" && e.preventDefault()}
  />
);