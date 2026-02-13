"use client";

import { motion } from "framer-motion";
import { useAppStore } from "@/lib/store";
import {
  GraduationCap,
  PenTool,
  Calculator,
  CheckCircle2,
  Code2,
  Wrench,
  Circle,
  Loader2,
  AlertTriangle,
} from "lucide-react";

const AGENT_INFO: Record<
  string,
  {
    name: string;
    icon: React.ReactNode;
    description: string;
    color: string;
  }
> = {
  pedagogue: {
    name: "Pedagogen",
    icon: <GraduationCap size={18} />,
    description: "Planlegger innhold basert på LK20...",
    color: "accent-blue",
  },
  author: {
    name: "Forfatteren",
    icon: <PenTool size={18} />,
    description: "Skriver LaTeX med matematikk og illustrasjoner...",
    color: "accent-green",
  },
  math_verifier: {
    name: "Matematikkverifisering",
    icon: <Calculator size={18} />,
    description: "Verifiserer alle beregninger med SymPy...",
    color: "accent-purple",
  },
  editor: {
    name: "Redaktøren",
    icon: <CheckCircle2 size={18} />,
    description: "Kvalitetssikrer innholdet...",
    color: "accent-teal",
  },
  latex_validator: {
    name: "LaTeX-kompilering",
    icon: <Code2 size={18} />,
    description: "Kompilerer med pdflatex...",
    color: "accent-orange",
  },
  latex_fixer: {
    name: "LaTeX-fikser",
    icon: <Wrench size={18} />,
    description: "Retter kompileringsfeil...",
    color: "accent-red",
  },
};

const PIPELINE_ORDER = [
  "pedagogue",
  "author",
  "math_verifier",
  "editor",
  "latex_validator",
];

export function PipelineProgress() {
  const { steps, currentAgent } = useAppStore();
  const completedAgents = new Set(steps.map((s) => s.agent));

  // Estimate remaining time
  const completedCount = completedAgents.size;
  const totalAgents = PIPELINE_ORDER.length;
  const avgDuration =
    steps.length > 0
      ? steps.reduce((sum, s) => sum + (s.durationSeconds || 0), 0) /
        steps.length
      : 5;
  const remaining = Math.max(0, (totalAgents - completedCount) * avgDuration);

  return (
    <div className="max-w-reading mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="font-display text-2xl mb-2">
          AI-teamet jobber
        </h2>
        <p className="text-sm text-text-secondary">
          {remaining > 0
            ? `~${Math.round(remaining)} sekunder igjen`
            : "Snart ferdig..."}
        </p>
      </div>

      {/* Timeline */}
      <div className="relative max-w-lg mx-auto">
        {/* Vertical line */}
        <div className="absolute left-5 top-0 bottom-0 w-px bg-border" />

        <div className="space-y-1">
          {PIPELINE_ORDER.map((agentKey, index) => {
            const info = AGENT_INFO[agentKey];
            const isCompleted = completedAgents.has(agentKey);
            const isCurrent = currentAgent === agentKey;
            const step = steps.find((s) => s.agent === agentKey);
            const hasError = step?.error;
            const retryCount = step?.retries || 0;

            return (
              <motion.div
                key={agentKey}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative flex items-start gap-4 py-3"
              >
                {/* Node */}
                <div className="relative z-10 flex-shrink-0">
                  {isCompleted ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-10 h-10 rounded-full bg-accent-green/15 flex items-center justify-center text-accent-green"
                    >
                      <CheckCircle2 size={20} />
                    </motion.div>
                  ) : isCurrent ? (
                    <div className="w-10 h-10 rounded-full bg-accent-blue/15 flex items-center justify-center text-accent-blue animate-pulse-ring">
                      {hasError ? (
                        <AlertTriangle size={18} className="text-accent-orange" />
                      ) : (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{
                            repeat: Infinity,
                            duration: 2,
                            ease: "linear",
                          }}
                        >
                          <Loader2 size={18} />
                        </motion.div>
                      )}
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-surface-elevated flex items-center justify-center text-text-muted">
                      <Circle size={16} />
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pt-1.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm font-medium ${
                        isCompleted || isCurrent
                          ? "text-text-primary"
                          : "text-text-muted"
                      }`}
                    >
                      {info.name}
                    </span>
                    {retryCount > 0 && (
                      <span className="badge bg-accent-orange/15 text-accent-orange">
                        Forsøk {retryCount + 1}/3
                      </span>
                    )}
                    {isCompleted && step?.durationSeconds && (
                      <span className="text-xs text-text-muted">
                        {step.durationSeconds.toFixed(1)}s
                      </span>
                    )}
                  </div>

                  {/* Description / status */}
                  <p className="text-xs text-text-muted mt-0.5 truncate">
                    {isCurrent
                      ? info.description
                      : isCompleted
                      ? step?.outputSummary || "Fullført"
                      : "Venter..."}
                  </p>

                  {/* Error message */}
                  {hasError && isCurrent && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-xs text-accent-orange mt-1"
                    >
                      Retter: {step.error}
                    </motion.p>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Retries info */}
      {steps.some((s) => s.retries > 0) && (
        <p className="text-xs text-text-muted text-center mt-6">
          Verifisering kjører — feil rettes automatisk
        </p>
      )}
    </div>
  );
}
