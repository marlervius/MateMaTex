"use client";

import { useEffect, useState } from "react";
import { Clock, Sparkles, Star, Trash2, Copy } from "lucide-react";
import { listHistory, removeHistoryEntry, updateHistoryFavorite, type HistoryEntry } from "@/lib/generation-history";
import { useAppStore } from "@/lib/store";

export default function HistoryPage() {
  const setRequest = useAppStore((s) => s.setRequest);
  const [entries, setEntries] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    setEntries(listHistory());
  }, []);

  const refresh = () => setEntries(listHistory());

  if (entries.length > 0) {
    return (
      <div className="max-w-content mx-auto">
        <div className="mb-6">
          <h1 className="font-display text-3xl mb-1">Historikk</h1>
          <p className="text-text-secondary text-sm">
            Gjenbruk tidligere innstillinger, merk favoritter, og rydd opp ved behov.
          </p>
        </div>
        <div className="space-y-3">
          {entries.map((entry) => (
            <div key={entry.jobId} className="card flex items-center justify-between gap-4">
              <div>
                <h3 className="text-sm font-medium">{entry.topic}</h3>
                <p className="text-xs text-text-secondary mt-1">
                  {entry.grade} · {entry.materialType} · {new Date(entry.createdAt).toLocaleString("nb-NO")}
                </p>
                {entry.request.competencyGoals.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {entry.request.competencyGoals.slice(0, 3).map((goal) => (
                      <span key={goal} className="badge text-[10px] !py-0.5 bg-accent-blue/10 text-accent-blue">
                        {goal}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-1">
                <button
                  className="btn-ghost !p-2"
                  title="Merk som favoritt"
                  onClick={() => {
                    updateHistoryFavorite(entry.jobId, !entry.favorite);
                    refresh();
                  }}
                >
                  <Star
                    size={16}
                    className={entry.favorite ? "fill-accent-orange text-accent-orange" : "text-text-muted"}
                  />
                </button>
                <a
                  href="/"
                  className="btn-secondary"
                  onClick={() => setRequest({ ...entry.request })}
                >
                  <Copy size={14} />
                  Lag lignende
                </a>
                <button
                  className="btn-ghost !p-2 text-accent-red"
                  title="Slett fra historikk"
                  onClick={() => {
                    removeHistoryEntry(entry.jobId);
                    refresh();
                  }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

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
