/**
 * API client for the MateMaTeX 2.0 backend.
 *
 * Covers: generation, exercises, editor, differentiation, export, sharing.
 * - POST/DELETE/GET result: optional NEXT_PUBLIC_MATE_API_KEY (exposed in browser).
 * - SSE: default same-origin proxy `/api/generate/.../stream` uses server-only MATE_API_KEY.
 */

import type {
  StreamCompletePayload,
  StreamCurrentAgentPayload,
  StreamStepPayload,
} from "@/types/generation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** SSE URL: Next.js proxy (recommended) or direct backend with ?api_key= (discouraged). */
function getGenerationStreamUrl(jobId: string): string {
  if (typeof window === "undefined") return "";
  if (process.env.NEXT_PUBLIC_STREAM_PROXY === "false") {
    const u = new URL(`${API_BASE}/generate/${encodeURIComponent(jobId)}/stream`);
    const k = process.env.NEXT_PUBLIC_MATE_API_KEY;
    if (k) u.searchParams.set("api_key", k);
    return u.toString();
  }
  return `/api/generate/${encodeURIComponent(jobId)}/stream`;
}

// ---------------------------------------------------------------------------
// Auth helper (optional shared API key — must match backend MATE_API_KEY)
// ---------------------------------------------------------------------------
async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const key =
    typeof window !== "undefined"
      ? process.env.NEXT_PUBLIC_MATE_API_KEY
      : undefined;
  if (key) {
    headers["X-API-Key"] = key;
  }
  return headers;
}

async function readErrorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg || "").filter(Boolean).join("; ");
    }
  } catch {
    /* ignore */
  }
  return res.statusText || `HTTP ${res.status}`;
}

// ---------------------------------------------------------------------------
// Generation
// ---------------------------------------------------------------------------
export interface GenerateRequest {
  grade: string;
  topic: string;
  material_type: string;
  language_level: string;
  num_exercises: number;
  difficulty: string;
  include_theory: boolean;
  include_examples: boolean;
  include_exercises: boolean;
  include_solutions: boolean;
  include_graphs: boolean;
  competency_goals: string[];
  extra_instructions: string;
}

export interface GenerateResponse {
  job_id: string;
  status: string;
  message: string;
}

export async function startGeneration(
  request: GenerateRequest
): Promise<GenerateResponse> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const msg = await readErrorMessage(res);
    if (res.status === 401) {
      throw new Error(
        "Ingen tilgang (401). Sjekk at backend MATE_API_KEY matcher NEXT_PUBLIC_MATE_API_KEY, eller at nøkkel ikke er påkrevd."
      );
    }
    if (res.status === 429) {
      throw new Error(
        "Du har sendt mange forespørsler på kort tid (rate limit). Vent et minutt og prøv igjen. Ved skoleutrulling: be administrator om høyere grense eller felles nøkkel bak proxy."
      );
    }
    throw new Error(msg || `Generation failed: ${res.statusText}`);
  }
  return res.json();
}

export function streamProgress(
  jobId: string,
  callbacks: {
    onStep?: (step: StreamStepPayload) => void;
    onCurrentAgent?: (agent: string) => void;
    onComplete?: (data: StreamCompletePayload) => void;
    onError?: (error: string) => void;
  }
): () => void {
  const url = getGenerationStreamUrl(jobId);
  const eventSource = new EventSource(url);

  eventSource.addEventListener("step", (e: MessageEvent) => {
    callbacks.onStep?.(JSON.parse(e.data) as StreamStepPayload);
  });
  eventSource.addEventListener("current_agent", (e: MessageEvent) => {
    const p = JSON.parse(e.data) as StreamCurrentAgentPayload;
    callbacks.onCurrentAgent?.(p.agent);
  });
  eventSource.addEventListener("complete", (e: MessageEvent) => {
    const data = JSON.parse(e.data) as StreamCompletePayload;
    callbacks.onComplete?.(data);
    eventSource.close();
  });
  eventSource.addEventListener("error", (e: Event) => {
    // Definitive server error with a JSON payload
    if ("data" in e && (e as MessageEvent).data) {
      try {
        const j = JSON.parse((e as MessageEvent).data) as { message?: string };
        callbacks.onError?.(j.message || "Feil fra strømmen");
        eventSource.close();
        return;
      } catch {
        /* fall through */
      }
    }
    // readyState === CONNECTING means the browser is already attempting to
    // reconnect — let it; only report a permanent failure when CLOSED.
    if (eventSource.readyState === EventSource.CONNECTING) {
      return;
    }
    callbacks.onError?.(
      "Mistet kontakt under generering. Sjekk nettverk og at backend kjører. " +
        "Med API-nøkkel: sett MATE_API_KEY på Vercel (server) for SSE-proxy, eller NEXT_PUBLIC_STREAM_PROXY=false og NEXT_PUBLIC_MATE_API_KEY for direkte strøm."
    );
    eventSource.close();
  });

  return () => eventSource.close();
}

