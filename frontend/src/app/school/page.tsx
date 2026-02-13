"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { School, Search, BookOpen } from "lucide-react";

export default function SchoolBankPage() {
  const [exercises, setExercises] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Placeholder — will fetch from /school/exercises in production
  const isEmpty = exercises.length === 0;

  return (
    <div className="max-w-content mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl mb-1">Skolens oppgavebank</h1>
          <p className="text-text-secondary text-sm">
            Oppgaver delt av lærere på din skole
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <input
          type="text"
          placeholder="Søk i skolens oppgaver..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10 w-full"
        />
      </div>

      {/* Empty state */}
      {isEmpty && !loading && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center min-h-[50vh] text-center"
        >
          <School size={48} className="text-text-muted opacity-20 mb-4" />
          <h2 className="font-display text-2xl mb-2">Ingen oppgaver ennå</h2>
          <p className="text-text-secondary text-sm mb-6 max-w-sm">
            Når du eller kollegaer publiserer oppgaver til skolens bank, dukker de
            opp her. Gå til oppgavebanken og klikk «Publiser til skolen» for å dele.
          </p>
          <a href="/exercises" className="btn bg-[hsl(var(--accent-blue))] text-white hover:opacity-90 inline-flex items-center gap-2">
            <BookOpen size={14} />
            Gå til min oppgavebank
          </a>
        </motion.div>
      )}

      {/* Exercise list — populated when data exists */}
      {!isEmpty && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exercises.map((ex) => (
            <div key={ex.id} className="card-interactive p-4">
              <h3 className="font-medium text-sm mb-1">{ex.title}</h3>
              <p className="text-xs text-text-muted">{ex.topic} · {ex.grade_level}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
