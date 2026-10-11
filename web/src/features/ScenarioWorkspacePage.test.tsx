import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import { workspaceFixture } from "@/test/fixtures/workspace";

import { ScenarioWorkspacePage } from "./ScenarioWorkspacePage";

const service = vi.hoisted(() => ({ getWorkspace: (): Promise<unknown> => Promise.resolve(undefined) }));
vi.mock("@/api/services/scenarioService", () => ({ getWorkspace: () => service.getWorkspace() }));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: () => undefined }),
  usePathname: () => `/scenarios/${"a".repeat(64)}/runs/${"b".repeat(64)}`,
}));

describe("ScenarioWorkspacePage", () => {
  it("loads, then shows the workspace", async () => {
    service.getWorkspace = () => Promise.resolve(workspaceFixture());
    render(<ScenarioWorkspacePage />);
    expect(await screen.findByRole("heading", { level: 1, name: "Raise the FTC rate" })).toBeInTheDocument();
  });

  it("shows Not found for a 404 scenario_not_found", async () => {
    service.getWorkspace = () =>
      Promise.reject(new ApiError("not_found", "No reform scenario has this id.", { status: 404, code: "scenario_not_found" }));
    render(<ScenarioWorkspacePage />);
    expect(await screen.findByText("Not found")).toBeInTheDocument();
    expect(screen.getByText("scenario_not_found")).toBeInTheDocument();
  });

  it("shows Unavailable for 503 scenario_storage_unavailable", async () => {
    service.getWorkspace = () =>
      Promise.reject(new ApiError("unavailable", "Scenario storage is not configured here.", { status: 503, code: "scenario_storage_unavailable" }));
    render(<ScenarioWorkspacePage />);
    expect(await screen.findByText("Scenarios are not available here")).toBeInTheDocument();
    expect(screen.getByText("Scenario storage is not configured here.")).toBeInTheDocument();
  });
});
