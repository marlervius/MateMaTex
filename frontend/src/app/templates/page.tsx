"use client";

import { LayoutTemplate, Plus } from "lucide-react";

export default function TemplatesPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <LayoutTemplate size={48} className="text-text-muted opacity-20 mb-4" />
      <h2 className="font-display text-2xl mb-2">Ingen maler ennå</h2>
      <p className="text-text-secondary text-sm mb-6 max-w-sm">
        Lagre dine favorittinnstillinger som maler for raskere generering.
      </p>
      <button className="btn-primary" disabled>
        <Plus size={14} />
        Ny mal (kommer snart)
      </button>
    </div>
  );
}
