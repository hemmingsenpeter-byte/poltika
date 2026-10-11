import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { CreateScenarioRequest } from "@/api/services/scenarioService";
import type { Registry } from "@/domain";

import { NewScenarioPage } from "./NewScenarioPage";

const state = vi.hoisted(() => ({ query: "", definition: vi.fn<(scenarioId: string, signal?: AbortSignal) => Promise<CreateScenarioRequest>>(), household: vi.fn<(scenarioId: string, runId: string, signal?: AbortSignal) => Promise<Record<string, unknown>>>() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }), useSearchParams: () => new URLSearchParams(state.query) }));
vi.mock("@/api/services/scenarioService", () => ({ getScenarioDefinition: (scenarioId: string, signal?: AbortSignal) => state.definition(scenarioId, signal), getHouseholdDefinition: (scenarioId: string, runId: string, signal?: AbortSignal) => state.household(scenarioId, runId, signal) }));
vi.mock("@/api/services/registryService", () => ({ getRegistry: () => Promise.resolve(REGISTRY) }));

const REGISTRY: Registry = {
  law_baseline: "Test baseline", limitations: [], max_options: 2, status_quo_label: "Status quo",
  instruments: [{ valid: true, id: "test_policy", title: "Test policy", version: "test", runnable: true,
    reference_period: { from: "2026-01-01", to: "2026-12-31" }, sources: [],
    parameters: [{ id: "test_parameter", policy_id: "test_policy", unit: "fraction", unit_label: "fraction", editable: true, value_type: "rate", current: { outcome: "calculated", value: "0.2" } }],
  }],
};
const DEFINITION: CreateScenarioRequest = {
  title: "Saved comparison", description: "Retained description",
  options: ["A", "B"].map((label, i) => ({ label, reform: { reform_id: `retained_${label}`, description: `Description ${label}`, overrides: [{ policy_id: "test_policy", parameter_id: "test_parameter", operation: "set", value: i === 0 ? "0.3" : "0.4" }] } })),
};

beforeEach(() => { state.query = ""; state.definition.mockReset(); state.household.mockReset(); });

describe("NewScenarioPage", () => {
  it("prefills both stored options when editing a comparison as new", async () => {
    state.query = "fromScenario=saved";
    state.definition.mockResolvedValue(DEFINITION);
    render(<NewScenarioPage />);
    expect(await screen.findByLabelText("Title")).toHaveValue("Saved comparison");
    expect(screen.getByLabelText("Description (optional)")).toHaveValue("Retained description");
    expect(screen.getAllByLabelText("Option label").map((input) => (input as HTMLInputElement).value)).toEqual(["A", "B"]);
    expect(screen.getAllByLabelText("Value").map((input) => (input as HTMLInputElement).value)).toEqual(["0.3", "0.4"]);
    expect(state.definition).toHaveBeenCalledWith("saved", expect.any(AbortSignal));
    expect(screen.queryByRole("button", { name: "Run analysis" })).toBeNull();
  });

  it("updates the template after query navigation on the same page", async () => {
    state.query = "template=policy_change";
    const view = render(<NewScenarioPage />);
    expect(await screen.findByRole("heading", { name: "Analyse a policy change" })).toBeInTheDocument();
    state.query = "template=compare";
    view.rerender(<NewScenarioPage />);
    expect(screen.getByRole("heading", { name: "Compare two settings" })).toBeInTheDocument();
    expect(await screen.findAllByLabelText("Option label")).toHaveLength(2);
    state.query = "";
    view.rerender(<NewScenarioPage />);
    expect(screen.getByRole("link", { name: /Analyse a policy change/ })).toBeInTheDocument();
  });

  it("shows the complete definition when the saved overrides exceed this form", async () => {
    state.query = "fromScenario=complex";
    const complex = { ...DEFINITION, options: [{ ...DEFINITION.options[0]!, reform: { ...DEFINITION.options[0]!.reform, overrides: [...DEFINITION.options[0]!.reform.overrides, { policy_id: "test_policy", parameter_id: "another_parameter", operation: "add" as const, value: "0.1" }] } }] };
    state.definition.mockResolvedValue(complex);
    render(<NewScenarioPage />);
    expect(await screen.findByText("These settings cannot be edited here")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Original settings"));
    expect(screen.getByText(/another_parameter/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Run analysis" })).toBeNull();
  });

  it("loads a specific household run without substituting an example", async () => {
    state.query = "fromHousehold=saved&fromRun=retained_run";
    const copied = { wff: { modelled_date: "2025-06-01", requested_policy_version: "historical", custom_fact: "retained" }, accommodation_supplement: { assessment_week_start: "2025-06-01", assessment_week_end: "2025-06-08", requested_policy_version: "historical" } };
    state.household.mockResolvedValue(copied);
    render(<NewScenarioPage />);
    expect(await screen.findByLabelText("Copied household facts")).toHaveValue(JSON.stringify(copied, null, 2));
    expect(state.household).toHaveBeenCalledWith("saved", "retained_run", expect.any(AbortSignal));
    expect(screen.queryByRole("radio")).toBeNull();
  });
});
