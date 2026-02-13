import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const error = requestUrl.searchParams.get("error");

  // Handle error from Supabase (e.g. expired link)
  if (error) {
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(error)}`, request.url)
    );
  }

  if (!code) {
    return NextResponse.redirect(
      new URL("/login?error=missing_code", request.url)
    );
  }

  try {
    const cookieStore = cookies();

    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll();
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          },
        },
      }
    );

    const { error: sessionError } =
      await supabase.auth.exchangeCodeForSession(code);

    if (sessionError) {
      return NextResponse.redirect(
        new URL(
          `/login?error=${encodeURIComponent(sessionError.message)}`,
          request.url
        )
      );
    }
  } catch {
    return NextResponse.redirect(
      new URL("/login?error=callback_failed", request.url)
    );
  }

  // Redirect to home after successful email confirmation
  return NextResponse.redirect(new URL("/", request.url));
}
