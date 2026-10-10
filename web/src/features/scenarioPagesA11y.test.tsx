import { fireEvent, render, screen } from "@testing-library/react";
import { describe, it, vi } from "vitest";

import type { Registry } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";
import { workspaceFixture } from "@/test/fixtures/workspace";

import { NewScenarioPage } from "./NewScenarioPage";
import { ScenariosPage } from "./ScenariosPage";
import { WorkspaceView } from "./workspace/WorkspaceView";

const REGISTRY: Registry = {
  law_baseline: "Test baseline", limitations: ["Full take-up."], max_options: 2, status_quo_label: "Status quo",
  instruments: [{ valid: true, id: "test_policy", title: "Test policy", version: "test", runnable: true,
    reference_period: { from: "2026-01-01", to: "2026-12-31" }, sources: [],
    parameters: [{ id: "test_parameter", policy_id: "test_policy", unit: "fraction", unit_label: "fraction", editable: true, value_type: "rate", current: { outcome: "calculated", value: "0.2" } }],
  }],
};
const LIST = {
  items: [{ scenario_id: "a".repeat(64), kind: "reform", title: "Raise the FTC rate", description: "A test.", created_at: "2026-10-01T00:00:00Z", runs: 1, latest_run_id: "b".repeat(64) }],
  total: 1,
};

const nav = vi.hoisted(() => ({ query: "" }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }), useSearchParams: () => new URLSearchParams(nav.query) }));
vi.mock("@/api/services/registryService", () => ({ getRegistry: () => Promise.resolve(REGISTRY), listHouseholdExamples: () => Promise.resolve([]) }));
vi.mock("@/api/services/scenarioService", () => ({
  listScenarios: () => Promise.resolve(LIST),
  runScenario: () => Promise.resolve(undefined),
  rerunHouseholdScenario: () => Promise.resolve(undefined),
}));

describe("scenario pages have no axe violations", () => {
  it("scenario list", async () => {
    const { container } = render(<ScenariosPage />);
    await screen.findByText("Raise the FTC rate");
    await expectNoAxeViolations(container);
  });

  it.each(["", "policy_change", "compare", "household"])("new scenario page, template %j", async (template) => {
    nav.query = template ? `template=${template}` : "";
    const { container } = render(<NewScenarioPage />);
    await screen.findByRole("heading", { level: 1 });
    await new Promise((r) => setTimeout(r, 50));
    await expectNoAxeViolations(container);
  });

  it("every workspace tab", async () => {
    const workspace = workspaceFixture();
    const { container } = render(<WorkspaceView workspace={workspace} navigate={() => undefined} />);
    for (const t of workspace.tabs) {
      fireEvent.click(screen.getByRole("tab", { name: t.title }));
      await expectNoAxeViolations(container);
    }
  }, 30_000);
});
