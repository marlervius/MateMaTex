import { describe, expect, it } from "vitest";
import type { StreamCompletePayload } from "./generation";

describe("generation stream types", () => {
  it("accepts complete payload shape", () => {
    const p: StreamCompletePayload = {
      status: "completed",
      total_duration: 1,
      total_steps: 5,
      math_checks: 10,
      math_correct: 8,
      latex_compiled: true,
      error: null,
    };
    expect(p.latex_compiled).toBe(true);
  });
});
