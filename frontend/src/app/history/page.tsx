"use client";

import { Clock, Sparkles } from "lucide-react";

export default function HistoryPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <Clock size={48} className="text-text-muted opacity-20 mb-4" />
      <h2 className="font-display text-2xl mb-2">Ingen genereringer ennå</h2>
      <p className="text-text-secondary text-sm mb-6 max-w-sm">
        Alt du lager dukker opp her, sortert etter dato.
      </p>
      <a href="/" className="btn-primary">
        <Sparkles size={14} />
        Start din første generering
      </a>
    </div>
  );
}
