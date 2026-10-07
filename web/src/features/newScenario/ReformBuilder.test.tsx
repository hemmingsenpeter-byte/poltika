import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { CheckResult, Registry } from "@/domain";

import { ReformBuilder } from "./ReformBuilder";

const svc = vi.hoisted(() => ({
  check: (): Promise<unknown> => Promise.resolve(undefined),
  create: (): Promise<unknown> => Promise.resolve(undefined),
  run: (): Promise<unknown> => Promise.resolve(undefined),
}));
vi.mock("@/api/services/registryService", () => ({
  getRegistry: () => Promise.resolve(REGISTRY),
  checkReform: () => svc.check(),
}));
vi.mock("@/api/services/scenarioService", () => ({
  createScenario: () => svc.create(),
  runScenario: () => svc.run(),
}));

const REGISTRY: Registry = {
  law_baseline: "Law as at 1 April 2026",
  limitations: ["Full take-up."],
  max_options: 2,
  status_quo_label: "Status quo",
  instruments: [
    {
      valid: true,
      id: "working_for_families",
      title: "Working for Families",
      version: "0.1.0",
      runnable: true,
      reference_period: { from: "2026-04-01", to: "2027-03-31" },
      sources: [{ id: "ird_ftc", title: "IRD Family Tax Credit" }],
      parameters: [
        {
          id: "ftc_rate",
          policy_id: "working_for_families",
          unit: "NZD_per_tax_year",
          unit_label: "NZ$ per tax year",
          editable: true,
          value_type: "money",
          current: { outcome: "calculated", value: "6500", source_id: "ird_ftc", locator: "Table 1" },
        },
      ],
    },
  ],
};

const OK: CheckResult = {
  ok: true,
  changes: [{ policy_id: "working_for_families", parameter_id: "ftc_rate", operation: "set", operand: "7000", baseline: "6500", resulting: "7000", unit: "NZD_per_tax_year" }],
  problems: [],
};

async function fill() {
  render(<ReformBuilder compare={false} navigate={navigate} />);
  fireEvent.change(await screen.findByLabelText("Title"), { target: { value: "Raise FTC" } });
  fireEvent.change(screen.getByLabelText("Policy"), { target: { value: "working_for_families" } });
  fireEvent.change(screen.getByLabelText("Parameter"), { target: { value: "ftc_rate" } });
}
const navigate = vi.fn();

describe("ReformBuilder", () => {
  it("rejects a value that is not a decimal and does not call the check", async () => {
    svc.check = vi.fn(() => Promise.resolve(OK));
    await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "abc" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    expect(await screen.findByText("Enter a decimal number, such as 0.25.")).toBeInTheDocument();
    expect(svc.check).not.toHaveBeenCalled();
  });

  it("checks, confirms, runs and navigates to the run", async () => {
    svc.check = () => Promise.resolve(OK);
    svc.create = () => Promise.resolve("s1");
    svc.run = () => Promise.resolve({ scenario_id: "s1", run_id: "r1" });
    await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "7000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    expect(await screen.findByText("Poltika has interpreted this as:")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Run analysis" }));
    await waitFor(() => expect(navigate).toHaveBeenCalledWith("/scenarios/s1/runs/r1"));
  });

  it("shows the 429 guidance when a run is already in progress", async () => {
    svc.check = () => Promise.resolve(OK);
    svc.create = () => Promise.resolve("s1");
    svc.run = () => Promise.reject(new ApiError("busy", "A run is in progress.", { status: 429, code: "run_in_progress" }));
    await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "7000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    fireEvent.click(await screen.findByRole("button", { name: "Run analysis" }));
    expect(await screen.findByText("Try again shortly.")).toBeInTheDocument();
  });
});
