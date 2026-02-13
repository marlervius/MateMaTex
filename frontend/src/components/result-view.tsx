"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Download,
  Pencil,
  Layers,
  Share2,
  Star,
  ChevronDown,
  FileText,
  FileSpreadsheet,
  Presentation,
  Printer,
  CheckCircle2,
  XCircle,
  Clock,
  Cpu,
  Plus,
} from "lucide-react";
import { useAppStore } from "@/lib/store";
import {
  exportPdf,
  exportDocx,
  exportPptx,
  downloadBase64,
  ingestExercises,
  differentiate,
} from "@/lib/api";

type Tab = "document" | "editor" | "differentiation";

export function ResultView() {
  const { result } = useAppStore();
  const store = useAppStore();
  const [activeTab, setActiveTab] = useState<Tab>("document");
  const [showLatex, setShowLatex] = useState(false);
  const [showDownloads, setShowDownloads] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  // Differentiation
  const [diffData, setDiffData] = useState<any>(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [activeLevel, setActiveLevel] = useState<"basic" | "standard" | "advanced">("standard");

  // Export
  const [exportLoading, setExportLoading] = useState("");
  const [ingestStatus, setIngestStatus] = useState("");

  if (!result) return null;
  const isSuccess = result.status === "completed";

  /* ---- Export handlers ---- */
  const handleExport = async (format: string) => {
    setExportLoading(format);
    try {
      if (format === "pdf" || format === "pdf-print") {
        const res = await exportPdf({
          latex_content: result.fullDocument,
          print_optimized: format === "pdf-print",
        });
        if (res.success) downloadBase64(res.content_base64, res.filename, res.mime_type);
      } else if (format === "docx") {
        const res = await exportDocx(result.fullDocument);
        if (res.success) downloadBase64(res.content_base64, res.filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
      } else if (format === "pptx") {
        const res = await exportPptx(result.fullDocument);
        if (res.success) downloadBase64(res.content_base64, res.filename, "application/vnd.openxmlformats-officedocument.presentationml.presentation");
      }
    } finally {
      setExportLoading("");
      setShowDownloads(false);
    }
  };

  const handleDifferentiate = async () => {
    setDiffLoading(true);
    setActiveTab("differentiation");
    try {
      const res = await differentiate(result.fullDocument);
      if (res.success) setDiffData(res);
    } finally {
      setDiffLoading(false);
    }
  };

  const handleIngest = async () => {
    setIngestStatus("loading");
    try {
      const res = await ingestExercises(result.fullDocument);
      setIngestStatus(`${res.ingested} oppgaver lagret`);
    } catch {
      setIngestStatus("Feil");
    }
  };

  return (
    <div className="max-w-content mx-auto pb-24">
      {/* Status banner */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`card mb-6 ${
          isSuccess
            ? "!border-accent-green/30 bg-accent-green/5"
            : "!border-accent-red/30 bg-accent-red/5"
        }`}
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              {isSuccess ? (
                <CheckCircle2 size={20} className="text-accent-green" />
              ) : (
                <XCircle size={20} className="text-accent-red" />
              )}
              {isSuccess ? "Materiale generert" : "Generering feilet"}
            </h2>
            <p className="text-sm text-text-secondary mt-1">
              {isSuccess
                ? `Ferdig på ${result.totalDuration.toFixed(1)} sekunder`
                : result.error}
            </p>
          </div>
          <button
            onClick={() => {
              store.setResult(null as any);
              store.resetRequest();
            }}
            className="btn-ghost"
          >
            <Plus size={16} className="rotate-45" />
            Ny generering
          </button>
        </div>
      </motion.div>

      {isSuccess && (
        <>
          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <StatCard
              icon={<CheckCircle2 size={16} />}
              label="Matte-sjekk"
              value={result.mathVerification.allCorrect ? "Alt korrekt" : `${result.mathVerification.claimsCorrect}/${result.mathVerification.claimsChecked}`}
              color={result.mathVerification.allCorrect ? "green" : "orange"}
            />
            <StatCard
              icon={<FileText size={16} />}
              label="LaTeX"
              value={result.latexCompiled ? "Kompilert" : "Feil"}
              color={result.latexCompiled ? "green" : "red"}
            />
            <StatCard
              icon={<Cpu size={16} />}
              label="Agenter"
              value={`${result.steps.length} steg`}
              color="blue"
            />
            <StatCard
              icon={<Clock size={16} />}
              label="Tid"
              value={`${result.totalDuration.toFixed(1)}s`}
              color="purple"
            />
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-1 border-b border-border mb-6">
            {([
              { id: "document" as Tab, label: "Dokument" },
              { id: "editor" as Tab, label: "Rediger" },
              { id: "differentiation" as Tab, label: "Differensiering" },
            ]).map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  if (tab.id === "differentiation" && !diffData && !diffLoading) {
                    handleDifferentiate();
                  } else {
                    setActiveTab(tab.id);
                  }
                }}
                className={`relative px-4 py-2.5 text-sm transition-colors ${
                  activeTab === tab.id
                    ? "text-accent-blue"
                    : "text-text-muted hover:text-text-secondary"
                }`}
              >
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-blue rounded-full"
                  />
                )}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <AnimatePresence mode="wait">
            {activeTab === "document" && (
              <motion.div
                key="doc"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {/* PDF Preview */}
                <div className="card !p-0 overflow-hidden">
                  <div className="bg-surface-elevated p-8 text-center min-h-[400px] flex items-center justify-center">
                    <div className="text-text-muted">
                      <FileText size={48} className="mx-auto mb-3 opacity-30" />
                      <p className="text-sm">
                        {result.latexCompiled
                          ? "PDF-forhåndsvisning"
                          : "PDF kunne ikke genereres"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* LaTeX source (collapsible) */}
                <div className="card">
                  <button
                    onClick={() => setShowLatex(!showLatex)}
                    className="flex items-center justify-between w-full"
                  >
                    <span className="text-sm font-medium">LaTeX-kilde</span>
                    <motion.span
                      animate={{ rotate: showLatex ? 180 : 0 }}
                      className="text-text-muted"
                    >
                      <ChevronDown size={16} />
                    </motion.span>
                  </button>
                  <AnimatePresence>
                    {showLatex && (
                      <motion.pre
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 bg-bg rounded-lg p-4 text-xs font-mono text-text-secondary overflow-x-auto max-h-96 overflow-y-auto"
                      >
                        {result.fullDocument}
                      </motion.pre>
                    )}
                  </AnimatePresence>
                </div>

                {/* Pipeline details */}
                <div className="card">
                  <h3 className="text-sm font-medium mb-3">Pipeline-detaljer</h3>
                  <div className="space-y-1">
                    {result.steps.map((step: any, i: number) => (
                      <div
                        key={i}
                        className="flex items-center justify-between text-sm py-2 border-b border-border last:border-0"
                      >
                        <span className="text-text-secondary">{step.agent}</span>
                        <div className="flex items-center gap-3 text-xs text-text-muted">
                          {step.error && (
                            <span className="text-accent-red">{step.error}</span>
                          )}
                          <span>{step.duration_seconds?.toFixed(1)}s</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === "editor" && (
              <motion.div
                key="edit"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="card text-center py-12">
                  <Pencil size={32} className="mx-auto mb-3 text-text-muted opacity-50" />
                  <p className="text-sm text-text-secondary mb-4">
                    Åpne fullskjerm-editoren for å redigere LaTeX med live forhåndsvisning
                  </p>
                  <button
                    onClick={() => store.toggleLatexEditor()}
                    className="btn-primary"
                  >
                    <Pencil size={14} />
                    Åpne editor
                  </button>
                </div>
              </motion.div>
            )}

            {activeTab === "differentiation" && (
              <motion.div
                key="diff"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {diffLoading ? (
                  <div className="card text-center py-12">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                      className="w-8 h-8 border-2 border-accent-blue border-t-transparent rounded-full mx-auto mb-3"
                    />
                    <p className="text-sm text-text-secondary">
                      Genererer tre nivåer...
                    </p>
                  </div>
                ) : diffData ? (
                  <div className="space-y-4">
                    {/* Level tabs */}
                    <div className="flex gap-2">
                      {(["basic", "standard", "advanced"] as const).map((level) => (
                        <button
                          key={level}
                          onClick={() => setActiveLevel(level)}
                          className={`btn-ghost flex-1 ${
                            activeLevel === level
                              ? "!bg-accent-blue/10 !text-accent-blue"
                              : ""
                          }`}
                        >
                          {level === "basic"
                            ? `Grunnleggende (${diffData.basic_exercise_count})`
                            : level === "standard"
                            ? `Standard (${diffData.standard_exercise_count})`
                            : `Avansert (${diffData.advanced_exercise_count})`}
                        </button>
                      ))}
                    </div>

                    {/* Content */}
                    <div className="card !p-0">
                      <pre className="p-4 text-xs font-mono text-text-secondary overflow-x-auto max-h-96 overflow-y-auto">
                        {activeLevel === "basic"
                          ? diffData.basic_latex
                          : activeLevel === "standard"
                          ? diffData.standard_latex
                          : diffData.advanced_latex}
                      </pre>
                    </div>

                    {/* Download per level */}
                    <div className="flex gap-2">
                      {(["basic", "standard", "advanced"] as const).map((level) => (
                        <button
                          key={level}
                          onClick={() => {
                            const c =
                              level === "basic" ? diffData.basic_latex
                              : level === "standard" ? diffData.standard_latex
                              : diffData.advanced_latex;
                            downloadText(c, `oppgaver_${level}.tex`);
                          }}
                          className="btn-secondary text-xs flex-1"
                        >
                          <Download size={12} />
                          {level === "basic" ? "Grunnleggende" : level === "standard" ? "Standard" : "Avansert"}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Sticky action bar */}
          <div className="fixed bottom-0 left-0 md:left-sidebar-collapsed lg:left-sidebar right-0 z-30 bg-surface/90 backdrop-blur-md border-t border-border">
            <div className="max-w-content mx-auto px-6 py-3 flex items-center gap-2">
              {/* Download dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowDownloads(!showDownloads)}
                  className="btn-primary"
                >
                  <Download size={14} />
                  Last ned
                  <ChevronDown size={14} />
                </button>
                <AnimatePresence>
                  {showDownloads && (
                    <motion.div
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 8 }}
                      className="absolute bottom-full left-0 mb-2 w-48 bg-surface border border-border rounded-xl shadow-soft-lg overflow-hidden"
                    >
                      {[
                        { id: "pdf", label: "PDF", icon: <FileText size={14} /> },
                        { id: "pdf-print", label: "PDF (print)", icon: <Printer size={14} /> },
                        { id: "docx", label: "Word", icon: <FileSpreadsheet size={14} /> },
                        { id: "pptx", label: "PowerPoint", icon: <Presentation size={14} /> },
                      ].map((item) => (
                        <button
                          key={item.id}
                          onClick={() => handleExport(item.id)}
                          disabled={exportLoading === item.id}
                          className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-text-secondary hover:bg-surface-elevated hover:text-text-primary transition-colors disabled:opacity-50"
                        >
                          {item.icon}
                          {exportLoading === item.id ? "Eksporterer..." : item.label}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <button
                onClick={() => store.toggleLatexEditor()}
                className="btn-secondary"
              >
                <Pencil size={14} />
                Rediger
              </button>

              <button
                onClick={handleDifferentiate}
                disabled={diffLoading}
                className="btn-secondary"
              >
                <Layers size={14} />
                Differensiér
              </button>

              <button className="btn-secondary">
                <Share2 size={14} />
                Del
              </button>

              <div className="flex-1" />

              <button
                onClick={handleIngest}
                disabled={ingestStatus === "loading"}
                className="btn-ghost text-xs"
              >
                {ingestStatus && ingestStatus !== "loading"
                  ? ingestStatus
                  : "Lagre i bank"}
              </button>

              <button
                onClick={() => setIsFavorite(!isFavorite)}
                className="btn-ghost !p-2"
                aria-label="Merk som favoritt"
              >
                <Star
                  size={16}
                  className={
                    isFavorite
                      ? "fill-accent-orange text-accent-orange animate-star-pop"
                      : "text-text-muted"
                  }
                />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/* ---- Sub-components ---- */

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  const colorMap: Record<string, string> = {
    green: "text-accent-green",
    orange: "text-accent-orange",
    red: "text-accent-red",
    blue: "text-accent-blue",
    purple: "text-accent-purple",
  };

  return (
    <div className="card !p-3">
      <div className="flex items-center gap-1.5 text-text-muted mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <div className={`text-sm font-semibold ${colorMap[color] || ""}`}>
        {value}
      </div>
    </div>
  );
}

function downloadText(content: string, filename: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
