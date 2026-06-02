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

  const status = String(api.status ?? "failed") as GenerationResult["status"];

  return {
    jobId: String(raw.job_id ?? ""),
    status,
    fullDocument: String(raw.full_document ?? ""),
    pdfUrl: String(raw.pdf_path ?? ""),
    pdfBase64: String(raw.pdf_base64 ?? ""),
    usedLatexFallback: Boolean(raw.used_latex_fallback),
    fromCache: Boolean(raw.from_cache),
    differentiatedBasic: String(raw.differentiated_basic ?? ""),
    differentiatedAdvanced: String(raw.differentiated_advanced ?? ""),
    warningReason: String(raw.warning_reason ?? ""),
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

export function isSuccessfulStatus(status: GenerationResult["status"]): boolean {
  return status === "completed" || status === "completed_with_warnings";
}

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

/** Human-readable explanation for a completed_with_warnings result. */
export function warningReasonLabel(reason: string): string {
  const parts = (reason || "").split(",").map((r) => r.trim()).filter(Boolean);
  const hasMath = parts.includes("math");
  const hasFallback = parts.includes("fallback");

  if (hasMath && hasFallback) {
    return "Noen figurer ble forenklet, og matematikken bør dobbeltsjekkes før bruk.";
  }
  if (hasFallback) {
    return "Avanserte figurer (f.eks. TikZ) ble fjernet for å få dokumentet til å kompilere. Tekst og oppgaver er beholdt.";
  }
  if (hasMath) {
    return "Noen utregninger kunne ikke verifiseres automatisk — kontroller matematikken før du deler.";
  }
  return "Materialet bør gjennomgås før det deles med elever.";
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
