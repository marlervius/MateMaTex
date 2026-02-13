"use client";

import { useState, useEffect } from "react";
import { Settings, Sun, Moon } from "lucide-react";

export default function SettingsPage() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggleTheme = () => {
    const html = document.documentElement;
    html.classList.add("theme-transitioning");
    if (isDark) {
      html.classList.remove("dark");
      localStorage.setItem("theme", "light");
    } else {
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
    }
    setIsDark(!isDark);
    setTimeout(() => html.classList.remove("theme-transitioning"), 250);
  };

  return (
    <div className="max-w-reading mx-auto">
      <h1 className="font-display text-3xl mb-8">Innstillinger</h1>

      <div className="space-y-6">
        {/* Appearance */}
        <div className="card">
          <h2 className="text-sm font-medium mb-4">Utseende</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-primary">Tema</p>
              <p className="text-xs text-text-muted">Velg mellom mørkt og lyst tema</p>
            </div>
            <button
              onClick={toggleTheme}
              className="btn-secondary !py-2"
            >
              {isDark ? <Moon size={14} /> : <Sun size={14} />}
              {isDark ? "Mørkt" : "Lyst"}
            </button>
          </div>
        </div>

        {/* Generation defaults */}
        <div className="card">
          <h2 className="text-sm font-medium mb-4">Standard-innstillinger</h2>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-text-muted block mb-1">
                Standard klassetrinn
              </label>
              <select className="input !w-auto">
                <option>8. trinn</option>
                <option>9. trinn</option>
                <option>10. trinn</option>
                <option>VG1 1T</option>
                <option>VG2 R1</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-text-muted block mb-1">
                Standard språknivå
              </label>
              <select className="input !w-auto">
                <option>Standard norsk</option>
                <option>Forenklet (B2)</option>
                <option>Enklere (B1)</option>
              </select>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="card">
          <h2 className="text-sm font-medium mb-2">Om MateMaTeX</h2>
          <p className="text-xs text-text-muted">
            Versjon 2.0 — AI-drevet matematikkverksted for norske lærere.
            Bygget med LangGraph, SymPy, FastAPI og Next.js.
          </p>
        </div>
      </div>
    </div>
  );
}
