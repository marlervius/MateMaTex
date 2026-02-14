"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Lock, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";
import { createClient } from "@/lib/supabase";

export default function UpdatePasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Supabase sends recovery tokens as hash fragments (#access_token=...&type=recovery)
    // The Supabase client automatically picks these up and sets the session.
    // We just need to verify there's a session with type=recovery.
    const supabase = createClient();

    supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        setReady(true);
      }
    });

    // Also check if we already have a session (page might have loaded after the event)
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setReady(true);
      }
    });

    // Give it a moment to process the hash fragment
    const timeout = setTimeout(() => {
      setReady(true);
    }, 2000);

    return () => clearTimeout(timeout);
  }, []);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password.length < 6) {
      setError("Passordet må være minst 6 tegn.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passordene er ikke like.");
      return;
    }

    setLoading(true);

    try {
      const supabase = createClient();
      const { error: updateError } = await supabase.auth.updateUser({
        password,
      });

      if (updateError) {
        setError(updateError.message);
        return;
      }

      setSuccess(true);

      // Redirect to home after 3 seconds
      setTimeout(() => {
        router.push("/");
        router.refresh();
      }, 3000);
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
          {success ? (
            <div className="text-center space-y-4">
              <CheckCircle className="w-12 h-12 text-[hsl(var(--accent-green))] mx-auto" />
              <h2 className="font-display text-2xl text-text-primary">
                Passord oppdatert!
              </h2>
              <p className="text-text-secondary text-sm">
                Passordet ditt er endret. Du blir sendt videre om et øyeblikk...
              </p>
            </div>
          ) : (
            <>
              <h2 className="font-display text-2xl text-text-primary mb-2 text-center">
                Nytt passord
              </h2>
              <p className="text-text-secondary text-sm text-center mb-6">
                Velg et nytt passord for kontoen din.
              </p>

              <form onSubmit={handleUpdate} className="space-y-4">
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
                    htmlFor="password"
                    className="block text-sm font-medium text-text-secondary mb-1.5"
                  >
                    Nytt passord
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                    <input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Minst 6 tegn"
                      className="input pl-10 w-full"
                      autoComplete="new-password"
                      minLength={6}
                    />
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="confirm-password"
                    className="block text-sm font-medium text-text-secondary mb-1.5"
                  >
                    Bekreft passord
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                    <input
                      id="confirm-password"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      placeholder="Skriv passordet på nytt"
                      className="input pl-10 w-full"
                      autoComplete="new-password"
                      minLength={6}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading || !ready}
                  className="btn w-full flex items-center justify-center gap-2 bg-[hsl(var(--accent-blue))] text-white hover:opacity-90 disabled:opacity-50 py-3"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <Lock className="w-4 h-4" />
                  )}
                  {loading ? "Oppdaterer..." : "Oppdater passord"}
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
