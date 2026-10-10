import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { CheckResult, RegistryParameter, ValidInstrument } from "@/domain";

import { ConfirmationPanel, type ConfirmationItem } from "./ConfirmationPanel";

const parameter: RegistryParameter = {
  id: "ftc_rate",
  policy_id: "working_for_families",
  unit: "NZD_per_tax_year",
  unit_label: "NZ$ per tax year",
  editable: true,
  value_type: "money",
  current: { outcome: "calculated", value: "6500", source_id: "ird_ftc", locator: "Table 1", effective_from: "2026-04-01" },
};

const instrument: ValidInstrument = {
  valid: true,
  id: "working_for_families",
  title: "Working for Families",
  version: "0.1.0",
  runnable: true,
  reference_period: { from: "2026-04-01", to: "2027-03-31" },
  parameters: [parameter],
  sources: [{ id: "ird_ftc", title: "IRD Family Tax Credit" }],
};

function item(check: CheckResult): ConfirmationItem {
  return { label: null, asked: "set Ftc rate to 7000", instrument, parameter, check };
}

const OK: CheckResult = {
  ok: true,
  changes: [
    { policy_id: "working_for_families", parameter_id: "ftc_rate", operation: "set", operand: "7000", baseline: "6500", resulting: "7000", unit: "NZD_per_tax_year" },
  ],
  problems: [],
};

describe("ConfirmationPanel", () => {
  it("shows the interpretation from the check: policy, baseline to scenario, source, period, notice", () => {
    const onRun = vi.fn();
    render(<ConfirmationPanel items={[item(OK)]} limitations={["Full take-up."]} reformJson={{ a: 1 }} onRun={onRun} running={false} />);
    expect(screen.getByText("You asked:")).toBeInTheDocument();
    expect(screen.getByText("Poltika has interpreted this as:")).toBeInTheDocument();
    expect(screen.getByText("Working for Families")).toBeInTheDocument();
    expect(screen.getByText("6,500")).toBeInTheDocument();
    expect(screen.getByText("7,000")).toBeInTheDocument();
    expect(screen.getByText("NZ$ per tax year")).toBeInTheDocument();
    expect(screen.getByText(/IRD Family Tax Credit/)).toBeInTheDocument();
    expect(screen.getByText(/Table 1/)).toBeInTheDocument();
    expect(screen.getByText("2026-04-01 to 2027-03-31")).toBeInTheDocument();
    expect(screen.getByText("Synthetic population — not an estimate for New Zealand")).toBeInTheDocument();
    expect(screen.getByText("Full take-up.")).toBeInTheDocument();
    expect(screen.getByText("Advanced settings")).toBeInTheDocument();
    const run = screen.getByRole("button", { name: "Run analysis" });
    expect(run).toBeEnabled();
    fireEvent.click(run);
    expect(onRun).toHaveBeenCalledOnce();
  });

  it("disables Run and shows the problem when the check is not ok", () => {
    const bad: CheckResult = {
      ok: false,
      changes: [],
      problems: [{ policy_id: "working_for_families", parameter_id: "ftc_rate", message: "no such parameter" }],
    };
    render(<ConfirmationPanel items={[item(bad)]} limitations={[]} reformJson={{}} onRun={() => undefined} running={false} />);
    expect(screen.getByRole("button", { name: "Run analysis" })).toBeDisabled();
    expect(screen.getByText(/no such parameter/)).toBeInTheDocument();
    expect(screen.queryByText("Baseline → scenario")).toBeNull();
  });
});
