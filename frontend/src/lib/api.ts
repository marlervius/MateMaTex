/**
 * API client for the MateMaTeX 2.0 backend.
 *
 * Covers: generation, exercises, editor, differentiation, export, sharing.
 * All authenticated requests include the Supabase JWT.
 */

import { createClient } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ---------------------------------------------------------------------------
// Auth helper
// ---------------------------------------------------------------------------
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const supabase = createClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (session?.access_token) {
      return {
        Authorization: `Bearer ${session.access_token}`,
        "Content-Type": "application/json",
      };
    }
  } catch {
    // Supabase not configured (local dev) — proceed without auth
  }

  return { "Content-Type": "application/json" };
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
  if (!res.ok) throw new Error(`Generation failed: ${res.statusText}`);
  return res.json();
}

export function streamProgress(
  jobId: string,
  callbacks: {
    onStep?: (step: any) => void;
    onCurrentAgent?: (agent: string) => void;
    onComplete?: (data: any) => void;
    onError?: (error: string) => void;
  }
): () => void {
  const eventSource = new EventSource(`${API_BASE}/generate/${jobId}/stream`);

  eventSource.addEventListener("step", (e) => {
    callbacks.onStep?.(JSON.parse(e.data));
  });
  eventSource.addEventListener("current_agent", (e) => {
    callbacks.onCurrentAgent?.(JSON.parse(e.data).agent);
  });
  eventSource.addEventListener("complete", (e) => {
    callbacks.onComplete?.(JSON.parse(e.data));
    eventSource.close();
  });
  eventSource.addEventListener("error", () => {
    callbacks.onError?.("Connection lost");
    eventSource.close();
  });

  return () => eventSource.close();
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
