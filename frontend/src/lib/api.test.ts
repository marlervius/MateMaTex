import { describe, expect, it } from "vitest";
import { categorizeError } from "@/lib/map-api-result";
import { isTerminalGenerateStatus } from "@/lib/api";

describe("categorizeError", () => {
  it("classifies user abort messages", () => {
    expect(categorizeError("Genereringen ble avbrutt av bruker.", false, true)).toBe(
      "aborted"
    );
  });

  it("classifies LaTeX failures", () => {
    expect(categorizeError("pdflatex failed", false, true)).toBe("latex");
  });

  it("returns unknown for empty non-failed messages", () => {
    expect(categorizeError("", false, false)).toBe("unknown");
  });
});

describe("isTerminalGenerateStatus", () => {
  it("recognises completed and failed statuses", () => {
    expect(isTerminalGenerateStatus("completed")).toBe(true);
    expect(isTerminalGenerateStatus("completed_with_warnings")).toBe(true);
    expect(isTerminalGenerateStatus("failed")).toBe(true);
    expect(isTerminalGenerateStatus("running")).toBe(false);
  });
});
