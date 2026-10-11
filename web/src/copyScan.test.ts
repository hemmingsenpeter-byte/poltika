import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/** ADR-0023: gated terms must not reach user-facing copy. The v0.3 release
 *  gate scans only HTML FastAPI serves itself, so the frontend checks its own
 *  source. (tests/unit/api/test_web_static.py scans the built pages.) */
const GATED = [
  "digital twin",
  "decision intelligence",
  "decision infrastructure",
  "scientific layer",
  "policy search",
  "predictive",
  "forecast",
];

const SRC = join(__dirname);
const SKIPPED = new Set(["schema.gen.ts"]); // generated from backend docstrings

function sourceFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) return sourceFiles(path);
    if (SKIPPED.has(name) || /\.test\.tsx?$/.test(name)) return [];
    return /\.(tsx?|css|json)$/.test(name) ? [path] : [];
  });
}

describe("copy scan", () => {
  const files = sourceFiles(SRC);

  it("finds the source files", () => {
    expect(files.length).toBeGreaterThan(20);
  });

  it("finds no gated term in web/src", () => {
    const hits = files.flatMap((file) => {
      const text = readFileSync(file, "utf8").toLowerCase();
      return GATED.filter((term) => text.includes(term)).map((term) => `${file}: ${term}`);
    });
    expect(hits).toEqual([]);
  });
});