export async function abortGeneration(jobId: string): Promise<any> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/generate/${jobId}`, {
    method: "DELETE",
    headers,
  });
  if (!res.ok) throw new Error(`Failed to abort: ${res.statusText}`);
  return res.json();
}

export async function getResult(jobId: string): Promise<any> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/generate/${jobId}/result`, { headers });
  if (!res.ok) throw new Error(`Failed to get result: ${res.statusText}`);
  return res.json();
}

export async function estimateCost(request: GenerateRequest): Promise<any> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/estimate`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Editor — compile & AI actions
// ---------------------------------------------------------------------------
export async function compileLatex(
  latexBody: string,
  filename: string = "preview"
): Promise<{
  success: boolean;
  pdf_base64: string;
  errors: Array<{ line: number; message: string; severity: string }>;
  warnings: Array<{ line: number; message: string; severity: string }>;
  cached: boolean;
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/editor/compile`, {
    method: "POST",
    headers,
    body: JSON.stringify({ latex_body: latexBody, filename }),
  });
  return res.json();
}

export async function editorAction(
  action: "simplify" | "add-illustration" | "variant" | "add-hint",
  selection: string,
  fullContext: string = "",
  extra: string = ""
): Promise<{
  success: boolean;
  replacement_latex: string;
  explanation: string;
  error: string;
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/editor/${action}`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      latex_selection: selection,
      full_context: fullContext,
      extra_instructions: extra,
    }),
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Exercises
// ---------------------------------------------------------------------------
export interface Exercise {
  id: string;
  title: string;
  number: number;
  latex_content: string;
  solution: string;
  hints: string[];
  difficulty: string;
  exercise_type: string;
  keywords: string[];
  has_figure: boolean;
  sub_parts: string[];
  topic: string;
  grade_level: string;
  source_generation_id: string;
  times_used: number;
  user_rating: number | null;
  created_at: string;
}

export async function listExercises(params?: {
  topic?: string;
  grade_level?: string;
  exercise_type?: string;
  difficulty?: string;
  page?: number;
  page_size?: number;
}): Promise<{
  exercises: Exercise[];
  total: number;
  page: number;
  page_size: number;
}> {
  const headers = await getAuthHeaders();
  const sp = new URLSearchParams();
  if (params?.topic) sp.set("topic", params.topic);
  if (params?.grade_level) sp.set("grade_level", params.grade_level);
  if (params?.exercise_type) sp.set("exercise_type", params.exercise_type);
  if (params?.difficulty) sp.set("difficulty", params.difficulty);
  if (params?.page) sp.set("page", String(params.page));
  if (params?.page_size) sp.set("page_size", String(params.page_size));

  const res = await fetch(`${API_BASE}/exercises?${sp.toString()}`, {
    headers,
  });
  return res.json();
}

export async function searchExercises(
  query: string,
  limit: number = 20
): Promise<{ exercises: Exercise[]; total: number }> {
  const headers = await getAuthHeaders();
  const res = await fetch(
    `${API_BASE}/exercises/search?q=${encodeURIComponent(query)}&limit=${limit}`,
    { headers }
  );
  return res.json();
}

export async function ingestExercises(
  latexContent: string,
  topic: string = "",
  gradeLevel: string = "",
  generationId: string = ""
): Promise<{ ingested: number; exercise_ids: string[] }> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/exercises/ingest`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      latex_content: latexContent,
      topic,
      grade_level: gradeLevel,
      generation_id: generationId,
    }),
  });
  return res.json();
}

