"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/lib/store";
import { GenerationWizard } from "@/components/generation-wizard";
import { PipelineProgress } from "@/components/pipeline-progress";
import { ResultView } from "@/components/result-view";
import { LatexEditor } from "@/components/latex-editor";

export default function HomePage() {
  const { isGenerating, result, showLatexEditor, toggleLatexEditor } =
    useAppStore();

  // Full-screen LaTeX editor (opened from result view)
  if (showLatexEditor && result?.fullDocument) {
    return (
      <div className="fixed inset-0 z-40 bg-bg flex flex-col">
        <LatexEditor
          initialContent={result.fullDocument}
          onSave={(content) => {
            useAppStore.getState().setResult({
              ...result,
              fullDocument: content,
            });
          }}
          onClose={toggleLatexEditor}
        />
      </div>
    );
  }

  return (
    <div>
      <AnimatePresence mode="wait">
        {/* State 1: Generation wizard */}
        {!isGenerating && !result && (
          <motion.div
            key="wizard"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
          >
            <div className="text-center mb-10 pt-4">
              <h1 className="font-display text-4xl tracking-tight mb-2">
                Hva skal vi lage i dag?
              </h1>
              <p className="text-text-secondary">
                Velg trinn, emne og type — AI-teamet tar seg av resten
              </p>
            </div>
            <GenerationWizard />
          </motion.div>
        )}

        {/* State 2: Pipeline running */}
        {isGenerating && (
          <motion.div
            key="progress"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            className="pt-4"
          >
            <PipelineProgress />
          </motion.div>
        )}

        {/* State 3: Results */}
        {!isGenerating && result && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
          >
            <ResultView />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
