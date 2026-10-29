import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { Registry } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

import { DataPage } from "./DataPage";
import { HomePage } from "./HomePage";
import { ModelsPage } from "./ModelsPage";
import { NewScenarioPage } from "./NewScenarioPage";
import { ScenarioWorkspacePage } from "./ScenarioWorkspacePage";
import { ScenariosPage } from "./ScenariosPage";

// Axe over the empty, loading, error and unavailable states (and Home), which
// the per-page tests do not cover. Rejections land on a later tick, as a real
// network call's would.
type Call = () => Promise<unknown>;
const never: Call = () => new Promise(() => undefined);
const later = (error: unknown): Call => () => new Promise((_, reject) => setTimeout(() => reject(error), 0));
const svc = vi.hoisted(() => ({
  models: undefined as unknown as () => Promise<unknown>,
  datasets: undefined as unknown as () => Promise<unknown>,
  scenarios: undefined as unknown as () => Promise<unknown>,
  workspace: undefined as unknown as () => Promise<unknown>,
  definition: undefined as unknown as () => Promise<unknown>,
  registry: undefined as unknown as () => Promise<unknown>,
  examples: undefined as unknown as () => Promise<unknown>,
  query: "",
}));
vi.mock("@/api/services/modelService", () => ({ listModels: () => svc.models() }));
vi.mock("@/api/services/dataService", () => ({ listDatasets: () => svc.datasets() }));
vi.mock("@/api/services/registryService", () => ({ getRegistry: () => svc.registry(), listHouseholdExamples: () => svc.examples() }));
vi.mock("@/api/services/scenarioService", () => ({
  listScenarios: () => svc.scenarios(),
  getWorkspace: () => svc.workspace(),
  getScenarioDefinition: () => svc.definition(),
  runScenario: () => Promise.resolve(undefined),
  rerunHouseholdScenario: () => Promise.resolve(undefined),
}));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(svc.query),
  usePathname: () => `/scenarios/${"a".repeat(64)}`,
}));

const REGISTRY: Registry = {
  law_baseline: "Test baseline", limitations: [], max_options: 2, status_quo_label: "Status quo",
  instruments: [{ valid: true, id: "test_policy", title: "Test policy", version: "test", runnable: true,
    reference_period: { from: "2026-01-01", to: "2026-12-31" }, sources: [],
    parameters: [{ id: "test_parameter", policy_id: "test_policy", unit: "fraction", unit_label: "fraction", editable: true, value_type: "rate", current: { outcome: "calculated", value: "0.2" } }],
  }],
};
const unavailable = new ApiError("unavailable", "Scenario storage is not configured here.", { status: 503, code: "scenario_storage_unavailable" });
const failed = new ApiError("server", "The server failed.", { status: 500, code: "boom" });

beforeEach(() => {
  svc.query = "";
  svc.models = svc.datasets = svc.scenarios = svc.workspace = svc.definition = svc.examples = never;
  svc.registry = () => Promise.resolve(REGISTRY);
});

describe("Home search note", () => {
  it("describes the search input whether Advanced is closed or open", () => {
    svc.registry = never;
    const { container } = render(<HomePage />);
    const note = "does not interpret questions in plain language yet";
    const input = screen.getByRole("searchbox");
    const details = container.querySelector("details") as HTMLDetailsElement;
    expect(details.open).toBe(false);
    expect(input).toHaveAccessibleDescription(expect.stringContaining(note));
    details.open = true;
    expect(input).toHaveAccessibleDescription(expect.stringContaining(note));
  });
});

describe("Home has no axe violations", () => {
  it("at rest and while searching: loading, error, no match, results", async () => {
    svc.registry = never;
    const { container } = render(<HomePage />);
    await expectNoAxeViolations(container);
    const search = screen.getByRole("searchbox");
    fireEvent.change(search, { target: { value: "family" } });
    await screen.findByRole("status");
    await expectNoAxeViolations(container);
  });

  it("when the registry fails", async () => {
    svc.registry = later(failed);
    const { container } = render(<HomePage />);
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "family" } });
    await screen.findByRole("alert");
    await expectNoAxeViolations(container);
  });

  it("with no match and with a match", async () => {
    const { container } = render(<HomePage />);
    const search = screen.getByRole("searchbox");
    fireEvent.change(search, { target: { value: "zzzz-no-such" } });
    await screen.findByText("No supported analysis matches");
    await expectNoAxeViolations(container);
    fireEvent.change(search, { target: { value: "test" } });
    await screen.findAllByRole("link", { name: /test/i });
    await expectNoAxeViolations(container);
  });
});

