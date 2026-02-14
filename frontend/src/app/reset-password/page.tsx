"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Mail, ArrowLeft, CheckCircle, AlertCircle } from "lucide-react";
import { createClient } from "@/lib/supabase";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const supabase = createClient();
      const { error: resetError } = await supabase.auth.resetPasswordForEmail(
        email,
        {
          redirectTo: `${window.location.origin}/update-password`,
        }
      );

      if (resetError) {
        setError(resetError.message);
        return;
      }

      setSent(true);
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
        <div className="text-center mb-8">
          <h1 className="font-display text-4xl text-text-primary mb-2">
            MateMaTeX
          </h1>
        </div>

        <div className="card p-8">
          {sent ? (
            <div className="text-center space-y-4">
              <CheckCircle className="w-12 h-12 text-[hsl(var(--accent-green))] mx-auto" />
              <h2 className="font-display text-2xl text-text-primary">
                E-post sendt
              </h2>
              <p className="text-text-secondary text-sm">
                Vi har sendt en lenke til <strong>{email}</strong> for å
                tilbakestille passordet ditt. Sjekk innboksen din (og
                søppelpost).
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-[hsl(var(--accent-blue))] hover:underline font-medium text-sm mt-4"
              >
                <ArrowLeft className="w-4 h-4" />
                Tilbake til innlogging
              </Link>
            </div>
          ) : (
            <>
              <h2 className="font-display text-2xl text-text-primary mb-2 text-center">
                Glemt passord?
              </h2>
              <p className="text-text-secondary text-sm text-center mb-6">
                Skriv inn e-postadressen din, så sender vi deg en lenke for å
                tilbakestille passordet.
              </p>

              <form onSubmit={handleReset} className="space-y-4">
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

                <button
                  type="submit"
                  disabled={loading}
                  className="btn w-full flex items-center justify-center gap-2 bg-[hsl(var(--accent-blue))] text-white hover:opacity-90 disabled:opacity-50 py-3"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <Mail className="w-4 h-4" />
                  )}
                  {loading ? "Sender..." : "Send tilbakestillingslenke"}
                </button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 text-[hsl(var(--accent-blue))] hover:underline font-medium text-sm"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Tilbake til innlogging
                </Link>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}
