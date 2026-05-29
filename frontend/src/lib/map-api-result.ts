import type { GenerationResultApi } from "@/lib/api";
import type { GenerationRequest, GenerationResult, MathClaimDetail } from "@/lib/store";

function mapClaims(raw: unknown[]): MathClaimDetail[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((c: any) => ({
    claimId: c.claim_id ?? c.claimId ?? "",
    latexExpression: c.latex_expression ?? c.latexExpression ?? "",
    claimType: c.claim_type ?? c.claimType ?? "",
    context: c.context ?? "",
    isCorrect: c.is_correct ?? c.isCorrect ?? null,
    errorMessage: c.error_message ?? c.errorMessage ?? "",
    expectedResult: c.expected_result ?? c.expectedResult ?? "",
    actualResult: c.actual_result ?? c.actualResult ?? "",
  }));
}

/**
 * Mapper backend GET /generate/{id}/result til frontend-modell.
 */
export function mapApiResultToGenerationResult(
  api: GenerationResultApi | Record<string, unknown>,
  generationMeta?: GenerationRequest
): GenerationResult {
  const raw = api as Record<string, unknown>;
  const mv = (raw.math_verification ?? {}) as Record<string, unknown>;
  const incorrect = mapClaims((mv.errors as unknown[]) ?? []);
  const unparseable = mapClaims((mv.unparseable_claims as unknown[]) ?? []);

  const stepsRaw = (raw.steps as unknown[]) ?? [];
  const steps = stepsRaw.map((s: any) => ({
    agent: String(s.agent ?? ""),
    startedAt: s.started_at ?? s.startedAt ?? "",
    completedAt: s.completed_at ?? s.completedAt ?? null,
    durationSeconds: Number(s.duration_seconds ?? s.durationSeconds ?? 0),
    outputSummary: s.output_summary ?? s.outputSummary ?? "",
    error: s.error ?? "",
    retries: Number(s.retries ?? 0),
  }));

  const latex = (raw.latex_compilation ?? {}) as Record<string, unknown>;

  return {
    jobId: String(raw.job_id ?? ""),
    status: raw.status as GenerationResult["status"],
    fullDocument: String(raw.full_document ?? ""),
    pdfUrl: String(raw.pdf_path ?? ""),
    steps,
    mathVerification: {
      claimsChecked: Number(mv.claims_checked ?? 0),
      claimsCorrect: Number(mv.claims_correct ?? 0),
      claimsIncorrect: Number(mv.claims_incorrect ?? 0),
      claimsUnparseable: Number(mv.claims_unparseable ?? 0),
      allCorrect: Boolean(mv.all_correct),
      summary: String(mv.summary ?? ""),
      incorrectClaims: incorrect,
      unparseableClaims: unparseable,
    },
    latexCompiled: Boolean(latex.success),
    totalDuration: Number(raw.total_duration_seconds ?? 0),
    error: String(raw.error ?? ""),
    generationMeta,
    errorCategory: categorizeError(
      String(raw.error ?? ""),
      Boolean(latex.success),
      raw.status === "failed"
    ),
  };
}

export type ErrorCategory = "aborted" | "latex" | "model" | "unknown";

export function categorizeError(
  errorMessage: string,
  latexCompiled: boolean,
  failed: boolean
): ErrorCategory {
  if (!failed) return "unknown";
  const m = errorMessage.toLowerCase();
  if (m.includes("avbrutt")) return "aborted";
  if (
    m.includes("latex") ||
    m.includes("kompiler") ||
    m.includes("pdflatex") ||
    m.includes("compile")
  ) {
    return "latex";
  }
  if (
    !latexCompiled &&
    (m.includes("pdf") || m.includes("dokument") || m.includes("figur"))
  ) {
    return "latex";
  }
  if (errorMessage) return "model";
  return "unknown";
}

export function errorCategoryLabel(cat: ErrorCategory): string {
  switch (cat) {
    case "aborted":
      return "Avbrutt av bruker";
    case "latex":
      return "LaTeX-kompilering";
    case "model":
      return "Generering / modell";
    default:
      return "Ukjent";
  }
}
