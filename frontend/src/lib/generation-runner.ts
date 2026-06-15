/**
 * Generation watch orchestration — lives outside React component lifecycle so
 * SSE/polling survive when GenerationWizard unmounts on isGenerating=true.
 */

import {
  streamProgress,
  getResult,
  watchGenerationJob,
  closeActiveStream,
  isTerminalGenerateStatus,
  isJobAborted,
  type JobStatusResponse,
} from "@/lib/api";
import {
  mapApiResultToGenerationResult,
  isSuccessfulStatus,
} from "@/lib/map-api-result";
import { appendHistory } from "@/lib/generation-history";
import { useAppStore, type GenerationRequest } from "@/lib/store";

type ActiveRun = {
  jobId: string;
  pollSignal: { cancelled: boolean };
};

let activeRun: ActiveRun | null = null;

export function stopGenerationWatch(): void {
  if (!activeRun) return;
  activeRun.pollSignal.cancelled = true;
  activeRun = null;
  closeActiveStream();
}

export function isWatchingJob(jobId: string): boolean {
  return activeRun?.jobId === jobId && !activeRun.pollSignal.cancelled;
}

/**
 * Stream agent progress, poll /status, and load /result when the job finishes.
 * Safe to call from both GenerationWizard and PipelineProgress (idempotent).
 */
export function startGenerationWatch(
  jobId: string,
  snapshot: GenerationRequest
): void {
  if (isWatchingJob(jobId)) return;

  stopGenerationWatch();

  const pollSignal = { cancelled: false };
  activeRun = { jobId, pollSignal };

  const {
    addStep,
    setCurrentAgent,
    setResult,
    setError,
  } = useAppStore.getState();

  let resultLoaded = false;
  let loadingResult = false;

  const finishWithResult = async () => {
    const raw = await getResult(jobId);
    if (activeRun?.jobId !== jobId) return;
    const mapped = mapApiResultToGenerationResult(raw, snapshot);
    setResult(mapped);
    if (isSuccessfulStatus(mapped.status)) {
      appendHistory({
        jobId,
        createdAt: new Date().toISOString(),
        topic: snapshot.topic,
        grade: snapshot.grade,
        materialType: snapshot.materialType,
        favorite: false,
        request: { ...snapshot },
      });
    }
  };

  const showPlaceholderResult = (status: string) => {
    const currentSteps = useAppStore.getState().steps;
    setResult(
      mapApiResultToGenerationResult(
        {
          job_id: jobId,
          status,
          full_document: "",
          pdf_available: true,
          latex_compilation: { success: true },
          math_verification: {
            claims_checked: 0,
            claims_correct: 0,
            claims_incorrect: 0,
            claims_unparseable: 0,
            all_correct: true,
            summary: "",
          },
          steps: currentSteps.map((s) => ({
            agent: s.agent,
            started_at: s.startedAt,
            completed_at: s.completedAt,
            duration_seconds: s.durationSeconds,
            output_summary: s.outputSummary,
            error: s.error,
            retries: s.retries,
          })),
          total_duration_seconds: 0,
          error: "",
        },
        snapshot
      )
    );
  };

  const loadResultOnce = async (statusHint?: string) => {
    if (resultLoaded || loadingResult || activeRun?.jobId !== jobId) return;
    if (isJobAborted(jobId)) return;
    loadingResult = true;
    if (statusHint && statusHint !== "failed") {
      setCurrentAgent(null);
      showPlaceholderResult(statusHint);
    }
    try {
      await finishWithResult();
      resultLoaded = true;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Kunne ikke hente resultat";
      setError(msg, snapshot);
    } finally {
      loadingResult = false;
      if (activeRun?.jobId === jobId) {
        stopGenerationWatch();
      }
    }
  };

  const handleTerminalFailure = (message: string) => {
    if (activeRun?.jobId !== jobId || resultLoaded) return;
    setError(message, snapshot);
    stopGenerationWatch();
  };

  const recoverFromResult = async (fallbackError: string) => {
    if (activeRun?.jobId !== jobId || resultLoaded) return;
    try {
      await finishWithResult();
      resultLoaded = true;
    } catch {
      setError(fallbackError, snapshot);
    } finally {
      if (activeRun?.jobId === jobId) {
        stopGenerationWatch();
      }
    }
  };

  streamProgress(jobId, {
    onStep: (s) =>
      addStep({
        agent: s.agent,
        startedAt: s.started_at,
        completedAt: s.completed_at,
        durationSeconds: s.duration_seconds,
        outputSummary: s.output_summary,
        error: s.error,
        retries: s.retries,
      }),
    onCurrentAgent: (a) => setCurrentAgent(a),
    onComplete: async (data) => {
      if (activeRun?.jobId !== jobId) return;
      if (data.status === "failed") {
        handleTerminalFailure(data.error || "Generering feilet");
        return;
      }
      await loadResultOnce(data.status);
    },
    onError: (err) => {
      void recoverFromResult(err);
    },
  });

  void watchGenerationJob(
    jobId,
    async (st: JobStatusResponse) => {
      if (activeRun?.jobId !== jobId) return;
      if (st.status === "failed") {
        handleTerminalFailure(st.error || "Generering feilet");
        return;
      }
      await loadResultOnce(st.status);
    },
    pollSignal,
    (msg) => {
      void recoverFromResult(msg);
    }
  );
}

/** POST /generate may return a terminal status for cache hits. */
export async function loadTerminalGeneration(
  jobId: string,
  status: string,
  snapshot: GenerationRequest,
  errorMessage?: string
): Promise<boolean> {
  if (!isTerminalGenerateStatus(status)) return false;
  if (status === "failed") {
    useAppStore.getState().setError(errorMessage || "Generering feilet", snapshot);
    return true;
  }
  stopGenerationWatch();
  try {
    const raw = await getResult(jobId);
    const mapped = mapApiResultToGenerationResult(raw, snapshot);
    useAppStore.getState().setResult(mapped);
    if (isSuccessfulStatus(mapped.status)) {
      appendHistory({
        jobId,
        createdAt: new Date().toISOString(),
        topic: snapshot.topic,
        grade: snapshot.grade,
        materialType: snapshot.materialType,
        favorite: false,
        request: { ...snapshot },
      });
    }
    return true;
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : "Kunne ikke hente resultat";
    useAppStore.getState().setError(msg, snapshot);
    return true;
  }
}
