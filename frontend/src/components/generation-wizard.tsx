"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { startGeneration, streamProgress, getResult } from "@/lib/api";

/* -----------------------------------------------------------------------
   Data
   ----------------------------------------------------------------------- */
const GRADES = [
  { value: "1.-4. trinn", label: "1.–4. trinn", sub: "Barneskole" },
  { value: "5.-7. trinn", label: "5.–7. trinn", sub: "Mellomtrinn" },
  { value: "8. trinn", label: "8. trinn", sub: "Ungdomsskole" },
  { value: "9. trinn", label: "9. trinn", sub: "Ungdomsskole" },
  { value: "10. trinn", label: "10. trinn", sub: "Ungdomsskole" },
  { value: "VG1 1T", label: "VG1 1T", sub: "Studieforberedende" },
  { value: "VG1 1P", label: "VG1 1P", sub: "Praktisk" },
  { value: "VG2 2P", label: "VG2 2P", sub: "Praktisk" },
  { value: "VG2 R1", label: "VG2 R1", sub: "Realfag" },
  { value: "VG3 R2", label: "VG3 R2", sub: "Realfag" },
];

const TOPICS: Record<string, string[]> = {
  "1.-4. trinn": ["Tall og telling", "Addisjon", "Subtraksjon", "Multiplikasjon", "Geometriske figurer", "Måling"],
  "5.-7. trinn": ["Brøk", "Desimaltall", "Prosent", "Areal og omkrets", "Statistikk", "Negative tall"],
  "8. trinn": ["Algebra", "Lineære likninger", "Brøk og prosent", "Geometri", "Statistikk", "Funksjoner"],
  "9. trinn": ["Lineære funksjoner", "Likningssett", "Pytagoras", "Sannsynlighet", "Potenser", "Tall og algebra"],
  "10. trinn": ["Funksjoner", "Likninger", "Geometri", "Trigonometri", "Sannsynlighet", "Økonomi"],
  "VG1 1T": ["Algebra", "Likninger og ulikheter", "Funksjoner", "Geometri", "Sannsynlighet"],
  "VG1 1P": ["Prosent og økonomi", "Lineære funksjoner", "Geometri", "Statistikk"],
  "VG2 2P": ["Funksjoner", "Statistikk", "Sannsynlighet", "Modellering"],
  "VG2 R1": ["Algebra", "Funksjoner", "Derivasjon", "Vektorer", "Kombinatorikk"],
  "VG3 R2": ["Integrasjon", "Differensiallikninger", "Romgeometri", "Vektorer i rommet"],
};

const MATERIAL_TYPES = [
  { value: "arbeidsark", label: "Oppgaveark", desc: "Sett med oppgaver og løsninger", icon: "📝" },
  { value: "kapittel", label: "Fullt kapittel", desc: "Teori, eksempler og oppgaver", icon: "📖" },
  { value: "prøve", label: "Eksamen", desc: "Prøve med poengskjema", icon: "📋" },
  { value: "differensiert", label: "Differensiert", desc: "Tre nivåer automatisk", icon: "🔀" },
];

const LANGUAGE_LEVELS = [
  { value: "standard", label: "Standard norsk" },
  { value: "b2", label: "Forenklet (B2)" },
  { value: "b1", label: "Enklere (B1)" },
];

/* -----------------------------------------------------------------------
   Slide animation variants
   ----------------------------------------------------------------------- */
const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 80 : -80,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -80 : 80,
    opacity: 0,
  }),
};

/* -----------------------------------------------------------------------
   Component
   ----------------------------------------------------------------------- */
