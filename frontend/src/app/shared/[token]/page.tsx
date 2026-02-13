"use client";

import { useState, useEffect } from "react";
import { Lock, AlertTriangle, Download, Copy, FileText } from "lucide-react";
import { getShared } from "@/lib/api";

export default function SharedResourcePage({
  params,
}: {
  params: { token: string };
}) {
  const [resource, setResource] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [needsPassword, setNeedsPassword] = useState(false);
  const [password, setPassword] = useState("");

  const loadResource = async (pwd?: string) => {
    setLoading(true);
    setError("");
    try {
      const res = await getShared(params.token, pwd);
      if (res.success) {
        setResource(res);
        setNeedsPassword(false);
      } else {
        setError("Kunne ikke laste ressursen.");
      }
    } catch (e: any) {
      if (e.message?.includes("401") || e.message?.includes("Password")) {
        setNeedsPassword(true);
      } else if (e.message?.includes("410")) {
        setError("Denne delingen har utløpt.");
      } else if (e.message?.includes("404")) {
        setError("Delt lenke ikke funnet.");
      } else {
        setError(e.message || "Noe gikk galt.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResource();
  }, [params.token]);

  if (needsPassword) {
    return (
      <div className="max-w-sm mx-auto py-20 text-center">
        <Lock size={32} className="mx-auto mb-4 text-text-muted opacity-40" />
        <h1 className="font-display text-xl mb-2">Passordbeskyttet</h1>
        <p className="text-sm text-text-secondary mb-6">
          Denne ressursen krever passord.
        </p>
        <form onSubmit={(e) => { e.preventDefault(); loadResource(password); }} className="space-y-3">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Skriv inn passord..."
            className="input text-center"
            autoFocus
          />
          <button type="submit" className="btn-primary w-full">Åpne</button>
        </form>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-2 border-accent-blue border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-sm mx-auto py-20 text-center">
        <AlertTriangle size={32} className="mx-auto mb-4 text-accent-red opacity-60" />
        <h1 className="font-display text-xl mb-2">Feil</h1>
        <p className="text-sm text-text-secondary">{error}</p>
      </div>
    );
  }

  if (!resource) return null;

  return (
    <div className="max-w-reading mx-auto">
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold flex items-center gap-2">
              <FileText size={18} className="text-text-muted" />
              Delt ressurs
            </h1>
            <p className="text-sm text-text-secondary mt-1">
              Type: {resource.resource_type}
            </p>
          </div>
          <div className="flex gap-2">
            {resource.allow_download && (
              <button className="btn-primary">
                <Download size={14} /> Last ned
              </button>
            )}
            {resource.allow_clone && (
              <button className="btn-secondary">
                <Copy size={14} /> Klon
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-sm font-medium mb-3">Innhold</h2>
        {resource.content?.latex_body ? (
          <pre className="bg-bg rounded-lg p-4 text-xs font-mono text-text-secondary overflow-x-auto max-h-[60vh] overflow-y-auto">
            {resource.content.latex_body}
          </pre>
        ) : (
          <div className="text-center py-8 text-text-muted text-sm">
            Forhåndsvisning ikke tilgjengelig
          </div>
        )}
      </div>
    </div>
  );
}
