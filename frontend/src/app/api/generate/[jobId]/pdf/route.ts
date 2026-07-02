import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function requireServerApiKey(): Response | null {
  const key = process.env.MATE_API_KEY?.trim();
  if (key) return null;
  if (process.env.NODE_ENV === "production") {
    return new Response(
      JSON.stringify({ detail: "Server mangler MATE_API_KEY-konfigurasjon" }),
      { status: 503, headers: { "Content-Type": "application/json" } },
    );
  }
  return null;
}

/**
 * Proxies job PDF download so the browser never needs MATE_API_KEY.
 */
export async function GET(
  req: NextRequest,
  context: { params: Promise<{ jobId: string }> | { jobId: string } },
) {
  const blocked = requireServerApiKey();
  if (blocked) return blocked;

  const { jobId } = await Promise.resolve(context.params);
  const clientUserId = req.nextUrl.searchParams.get("client_user_id")?.trim() || "";
  const backend = (
    process.env.BACKEND_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");

  const headers: Record<string, string> = {
    "X-API-Key": process.env.MATE_API_KEY!.trim(),
  };
  if (clientUserId) {
    headers["X-Client-User-Id"] = clientUserId;
  }

  const pdfQs = clientUserId
    ? `?client_user_id=${encodeURIComponent(clientUserId)}`
    : "";
  const url = `${backend}/generate/${encodeURIComponent(jobId)}/pdf${pdfQs}`;
  const upstream = await fetch(url, { headers, cache: "no-store" });

  if (!upstream.ok) {
    const text = await upstream.text().catch(() => "");
    return new Response(text || `Upstream ${upstream.status}`, {
      status: upstream.status,
    });
  }

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": upstream.headers.get("content-type") || "application/pdf",
      "Cache-Control": "private, max-age=0, must-revalidate",
    },
  });
}
