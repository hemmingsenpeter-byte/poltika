import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import { workspaceFixture } from "@/test/fixtures/workspace";

import { WorkspaceView } from "./WorkspaceView";

const service = vi.hoisted(() => ({
  runScenario: (() => Promise.resolve(undefined)) as (scenarioId: string, signal?: AbortSignal) => Promise<unknown>,
  rerunHousehold: vi.fn<(resultId: string, signal?: AbortSignal) => Promise<{ new_result_id: string }>>(),
}));
vi.mock("@/api/services/scenarioService", () => ({
  runScenario: (scenarioId: string, signal?: AbortSignal) => service.runScenario(scenarioId, signal),
  rerunHouseholdScenario: (resultId: string, signal?: AbortSignal) => service.rerunHousehold(resultId, signal),
}));

beforeEach(() => window.history.replaceState(null, "", "/scenarios/x"));

describe("WorkspaceView", () => {
  it("shows the header, IDs, context and the synthetic marker", () => {
    render(<WorkspaceView workspace={workspaceFixture()} navigate={() => undefined} />);
    expect(screen.getByRole("heading", { level: 1, name: "Raise the FTC rate" })).toBeInTheDocument();
    expect(screen.getByText("Policy change")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy scenario ID" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy run ID" })).toBeInTheDocument();
    expect(screen.getByText("Law as at 1 April 2026")).toBeInTheDocument();
    expect(screen.getByText("Synthetic")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Export Excel" })).toHaveAttribute("href", `/api/v1/scenarios/${"a".repeat(64)}/runs/${"b".repeat(64)}/export.xlsx`);
    expect(screen.getByRole("link", { name: "Export headline CSV" })).toHaveAttribute("href", `/api/v1/scenarios/${"a".repeat(64)}/runs/${"b".repeat(64)}/export/headline.csv`);
    expect(screen.getByRole("link", { name: "Edit as new scenario" })).toHaveAttribute("href", `/scenarios/new?fromScenario=${"a".repeat(64)}`);
  });

  it("moves focus and selection with the arrow keys (roving tabindex)", async () => {
    const user = userEvent.setup();
    render(<WorkspaceView workspace={workspaceFixture()} navigate={() => undefined} />);
    const overview = screen.getByRole("tab", { name: "Overview" });
    expect(overview).toHaveAttribute("aria-selected", "true");
    expect(overview).toHaveAttribute("tabindex", "0");
    expect(screen.getByRole("tab", { name: "Fiscal" })).toHaveAttribute("tabindex", "-1");

    overview.focus();
    await user.keyboard("{ArrowRight}");
    const fiscal = screen.getByRole("tab", { name: "Fiscal" });
    expect(fiscal).toHaveFocus();
    expect(fiscal).toHaveAttribute("aria-selected", "true");
    expect(window.location.search).toBe("?tab=fiscal");

    await user.keyboard("{End}");
    expect(screen.getByRole("tab", { name: "Audit" })).toHaveFocus();
    await user.keyboard("{ArrowRight}");
    expect(screen.getByRole("tab", { name: "Overview" })).toHaveFocus();
  });

  it("opens the tab named in ?tab= and shows Unavailable for empty and deferred tabs", async () => {
    window.history.replaceState(null, "", "/scenarios/x?tab=assumptions");
    render(<WorkspaceView workspace={workspaceFixture()} navigate={() => undefined} />);
    await waitFor(() => expect(screen.getByRole("tab", { name: "Assumptions" })).toHaveAttribute("aria-selected", "true"));
    expect(screen.getByText("Coming later.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "Distribution" }));
    expect(screen.getByText("No distribution for this run.")).toBeInTheDocument();
  });

  it("switches tab from a provenance chip", () => {
    render(<WorkspaceView workspace={workspaceFixture()} navigate={() => undefined} />);
    fireEvent.click(screen.getByRole("button", { name: /Fiscal: Fiscal components/ }));
    expect(screen.getByRole("tab", { name: "Fiscal" })).toHaveAttribute("aria-selected", "true");
    expect(document.getElementById("block-fiscal_components")).not.toBeNull();
  });

  it("runs again and navigates to the new run", async () => {
    const navigate = vi.fn();
    service.runScenario = () => Promise.resolve({ scenario_id: "s", run_id: "r2" });
    render(<WorkspaceView workspace={workspaceFixture()} navigate={navigate} />);
    fireEvent.click(screen.getByRole("button", { name: "Run again" }));
    await waitFor(() => expect(navigate).toHaveBeenCalledWith(`/scenarios/${"a".repeat(64)}/runs/r2`));
  });

  it("explains a 429 and offers another try", async () => {
    service.runScenario = () => Promise.reject(new ApiError("busy", "Another analysis is running.", { status: 429, code: "run_in_progress" }));
    render(<WorkspaceView workspace={workspaceFixture()} navigate={() => undefined} />);
    fireEvent.click(screen.getByRole("button", { name: "Run again" }));
    expect(await screen.findByText("Try again shortly.")).toBeInTheDocument();
    expect(screen.getByText("run_in_progress")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });

  it("reruns a household through the existing legacy endpoint", async () => {
    const base = workspaceFixture();
    const navigate = vi.fn();
    service.rerunHousehold.mockResolvedValue({ new_result_id: "new_result" });
    render(<WorkspaceView workspace={{ ...base, scenario: { ...base.scenario, kind: "household" } }} navigate={navigate} />);
    fireEvent.click(screen.getByRole("button", { name: "Run again" }));
    await waitFor(() => expect(navigate).toHaveBeenCalledWith(`/scenarios/${base.scenario.scenario_id}/runs/new_result`));
    expect(service.rerunHousehold).toHaveBeenCalledWith(base.run?.run_id, expect.any(AbortSignal));
    expect(screen.queryByRole("link", { name: "Export Excel" })).toBeNull();
    expect(screen.getByRole("link", { name: "Edit as new scenario" })).toHaveAttribute("href", `/scenarios/new?fromHousehold=${base.scenario.scenario_id}&fromRun=${base.run?.run_id}`);
  });

  it("selects a different stored run by its full ID", () => {
    const base = workspaceFixture();
    const navigate = vi.fn();
    render(<WorkspaceView workspace={{ ...base, runs: [...base.runs, { run_id: "another_run", created_at: null }] }} navigate={navigate} />);
    fireEvent.change(screen.getByLabelText("Run"), { target: { value: "another_run" } });
    expect(navigate).toHaveBeenCalledWith(`/scenarios/${base.scenario.scenario_id}/runs/another_run`);
  });

  it("ignores a pending run completion after leaving the workspace", async () => {
    let finish!: (value: { scenario_id: string; run_id: string }) => void;
    const run = vi.fn<(scenarioId: string, signal?: AbortSignal) => Promise<unknown>>(() => new Promise((resolve) => { finish = resolve; }));
    service.runScenario = run;
    const navigate = vi.fn();
    const view = render(<WorkspaceView workspace={workspaceFixture()} navigate={navigate} />);
    fireEvent.click(screen.getByRole("button", { name: "Run again" }));
    const signal = run.mock.calls[0]?.[1];
    view.unmount();
    expect(signal?.aborted).toBe(true);
    await act(async () => { finish({ scenario_id: "s", run_id: "r" }); });
    expect(navigate).not.toHaveBeenCalled();
  });
});