export async function findSimilarExercises(
  exerciseId: string,
  limit: number = 5
): Promise<Exercise[]> {
  const headers = await getAuthHeaders();
  const res = await fetch(
    `${API_BASE}/exercises/${exerciseId}/similar?limit=${limit}`,
    { headers }
  );
  return res.json();
}

export async function generateVariant(
  exerciseId: string,
  instructions: string = ""
): Promise<Exercise> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/exercises/${exerciseId}/variant`, {
    method: "POST",
    headers,
    body: JSON.stringify({ instructions }),
  });
  return res.json();
}

export async function exportExercises(
  exerciseIds: string[],
  format: "pdf" | "docx" = "pdf",
  includeSolutions: boolean = true,
  title: string = "Oppgaveark"
): Promise<{
  success: boolean;
  content_base64: string;
  filename: string;
  errors: string[];
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/exercises/export`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      exercise_ids: exerciseIds,
      format,
      include_solutions: includeSolutions,
      title,
    }),
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Differentiation
// ---------------------------------------------------------------------------
export async function differentiate(
  latexContent: string,
  topic: string = "",
  grade: string = ""
): Promise<{
  success: boolean;
  basic_latex: string;
  standard_latex: string;
  advanced_latex: string;
  basic_exercise_count: number;
  standard_exercise_count: number;
  advanced_exercise_count: number;
  errors: string[];
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/differentiation/generate`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      latex_content: latexContent,
      topic,
      grade,
    }),
  });
  return res.json();
}

export async function generateHints(
  exerciseId: string,
  exerciseLatex: string,
  solution: string = ""
): Promise<{
  success: boolean;
  hints: { nudge: string; step: string; near_solution: string };
  error: string;
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/exercises/${exerciseId}/hints`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      exercise_latex: exerciseLatex,
      solution,
    }),
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------
export async function exportPdf(params: {
  latex_content: string;
  include_solutions?: boolean;
  include_cover?: boolean;
  cover_school?: string;
  cover_teacher?: string;
  cover_subject?: string;
  cover_topic?: string;
  print_optimized?: boolean;
}): Promise<{
  success: boolean;
  content_base64: string;
  filename: string;
  mime_type: string;
  errors: string[];
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/export/pdf`, {
    method: "POST",
    headers,
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function exportDocx(
  latexContent: string,
  title: string = "Oppgaveark",
  includeSolutions: boolean = true
): Promise<{
  success: boolean;
  content_base64: string;
  filename: string;
  mime_type: string;
  errors: string[];
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/export/docx`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      latex_content: latexContent,
      title,
      include_solutions: includeSolutions,
    }),
  });
  return res.json();
}

export async function exportPptx(
  latexContent: string,
  title: string = "Matematikk",
  solutionsAs: "speaker_notes" | "hidden_slides" = "speaker_notes"
): Promise<{
  success: boolean;
  content_base64: string;
  filename: string;
  mime_type: string;
  errors: string[];
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/export/pptx`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      latex_content: latexContent,
      title,
      solutions_as: solutionsAs,
    }),
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Sharing
// ---------------------------------------------------------------------------
export async function createShare(params: {
  resource_type: string;
  resource_id: string;
  password?: string;
  expires_hours?: number;
  max_views?: number;
}): Promise<{
  success: boolean;
  token: string;
  share_url: string;
  expires_at: string | null;
}> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/sharing`, {
    method: "POST",
    headers,
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function getShared(
  token: string,
  password?: string
): Promise<{
  success: boolean;
  resource_type: string;
  content: any;
  allow_download: boolean;
  allow_clone: boolean;
}> {
  const url = password
    ? `${API_BASE}/sharing/${token}?password=${encodeURIComponent(password)}`
    : `${API_BASE}/sharing/${token}`;
  const res = await fetch(url);
  return res.json();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
export function downloadBase64(
  base64: string,
  filename: string,
  mimeType: string = "application/octet-stream"
) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