export function GenerationWizard() {
  const { request, setRequest } = useAppStore();
  const store = useAppStore();
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const totalSteps = 3;

  const goNext = () => {
    if (step < totalSteps - 1) {
      setDirection(1);
      setStep(step + 1);
    }
  };
  const goPrev = () => {
    if (step > 0) {
      setDirection(-1);
      setStep(step - 1);
    }
  };

  // Keyboard nav
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      goNext();
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      goPrev();
    }
  };

  const canGenerate = request.topic.trim().length > 0;

  const handleGenerate = async () => {
    if (!canGenerate) return;
    store.startGeneration();

    try {
      const { job_id } = await startGeneration({
        grade: request.grade,
        topic: request.topic,
        material_type: request.materialType,
        language_level: request.languageLevel,
        num_exercises: request.numExercises,
        difficulty: request.difficulty,
        include_theory: request.includeTheory,
        include_examples: request.includeExamples,
        include_exercises: request.includeExercises,
        include_solutions: request.includeSolutions,
        include_graphs: request.includeGraphs,
        competency_goals: request.competencyGoals,
        extra_instructions: request.extraInstructions,
      });

      streamProgress(job_id, {
        onStep: (s) => store.addStep(s),
        onCurrentAgent: (a) => store.setCurrentAgent(a),
        onComplete: async (data) => {
          const result = await getResult(job_id);
          store.setResult({
            jobId: job_id,
            status: data.status,
            fullDocument: result.full_document,
            pdfUrl: result.pdf_path,
            steps: result.steps,
            mathVerification: {
              claimsChecked: data.math_checks,
              claimsCorrect: data.math_correct,
              claimsIncorrect: data.math_checks - data.math_correct,
              allCorrect: data.math_checks === data.math_correct,
            },
            latexCompiled: data.latex_compiled,
            totalDuration: data.total_duration,
            error: data.error || "",
          });
        },
        onError: (err) => store.setError(err),
      });
    } catch (err: any) {
      store.setError(err.message || "Noe gikk galt");
    }
  };

  return (
    <div className="max-w-reading mx-auto" onKeyDown={handleKeyDown} tabIndex={-1}>
      {/* Step indicator */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {["Trinn", "Emne", "Innstillinger"].map((label, i) => (
          <div key={i} className="flex items-center gap-2">
            <button
              onClick={() => {
                setDirection(i > step ? 1 : -1);
                setStep(i);
              }}
              className={`flex items-center gap-2 text-sm transition-colors ${
                i === step
                  ? "text-accent-blue font-medium"
                  : i < step
                  ? "text-text-primary"
                  : "text-text-muted"
              }`}
            >
              <span
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                  i === step
                    ? "bg-accent-blue text-white"
                    : i < step
                    ? "bg-accent-green/20 text-accent-green"
                    : "bg-surface-elevated text-text-muted"
                }`}
              >
                {i < step ? "✓" : i + 1}
              </span>
              <span className="hidden sm:inline">{label}</span>
            </button>
            {i < totalSteps - 1 && (
              <div className="w-8 h-px bg-border" />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      <div className="overflow-hidden relative min-h-[320px]">
        <AnimatePresence initial={false} custom={direction} mode="wait">
          {step === 0 && (
            <motion.div
              key="step-grade"
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.25, ease: "easeInOut" }}
            >
              <h2 className="font-display text-2xl mb-2 text-center">
                Hvilket trinn?
              </h2>
              <p className="text-text-secondary text-sm text-center mb-6">
                Velg klassetrinnet for materialet
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {GRADES.map((g, i) => (
                  <motion.button
                    key={g.value}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                    onClick={() => {
                      setRequest({ grade: g.value });
                      goNext();
                    }}
                    className={`card-interactive !p-4 text-center ${
                      request.grade === g.value
                        ? "!border-accent-blue bg-accent-blue/5"
                        : ""
                    }`}
                  >
                    <div className="text-lg font-semibold mb-0.5">
                      {g.label}
                    </div>
                    <div className="text-[11px] text-text-muted">{g.sub}</div>
                    {request.grade === g.value && (
                      <motion.div
                        layoutId="grade-check"
                        className="absolute top-2 right-2 w-5 h-5 rounded-full bg-accent-blue flex items-center justify-center text-white text-xs"
                      >
                        ✓
                      </motion.div>
                    )}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {step === 1 && (
            <motion.div
              key="step-topic"
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.25, ease: "easeInOut" }}
            >
              <h2 className="font-display text-2xl mb-2 text-center">
                Hvilket emne?
              </h2>
              <p className="text-text-secondary text-sm text-center mb-6">
                Velg et foreslått emne eller skriv ditt eget
              </p>

              {/* Topic chips */}
              <div className="flex flex-wrap justify-center gap-2 mb-6">
                {(TOPICS[request.grade] || []).map((topic, i) => (
                  <motion.button
                    key={topic}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.04 }}
                    onClick={() => setRequest({ topic })}
                    className={`badge text-sm !py-1.5 !px-3 cursor-pointer transition-all ${
                      request.topic === topic
                        ? "bg-accent-blue text-white"
                        : "bg-surface-elevated text-text-secondary hover:bg-accent-blue/10 hover:text-accent-blue"
                    }`}
                  >
                    {topic}
                  </motion.button>
                ))}
              </div>

              {/* Custom topic input */}
              <div className="max-w-md mx-auto">
                <input
                  type="text"
                  value={request.topic}
                  onChange={(e) => setRequest({ topic: e.target.value })}
                  placeholder="Eller skriv et emne... f.eks. 'Pytagoras setning'"
                  className="input text-center"
                  autoFocus
                />
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step-settings"
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.25, ease: "easeInOut" }}
            >
              <h2 className="font-display text-2xl mb-2 text-center">
                Type og innstillinger
              </h2>
              <p className="text-text-secondary text-sm text-center mb-6">
                Tilpass materialet etter behov
              </p>

              {/* Material type */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                {MATERIAL_TYPES.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => setRequest({ materialType: type.value })}
                    className={`card-interactive !p-4 text-center relative ${
                      request.materialType === type.value
                        ? "!border-accent-blue bg-accent-blue/5"
                        : ""
                    }`}
                  >
                    <div className="text-2xl mb-1">{type.icon}</div>
                    <div className="text-sm font-medium">{type.label}</div>
                    <div className="text-[10px] text-text-muted mt-0.5">
                      {type.desc}
                    </div>
                  </button>
                ))}
              </div>

              {/* Advanced settings (expandable) */}
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-xs text-text-muted hover:text-text-secondary flex items-center gap-1 mx-auto mb-3 transition-colors"
              >
                <motion.span
                  animate={{ rotate: showAdvanced ? 90 : 0 }}
                  transition={{ duration: 0.15 }}
                >
                  ▸
                </motion.span>
                Avanserte innstillinger
              </button>

              <AnimatePresence>
                {showAdvanced && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-4 overflow-hidden"
                  >
                    {/* Content toggles */}
                    <div className="card">
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        {[
                          { key: "includeTheory" as const, label: "Teori" },
                          { key: "includeExamples" as const, label: "Eksempler" },
                          { key: "includeExercises" as const, label: "Oppgaver" },
                          { key: "includeSolutions" as const, label: "Løsninger" },
                          { key: "includeGraphs" as const, label: "Grafer" },
                        ].map(({ key, label }) => (
                          <label
                            key={key}
                            className="flex items-center gap-2 text-sm cursor-pointer text-text-secondary hover:text-text-primary transition-colors"
                          >
                            <input
                              type="checkbox"
                              checked={request[key]}
                              onChange={(e) =>
                                setRequest({ [key]: e.target.checked })
                              }
                              className="rounded border-border"
                            />
                            {label}
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Sliders and selects */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div className="card !p-3">
                        <label className="text-xs text-text-muted mb-1 block">
                          Antall oppgaver: {request.numExercises}
                        </label>
                        <input
                          type="range"
                          min={1}
                          max={30}
                          value={request.numExercises}
                          onChange={(e) =>
                            setRequest({
                              numExercises: parseInt(e.target.value),
                            })
                          }
                          className="w-full accent-accent-blue"
                        />
                      </div>
                      <div className="card !p-3">
                        <label className="text-xs text-text-muted mb-1 block">
                          Vanskelighetsgrad
                        </label>
                        <select
                          value={request.difficulty}
                          onChange={(e) =>
                            setRequest({ difficulty: e.target.value })
                          }
                          className="input !py-1.5"
                        >
                          <option value="Lett">Lett</option>
                          <option value="Middels">Middels</option>
                          <option value="Vanskelig">Vanskelig</option>
                        </select>
                      </div>
                      <div className="card !p-3">
                        <label className="text-xs text-text-muted mb-1 block">
                          Språknivå
                        </label>
                        <select
                          value={request.languageLevel}
                          onChange={(e) =>
                            setRequest({ languageLevel: e.target.value })
                          }
                          className="input !py-1.5"
                        >
                          {LANGUAGE_LEVELS.map((l) => (
                            <option key={l.value} value={l.value}>
                              {l.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Extra instructions */}
                    <div className="card !p-3">
                      <label className="text-xs text-text-muted mb-1 block">
                        Spesielle instruksjoner (valgfritt)
                      </label>
                      <textarea
                        value={request.extraInstructions}
                        onChange={(e) =>
                          setRequest({ extraInstructions: e.target.value })
                        }
                        placeholder="f.eks. 'Bruk kontekster fra sport', 'Inkluder bevisoppgaver'"
                        rows={2}
                        className="input resize-none"
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation buttons */}
      <div className="flex items-center justify-between mt-8">
        <button
          onClick={goPrev}
          disabled={step === 0}
          className="btn-ghost disabled:opacity-30"
        >
          <ChevronLeft size={16} />
          Tilbake
        </button>

        {step < totalSteps - 1 ? (
          <button onClick={goNext} className="btn-primary">
            Neste
            <ChevronRight size={16} />
          </button>
        ) : (
          <button
            onClick={handleGenerate}
            disabled={!canGenerate}
            className="btn-primary !px-8 shadow-lg shadow-accent-blue/20 disabled:opacity-40 disabled:shadow-none"
          >
            <Sparkles size={16} />
            Generer materiale
          </button>
        )}
      </div>
    </div>
  );
}
