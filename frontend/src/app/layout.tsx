import type { Metadata } from "next";
import { DM_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ConditionalShell } from "@/components/conditional-shell";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "MateMaTeX — LK20-matte med verifisert fasit",
  description:
    "LK20-tilpassede matteoppgaver og prøver for norske VGS-lærere. SymPy-verifisert fasit. Ingen elevdata.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="no"
      className={`dark ${dmSans.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <body className="font-sans antialiased bg-bg text-text-primary">
        {/* Theme init script — avoids flash */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var stored = localStorage.getItem('theme');
                  if (stored === 'light') {
                    document.documentElement.classList.remove('dark');
                  } else if (!stored && window.matchMedia('(prefers-color-scheme: light)').matches) {
                    document.documentElement.classList.remove('dark');
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
        <ConditionalShell>{children}</ConditionalShell>
      </body>
    </html>
  );
}
