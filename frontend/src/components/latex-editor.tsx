"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Save,
  X,
  Code2,
  Eye,
  Loader2,
  AlertTriangle,
  Check,
  Wand2,
  Image,
  Copy,
  Lightbulb,
} from "lucide-react";
import { compileLatex, editorAction } from "@/lib/api";

interface LatexEditorProps {
  initialContent: string;
  onSave?: (content: string) => void;
  onClose?: () => void;
}

export function LatexEditor({ initialContent, onSave, onClose }: LatexEditorProps) {
  const [content, setContent] = useState(initialContent);
  const [pdfBase64, setPdfBase64] = useState("");
  const [errors, setErrors] = useState<Array<{ line: number; message: string }>>([]);
  const [warnings, setWarnings] = useState<Array<{ line: number; message: string }>>([]);
  const [compiling, setCompiling] = useState(false);
  const [showDiff, setShowDiff] = useState(false);
  const [diffContent, setDiffContent] = useState("");
  const [aiLoading, setAiLoading] = useState("");
  const [mobileTab, setMobileTab] = useState<"code" | "preview">("code");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Debounced compilation
  const triggerCompile = useCallback((latexContent: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setCompiling(true);
      try {
        const result = await compileLatex(latexContent);
        if (result.success) {
          setPdfBase64(result.pdf_base64);
          setErrors([]);
        } else {
          setErrors(result.errors || []);
        }
        setWarnings(result.warnings || []);
      } catch {
        setErrors([{ line: 0, message: "Compilation request failed" }]);
      } finally {
        setCompiling(false);
      }
    }, 800);
  }, []);

  useEffect(() => {
    triggerCompile(content);
  }, []);

  // Cmd+S to save
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        onSave?.(content);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [content, onSave]);

  const handleChange = (value: string) => {
    setContent(value);
    triggerCompile(value);
  };

  const handleAiAction = async (action: "simplify" | "add-illustration" | "variant" | "add-hint") => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const selection = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
    if (!selection) return;

    setAiLoading(action);
    try {
      const result = await editorAction(action, selection, content);
      if (result.success) {
        setDiffContent(result.replacement_latex);
        setShowDiff(true);
      }
    } finally {
      setAiLoading("");
    }
  };

  const acceptDiff = () => {
    const textarea = textareaRef.current;
    if (!textarea || !diffContent) return;
    const before = content.substring(0, textarea.selectionStart);
    const after = content.substring(textarea.selectionEnd);
    const newContent = before + diffContent + after;
    setContent(newContent);
    triggerCompile(newContent);
    setShowDiff(false);
    setDiffContent("");
  };

  const insertAtCursor = (text: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newContent = content.substring(0, start) + text + content.substring(end);
    setContent(newContent);
    triggerCompile(newContent);
    setTimeout(() => {
      textarea.focus();
      textarea.selectionStart = textarea.selectionEnd = start + text.length;
    }, 0);
  };

  return (
    <div className="h-full flex flex-col bg-bg">
      {/* Toolbar */}
      <div className="flex items-center gap-1 px-3 py-2 border-b border-border bg-surface overflow-x-auto flex-shrink-0">
        {/* LaTeX snippets */}
        <ToolbarGroup label="Sett inn">
          <ToolbarBtn label="\\frac" onClick={() => insertAtCursor("\\frac{}{}")} />
          <ToolbarBtn label="\\int" onClick={() => insertAtCursor("\\int_{a}^{b}  \\, dx")} />
          <ToolbarBtn label="align" onClick={() => insertAtCursor("\\begin{align*}\n  & \n\\end{align*}")} />
          <ToolbarBtn label="boks" onClick={() => insertAtCursor("\\begin{taskbox}{Oppgave}\n\n\\end{taskbox}")} />
        </ToolbarGroup>

        <div className="w-px h-5 bg-border mx-1.5" />

        {/* AI actions */}
        <ToolbarGroup label="AI">
          <ToolbarBtn icon={<Wand2 size={12} />} label="Forenkle" onClick={() => handleAiAction("simplify")} loading={aiLoading === "simplify"} />
          <ToolbarBtn icon={<Image size={12} />} label="Illustrasjon" onClick={() => handleAiAction("add-illustration")} loading={aiLoading === "add-illustration"} />
          <ToolbarBtn icon={<Copy size={12} />} label="Variant" onClick={() => handleAiAction("variant")} loading={aiLoading === "variant"} />
          <ToolbarBtn icon={<Lightbulb size={12} />} label="Hint" onClick={() => handleAiAction("add-hint")} loading={aiLoading === "add-hint"} />
        </ToolbarGroup>

        <div className="flex-1" />

        {/* Status */}
        <div className="flex items-center gap-2">
          {compiling && (
            <span className="flex items-center gap-1 text-xs text-text-muted">
              <Loader2 size={12} className="animate-spin" />
              Kompilerer
            </span>
          )}
          {errors.length > 0 && (
            <span className="flex items-center gap-1 text-xs text-accent-red">
              <AlertTriangle size={12} />
              {errors.length} feil
            </span>
          )}
          {!compiling && errors.length === 0 && pdfBase64 && (
            <span className="flex items-center gap-1 text-xs text-accent-green">
              <Check size={12} />
              OK
            </span>
          )}
        </div>

        <div className="w-px h-5 bg-border mx-1.5" />

        {onSave && (
          <button onClick={() => onSave(content)} className="btn-primary !py-1.5 !px-3 text-xs">
            <Save size={12} /> Lagre
          </button>
        )}
        {onClose && (
          <button onClick={onClose} className="btn-ghost !py-1.5 !px-3 text-xs">
            <X size={12} /> Lukk
          </button>
        )}
      </div>

      {/* Mobile tabs */}
      <div className="md:hidden flex border-b border-border">
        <button
          onClick={() => setMobileTab("code")}
          className={`flex-1 py-2 text-xs text-center transition-colors ${mobileTab === "code" ? "text-accent-blue border-b-2 border-accent-blue" : "text-text-muted"}`}
        >
          <Code2 size={14} className="inline mr-1" /> Kode
        </button>
        <button
          onClick={() => setMobileTab("preview")}
          className={`flex-1 py-2 text-xs text-center transition-colors ${mobileTab === "preview" ? "text-accent-blue border-b-2 border-accent-blue" : "text-text-muted"}`}
        >
          <Eye size={14} className="inline mr-1" /> Forhåndsvisning
        </button>
      </div>

      {/* Split view */}
      <div className="flex-1 flex min-h-0">
        {/* Left: Editor */}
        <div className={`flex flex-col border-r border-border ${mobileTab === "preview" ? "hidden md:flex" : "flex"} md:w-1/2 w-full`}>
          {errors.length > 0 && (
            <div className="px-3 py-1.5 bg-accent-red/5 border-b border-accent-red/20 text-xs text-accent-red max-h-16 overflow-y-auto">
              {errors.map((err, i) => (
                <div key={i}>
                  {err.line > 0 ? `L${err.line}: ` : ""}{err.message}
                </div>
              ))}
            </div>
          )}
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => handleChange(e.target.value)}
            className="flex-1 w-full bg-bg text-text-primary font-mono text-xs p-4 resize-none focus:outline-none leading-relaxed"
            spellCheck={false}
            placeholder="Skriv LaTeX her..."
          />
        </div>

        {/* Right: Preview */}
        <div className={`bg-white flex items-center justify-center overflow-auto ${mobileTab === "code" ? "hidden md:flex" : "flex"} md:w-1/2 w-full`}>
          {pdfBase64 ? (
            <iframe
              src={`data:application/pdf;base64,${pdfBase64}`}
              className="w-full h-full border-0"
              title="PDF Preview"
            />
          ) : (
            <div className="text-slate-400 text-sm text-center p-8">
              {compiling ? "Kompilerer..." : errors.length > 0 ? "Rett feilene for forhåndsvisning" : "Skriv LaTeX for forhåndsvisning"}
            </div>
          )}
        </div>
      </div>

      {/* AI diff overlay */}
      <AnimatePresence>
        {showDiff && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-4 left-4 right-4 bg-surface border border-border rounded-xl shadow-soft-lg p-4 max-h-64 overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium">AI-forslag</h4>
              <div className="flex gap-2">
                <button onClick={acceptDiff} className="btn-primary !py-1 !px-3 text-xs">
                  <Check size={12} /> Godta
                </button>
                <button onClick={() => { setShowDiff(false); setDiffContent(""); }} className="btn-ghost !py-1 !px-3 text-xs">
                  Avvis
                </button>
              </div>
            </div>
            <pre className="text-xs font-mono text-accent-green whitespace-pre-wrap">{diffContent}</pre>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ---- Toolbar helpers ---- */
function ToolbarGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-0.5">
      <span className="text-[9px] text-text-muted mr-1 uppercase tracking-widest">{label}</span>
      {children}
    </div>
  );
}

function ToolbarBtn({
  label,
  icon,
  onClick,
  loading,
}: {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  loading?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="flex items-center gap-1 px-2 py-1 text-[11px] text-text-secondary rounded-md hover:bg-surface-elevated hover:text-text-primary transition-colors disabled:opacity-50 whitespace-nowrap"
      title={label}
    >
      {loading ? <Loader2 size={10} className="animate-spin" /> : icon}
      {label}
    </button>
  );
}
