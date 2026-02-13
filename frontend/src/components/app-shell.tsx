"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/sidebar";
import { CommandPalette } from "@/components/command-palette";

const PAGE_TITLES: Record<string, string> = {
  "/": "Generer",
  "/exercises": "Oppgavebank",
  "/templates": "Maler",
  "/history": "Historikk",
  "/school": "Skolens bank",
  "/shared": "Delt med meg",
  "/settings": "Innstillinger",
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [cmdOpen, setCmdOpen] = useState(false);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Cmd+K — Command palette
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCmdOpen((o) => !o);
      }
      // Cmd+N — New generation
      if ((e.metaKey || e.ctrlKey) && e.key === "n") {
        e.preventDefault();
        window.location.href = "/";
      }
      // Escape — Close modals
      if (e.key === "Escape") {
        setCmdOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Get breadcrumb from path
  const pageTitle = PAGE_TITLES[pathname] || "";

  return (
    <div className="min-h-screen flex">
      {/* Sidebar (desktop) */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* Mobile bottom bar */}
      <MobileBottomBar pathname={pathname} />

      {/* Main content area */}
      <div className="flex-1 md:ml-sidebar-collapsed lg:ml-sidebar min-w-0">
        {/* Top bar */}
        {pageTitle && (
          <header className="sticky top-0 z-30 bg-bg/80 backdrop-blur-md border-b border-border">
            <div className="max-w-content mx-auto px-6 h-14 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <h1 className="text-sm font-medium text-text-primary">
                  {pageTitle}
                </h1>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCmdOpen(true)}
                  className="hidden md:flex items-center gap-2 px-3 py-1.5 text-xs text-text-muted border border-border rounded-lg hover:border-text-muted transition-colors"
                >
                  <span>Kommandoer</span>
                  <kbd className="px-1.5 py-0.5 text-[10px] bg-surface-elevated rounded font-mono">
                    ⌘K
                  </kbd>
                </button>
              </div>
            </div>
          </header>
        )}

        {/* Page content */}
        <main className="max-w-content mx-auto px-6 py-8">
          {children}
        </main>
      </div>

      {/* Command palette overlay */}
      <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} />
    </div>
  );
}

/* -----------------------------------------------------------------------
   Mobile bottom tab bar (< 768px)
   ----------------------------------------------------------------------- */
function MobileBottomBar({ pathname }: { pathname: string }) {
  const tabs = [
    { href: "/", label: "Generer", icon: "✦" },
    { href: "/exercises", label: "Bank", icon: "📚" },
    { href: "/history", label: "Historikk", icon: "🕐" },
    { href: "/settings", label: "Mer", icon: "⚙" },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface border-t border-border safe-area-inset-bottom">
      <div className="flex">
        {tabs.map((tab) => {
          const active = pathname === tab.href;
          return (
            <a
              key={tab.href}
              href={tab.href}
              className={`flex-1 flex flex-col items-center gap-0.5 py-2 text-[10px] transition-colors ${
                active ? "text-accent-blue" : "text-text-muted"
              }`}
            >
              <span className="text-lg">{tab.icon}</span>
              <span>{tab.label}</span>
            </a>
          );
        })}
      </div>
    </nav>
  );
}