describe("catalogue pages: empty, loading and error states have no axe violations", () => {
  it("Models", async () => {
    svc.models = never;
    const loading = render(<ModelsPage />);
    await screen.findByRole("status");
    await expectNoAxeViolations(loading.container);
    loading.unmount();

    svc.models = () => Promise.resolve({ validation_levels: [], models: [] });
    const empty = render(<ModelsPage />);
    await screen.findByText("No models are registered");
    await expectNoAxeViolations(empty.container);
    empty.unmount();

    svc.models = later(new ApiError("unavailable", "The model registry here is invalid.", { status: 503, code: "catalogue_unavailable" }));
    const error = render(<ModelsPage />);
    await screen.findByRole("alert");
    await expectNoAxeViolations(error.container);
  });

  it("Data", async () => {
    svc.datasets = never;
    const loading = render(<DataPage />);
    await screen.findByRole("status");
    await expectNoAxeViolations(loading.container);
    loading.unmount();

    svc.datasets = () => Promise.resolve({ datasets: [], populations: [], preserved_sources: { exposed: false, note: "Preserved sources are not yet exposed (ADR-0022)." } });
    const empty = render(<DataPage />);
    await screen.findByText("No datasets are registered");
    await expectNoAxeViolations(empty.container);
    empty.unmount();

    svc.datasets = later(new ApiError("unavailable", "The dataset catalogue here is invalid.", { status: 503, code: "catalogue_unavailable" }));
    const error = render(<DataPage />);
    await screen.findByRole("alert");
    await expectNoAxeViolations(error.container);
  });
});

describe("scenario pages: empty, loading, error and unavailable states have no axe violations", () => {
  it("scenario list", async () => {
    svc.scenarios = never;
    const loading = render(<ScenariosPage />);
    await screen.findByRole("status");
    await expectNoAxeViolations(loading.container);
    loading.unmount();

    svc.scenarios = () => Promise.resolve({ items: [], total: 0 });
    const empty = render(<ScenariosPage />);
    await screen.findByText("No scenarios yet");
    await expectNoAxeViolations(empty.container);
    empty.unmount();

    svc.scenarios = later(failed);
    const error = render(<ScenariosPage />);
    await screen.findByRole("alert");
    await expectNoAxeViolations(error.container);
    error.unmount();

    svc.scenarios = later(unavailable);
    const gone = render(<ScenariosPage />);
    await screen.findByText("Scenarios are not available here");
    await expectNoAxeViolations(gone.container);
  });

  it("workspace", async () => {
    svc.workspace = never;
    const loading = render(<ScenarioWorkspacePage />);
    await screen.findByRole("status");
    await expectNoAxeViolations(loading.container);
    loading.unmount();

    svc.workspace = later(new ApiError("not_found", "No reform scenario has this id.", { status: 404, code: "scenario_not_found" }));
    const error = render(<ScenarioWorkspacePage />);
    await screen.findByRole("alert");
    await expectNoAxeViolations(error.container);
    error.unmount();

    svc.workspace = later(unavailable);
    const gone = render(<ScenarioWorkspacePage />);
    await screen.findByText("Scenarios are not available here");
    await expectNoAxeViolations(gone.container);
  });

  it("new scenario: loading and error while reading a saved definition, and no household examples", async () => {
    svc.query = "fromScenario=saved";
    svc.definition = never;
    const loading = render(<NewScenarioPage />);
    await screen.findByRole("status");
    await expectNoAxeViolations(loading.container);
    loading.unmount();

    svc.definition = later(failed);
    const error = render(<NewScenarioPage />);
    await screen.findByRole("alert");
    await expectNoAxeViolations(error.container);
    error.unmount();

    svc.query = "template=household";
    svc.examples = () => Promise.resolve([]);
    const empty = render(<NewScenarioPage />);
    await screen.findByText("No examples are available");
    await expectNoAxeViolations(empty.container);
  });
});
