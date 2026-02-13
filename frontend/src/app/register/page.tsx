"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { UserPlus, Mail, Lock, User, AlertCircle, CheckCircle } from "lucide-react";
import { createClient } from "@/lib/supabase";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passordene stemmer ikke overens");
      return;
    }

    if (password.length < 6) {
      setError("Passordet må være minst 6 tegn");
      return;
    }

    setLoading(true);

    try {
      const supabase = createClient();
      const { error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (authError) {
        setError(authError.message);
        return;
      }

      setSuccess(true);
    } catch {
      setError("Noe gikk galt. Prøv igjen.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md card p-8 text-center"
        >
          <CheckCircle className="w-12 h-12 text-[hsl(var(--accent-green))] mx-auto mb-4" />
          <h2 className="font-display text-2xl text-text-primary mb-2">
            Konto opprettet!
          </h2>
          <p className="text-text-secondary mb-6">
            Vi har sendt en bekreftelseslenke til <strong>{email}</strong>.
            Sjekk innboksen din og klikk lenken for å aktivere kontoen.
          </p>
          <Link
            href="/login"
            className="btn bg-[hsl(var(--accent-blue))] text-white hover:opacity-90 inline-flex items-center gap-2"
          >
            Gå til innlogging
          </Link>
        </motion.div>
      </div>
    );
  }

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
            Opprett din konto og kom i gang
          </p>
        </div>

        {/* Card */}
        <div className="card p-8">
          <h2 className="font-display text-2xl text-text-primary mb-6 text-center">
            Opprett konto
          </h2>

          <form onSubmit={handleRegister} className="space-y-4">
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
                htmlFor="fullName"
                className="block text-sm font-medium text-text-secondary mb-1.5"
              >
                Fullt navn
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  placeholder="Kari Nordmann"
                  className="input pl-10 w-full"
                  autoComplete="name"
                />
              </div>
            </div>

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
                  placeholder="Minst 6 tegn"
                  className="input pl-10 w-full"
                  autoComplete="new-password"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-text-secondary mb-1.5"
              >
                Bekreft passord
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  placeholder="Skriv passordet igjen"
                  className="input pl-10 w-full"
                  autoComplete="new-password"
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
                <UserPlus className="w-4 h-4" />
              )}
              {loading ? "Oppretter konto..." : "Opprett konto"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-text-secondary">
              Har du allerede en konto?{" "}
              <Link
                href="/login"
                className="text-[hsl(var(--accent-blue))] hover:underline font-medium"
              >
                Logg inn
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
