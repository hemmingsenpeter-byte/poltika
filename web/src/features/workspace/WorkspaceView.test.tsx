import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import { workspaceFixture } from "@/test/fixtures/workspace";

import { WorkspaceView } from "./WorkspaceView";

const service = vi.hoisted(() => ({ runScenario: (): Promise<unknown> => Promise.resolve(undefined) }));
vi.mock("@/api/services/scenarioService", () => ({ runScenario: () => service.runScenario() }));

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
    expect(screen.getByText(/available from the classic workbench API/)).toBeInTheDocument();
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

  it("offers no run button for a household scenario", () => {
    const base = workspaceFixture();
    render(<WorkspaceView workspace={{ ...base, scenario: { ...base.scenario, kind: "household" } }} navigate={() => undefined} />);
    expect(screen.queryByRole("button", { name: "Run again" })).toBeNull();
  });
});
