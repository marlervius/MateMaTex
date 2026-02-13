"use client";

import { usePathname } from "next/navigation";
import { AppShell } from "@/components/app-shell";

/**
 * Wraps children in AppShell only for authenticated pages.
 * Login, register, auth callback, and shared pages render without the shell.
 */
export function ConditionalShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const publicPaths = ["/login", "/register", "/auth"];
  const isPublic = publicPaths.some((p) => pathname.startsWith(p));

  // Shared pages also bypass the shell (they're publicly accessible)
  const isShared = pathname.startsWith("/shared");

  if (isPublic || isShared) {
    return <>{children}</>;
  }

  return <AppShell>{children}</AppShell>;
}
