/**
 * Zustand store for MateMaTeX 2.0 — lightweight state management.
 */

import { create } from "zustand";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface GenerationRequest {
  grade: string;
  topic: string;
  materialType: string;
  languageLevel: string;
  numExercises: number;
  difficulty: string;
  includeTheory: boolean;
  includeExamples: boolean;
  includeExercises: boolean;
  includeSolutions: boolean;
  includeGraphs: boolean;
  competencyGoals: string[];
  extraInstructions: string;
}

export interface AgentStep {
  agent: string;
  startedAt: string;
  completedAt: string | null;
  durationSeconds: number;
  outputSummary: string;
  error: string;
  retries: number;
}

export interface GenerationResult {
  jobId: string;
  status: "pending" | "running" | "completed" | "failed";
  fullDocument: string;
  pdfUrl: string;
  steps: AgentStep[];
  mathVerification: {
    claimsChecked: number;
    claimsCorrect: number;
    claimsIncorrect: number;
    allCorrect: boolean;
  };
  latexCompiled: boolean;
  totalDuration: number;
  error: string;
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------
interface AppStore {
  // Generation form
  request: GenerationRequest;
  setRequest: (partial: Partial<GenerationRequest>) => void;
  resetRequest: () => void;

  // Generation state
  isGenerating: boolean;
  currentAgent: string | null;
  steps: AgentStep[];
  result: GenerationResult | null;

  // Actions
  startGeneration: () => void;
  addStep: (step: AgentStep) => void;
  setCurrentAgent: (agent: string | null) => void;
  setResult: (result: GenerationResult) => void;
  setError: (error: string) => void;

  // UI
  showLatexEditor: boolean;
  toggleLatexEditor: () => void;
}

const DEFAULT_REQUEST: GenerationRequest = {
  grade: "10. trinn",
  topic: "",
  materialType: "arbeidsark",
  languageLevel: "standard",
  numExercises: 10,
  difficulty: "Middels",
  includeTheory: true,
  includeExamples: true,
  includeExercises: true,
  includeSolutions: true,
  includeGraphs: true,
  competencyGoals: [],
  extraInstructions: "",
};

export const useAppStore = create<AppStore>((set) => ({
  // Form
  request: { ...DEFAULT_REQUEST },
  setRequest: (partial) =>
    set((state) => ({ request: { ...state.request, ...partial } })),
  resetRequest: () => set({ request: { ...DEFAULT_REQUEST } }),

  // Generation state
  isGenerating: false,
  currentAgent: null,
  steps: [],
  result: null,

  // Actions
  startGeneration: () =>
    set({ isGenerating: true, currentAgent: null, steps: [], result: null }),
  addStep: (step) =>
    set((state) => ({ steps: [...state.steps, step] })),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
  setResult: (result) =>
    set({ result, isGenerating: false, currentAgent: null }),
  setError: (error) =>
    set({
      result: {
        jobId: "",
        status: "failed",
        fullDocument: "",
        pdfUrl: "",
        steps: [],
        mathVerification: {
          claimsChecked: 0,
          claimsCorrect: 0,
          claimsIncorrect: 0,
          allCorrect: false,
        },
        latexCompiled: false,
        totalDuration: 0,
        error,
      },
      isGenerating: false,
    }),

  // UI
  showLatexEditor: false,
  toggleLatexEditor: () =>
    set((state) => ({ showLatexEditor: !state.showLatexEditor })),
}));
