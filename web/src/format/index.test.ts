import { describe, expect, it } from "vitest";

import { formatCount, formatMoney, formatPercent, formatPp, NOT_CALCULATED, outcomeOfCell, periodLabel } from "./index";

describe("formatMoney household_rule", () => {
  const rule = { precision: "household_rule" } as const;

  it("shows exact cents as given", () => {
    expect(formatMoney("1234.56", rule)).toBe("$1,234.56");
    expect(formatMoney("7921", rule)).toBe("$7,921");
    expect(formatMoney("305.50", rule)).toBe("$305.50");
    expect(formatMoney("1234567.891", rule)).toBe("$1,234,567.891");
  });

  it("uses a true minus for a negative amount", () => {
    expect(formatMoney("-1234.56", rule)).toBe("−$1,234.56");
  });

  it("keeps a real zero, which is not the same as missing", () => {
    expect(formatMoney("0", rule)).toBe("$0");
    expect(formatMoney("-0.00", rule)).toBe("$0.00");
  });

  it("returns the marker for null, never zero", () => {
    expect(formatMoney(null, rule)).toBe(NOT_CALCULATED);
    expect(formatMoney(null, rule)).not.toMatch(/0/);
  });

  it("appends the period when given", () => {
    expect(formatMoney("7921", { ...rule, period: "tax_year" })).toBe("$7,921 per tax year");
    expect(formatMoney("305", { ...rule, period: "week" })).toBe("$305 per week");
  });

  it("returns an unparseable value as written, not as a number", () => {
    expect(formatMoney("abc", rule)).toBe("abc");
  });
});

describe("formatMoney population_estimate", () => {
  const estimate = { precision: "population_estimate" } as const;

  it("uses 3 significant figures with a suffix", () => {
    expect(formatMoney("1420000000", estimate)).toBe("$1.42B");
    expect(formatMoney("1423456789", estimate)).toBe("$1.42B");
    expect(formatMoney("12345678", estimate)).toBe("$12.3M");
    expect(formatMoney("123456", estimate)).toBe("$123k");
    expect(formatMoney("999600", estimate)).toBe("$1.00M");
    expect(formatMoney("456", estimate)).toBe("$456");
    expect(formatMoney("12.345", estimate)).toBe("$12.3");
  });

  it("carries the sign", () => {
    expect(formatMoney("-23456", estimate)).toBe("−$23.5k");
    expect(formatMoney("-1420000000", estimate)).toBe("−$1.42B");
  });

  it("does not round a billion-scale value into a different unit label", () => {
    expect(formatMoney("1234000000000", estimate)).toBe("$1230B");
  });

  it("returns the marker for null", () => {
    expect(formatMoney(null, estimate)).toBe(NOT_CALCULATED);
  });

  it("adds the period", () => {
    expect(formatMoney("1420000000", { ...estimate, period: "tax_year" })).toBe("$1.42B per tax year");
  });
});

describe("formatCount", () => {
  it("groups exactly for a household rule and rounds an estimate", () => {
    expect(formatCount("12345", { precision: "household_rule" })).toBe("12,345");
    expect(formatCount("1423456", { precision: "population_estimate" })).toBe("1.42M");
    expect(formatCount("812", { precision: "population_estimate" })).toBe("812");
    expect(formatCount(null, { precision: "population_estimate" })).toBe(NOT_CALCULATED);
  });
});

describe("formatPercent and formatPp", () => {
  it("scales a fraction to a percentage", () => {
    expect(formatPercent("-0.012")).toBe("−1.2%");
    expect(formatPercent("0.5")).toBe("50.0%");
    expect(formatPercent("0")).toBe("0.0%");
    expect(formatPercent("-0.0001")).toBe("0.0%");
    expect(formatPercent(null)).toBe(NOT_CALCULATED);
  });

  it("shows percentage points with an explicit sign", () => {
    expect(formatPp("0.021")).toBe("+2.1 pp");
    expect(formatPp("-0.021")).toBe("−2.1 pp");
    expect(formatPp("0")).toBe("0.0 pp");
    expect(formatPp(null)).toBe(NOT_CALCULATED);
  });
});

describe("periodLabel", () => {
  it("names the period", () => {
    expect(periodLabel("tax_year")).toBe("per tax year");
    expect(periodLabel("week")).toBe("per week");
  });
});

describe("outcomeOfCell", () => {
  it.each(["constructor", "__proto__", "Option A", "123.45", ""])(
    "keeps ordinary text %j outside the outcome markers",
    (cell) => expect(outcomeOfCell(cell)).toBeNull(),
  );

  it.each([
    ["not calculated", "not_calculated"],
    ["NOT_CALCULATED", "not_calculated"],
    [" Needs review ", "needs_review"],
    ["needs_review", "needs_review"],
    ["unsupported", "unsupported"],
  ])("recognises the supported marker %j", (cell, outcome) => {
    expect(outcomeOfCell(cell)).toBe(outcome);
  });
});
