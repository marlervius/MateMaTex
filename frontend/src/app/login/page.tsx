"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { LogIn, Mail, Lock, AlertCircle } from "lucide-react";
import { createClient } from "@/lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Show error from auth callback redirect
  useEffect(() => {
    const callbackError = searchParams.get("error");
    if (callbackError) {
      const messages: Record<string, string> = {
        missing_code: "Ugyldig bekreftelseslenke",
        callback_failed: "Noe gikk galt ved bekreftelse. Prøv igjen.",
      };
      setError(messages[callbackError] || callbackError);
    }
  }, [searchParams]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const supabase = createClient();
      const { error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) {
        setError(
          authError.message === "Invalid login credentials"
            ? "Feil e-post eller passord"
            : authError.message
        );
        return;
      }

      router.push("/");
      router.refresh();
    } catch {
      setError("Noe gikk galt. Prøv igjen.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="font-display text-4xl text-text-primary mb-2">
            MateMaTeX
          </h1>
          <p className="text-text-secondary text-sm">
            AI-drevet matematikkverksted for norske lærere
          </p>
        </div>

        {/* Card */}
        <div className="card p-8">
          <h2 className="font-display text-2xl text-text-primary mb-6 text-center">
            Logg inn
          </h2>

          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="flex items-center gap-2 p-3 rounded-xl bg-[hsl(var(--accent-red)/0.1)] text-[hsl(var(--accent-red))] text-sm"
              >
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </motion.div>
            )}

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-text-secondary mb-1.5"
              >
                E-post
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="din@epost.no"
                  className="input pl-10 w-full"
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-text-secondary mb-1.5"
              >
                Passord
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="input pl-10 w-full"
                  autoComplete="current-password"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn w-full flex items-center justify-center gap-2 bg-[hsl(var(--accent-blue))] text-white hover:opacity-90 disabled:opacity-50 py-3"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <LogIn className="w-4 h-4" />
              )}
              {loading ? "Logger inn..." : "Logg inn"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-text-secondary">
              Har du ikke en konto?{" "}
              <Link
                href="/register"
                className="text-[hsl(var(--accent-blue))] hover:underline font-medium"
              >
                Opprett konto
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
