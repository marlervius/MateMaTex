import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function backendBase(): string {
  return (
    process.env.BACKEND_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  ).replace(/\/$/, "");
}

async function proxyRequest(req: NextRequest, pathSegments: string[]) {
  const path = pathSegments.join("/");
  const search = req.nextUrl.search;
  const url = `${backendBase()}/${path}${search}`;

  const headers = new Headers();
  const key = process.env.MATE_API_KEY?.trim();
  if (key) {
    headers.set("X-API-Key", key);
  }
  const contentType = req.headers.get("content-type");
  if (contentType) {
    headers.set("Content-Type", contentType);
  }
  const accept = req.headers.get("accept");
  if (accept) {
    headers.set("Accept", accept);
  }

  const init: RequestInit = {
    method: req.method,
    headers,
    cache: "no-store",
  };

  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = await req.arrayBuffer();
  }

  const upstream = await fetch(url, init);
  const responseHeaders = new Headers();
  const upstreamType = upstream.headers.get("content-type");
  if (upstreamType) {
    responseHeaders.set("Content-Type", upstreamType);
  }
  const disposition = upstream.headers.get("content-disposition");
  if (disposition) {
    responseHeaders.set("Content-Disposition", disposition);
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

type RouteContext = {
  params: Promise<{ path: string[] }> | { path: string[] };
};

async function resolvePath(context: RouteContext): Promise<string[]> {
  const params = await Promise.resolve(context.params);
  return params.path;
}

export async function GET(req: NextRequest, context: RouteContext) {
  return proxyRequest(req, await resolvePath(context));
}

export async function POST(req: NextRequest, context: RouteContext) {
  return proxyRequest(req, await resolvePath(context));
}

export async function PUT(req: NextRequest, context: RouteContext) {
  return proxyRequest(req, await resolvePath(context));
}

export async function PATCH(req: NextRequest, context: RouteContext) {
  return proxyRequest(req, await resolvePath(context));
}

export async function DELETE(req: NextRequest, context: RouteContext) {
  return proxyRequest(req, await resolvePath(context));
}
