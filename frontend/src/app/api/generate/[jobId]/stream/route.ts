import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export const maxDuration = 300; // 5 min — generation can take 3-4 min on Render free tier

/**
 * Proxies SSE from the FastAPI backend so the browser never needs MATE_API_KEY.
 * Set BACKEND_INTERNAL_URL on Vercel if the API URL must differ from NEXT_PUBLIC_API_URL.
 */
export async function GET(
  _req: NextRequest,
  context: { params: Promise<{ jobId: string }> | { jobId: string } },
) {
  const params = await Promise.resolve(context.params);
  const jobId = params.jobId;
  const backend = (
    process.env.BACKEND_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");

  const key = process.env.MATE_API_KEY?.trim() || "";
  const headers: Record<string, string> = {
    Accept: "text/event-stream",
  };
  if (key) {
    headers["X-API-Key"] = key;
  }

  const url = `${backend}/generate/${encodeURIComponent(jobId)}/stream`;
  let upstream: Response;
  try {
    upstream = await fetch(url, {
      headers,
      cache: "no-store",
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "fetch failed";
    return new Response(`Upstream unreachable: ${msg}`, { status: 502 });
  }

  if (!upstream.ok || !upstream.body) {
    const text = await upstream.text().catch(() => "");
    return new Response(text || `Upstream ${upstream.status}`, {
      status: upstream.status === 401 ? 401 : 502,
    });
  }

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
