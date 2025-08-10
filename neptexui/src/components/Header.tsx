import React from "react";

export const Header: React.FC = () => (
  <header className="pt-16 flex space-x-2 items-center">
    <img src="/neptext.jpg" alt="NepText" className="w-8 h-8 rounded-sm" />
    <h1 className="text-2xl font-semibold text-foreground">NepText</h1>
  </header>
);
