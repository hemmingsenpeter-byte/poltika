import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { Registry } from "@/domain";

import { HouseholdBuilder } from "./HouseholdBuilder";

const service = vi.hoisted(() => ({ create: vi.fn<(request: Record<string, unknown>, signal?: AbortSignal) => Promise<{ scenario_id: string; result_id: string }>>() }));
vi.mock("@/api/services/registryService", () => ({
  listHouseholdExamples: () => Promise.resolve([EXAMPLE]),
  getRegistry: () => Promise.resolve(REGISTRY),
}));
vi.mock("@/api/services/scenarioService", () => ({ createHouseholdScenario: (request: Record<string, unknown>, signal?: AbortSignal) => service.create(request, signal) }));

const EXAMPLE = {
  id: "example", description: "Example household",
  request: {
    wff: { modelled_date: "2026-06-01", requested_policy_version: "test", family_income: "12345" },
    accommodation_supplement: { assessment_week_start: "2026-06-01", assessment_week_end: "2026-06-08", requested_policy_version: "test", accommodation_cost: "300" },
    as_claimant_is_wff_claimant_or_partner: true,
  },
};
const REGISTRY: Registry = {
  law_baseline: "Test baseline", limitations: ["Test limitation"], max_options: 2, status_quo_label: "Status quo",
  instruments: [{
    valid: true, id: "working_for_families", title: "Working for Families", version: "test", runnable: true,
    reference_period: { from: "2026-04-01", to: "2027-03-31" },
    sources: [{ id: "test-source", title: "Test primary source" }],
    parameters: [{ id: "test_parameter", policy_id: "working_for_families", unit: "fraction", unit_label: "fraction", editable: true, value_type: "rate", current: { outcome: "calculated", value: "0.2", source_id: "test-source", locator: "Test locator" } }],
  }],
};

beforeEach(() => { service.create.mockReset(); });

async function choose(navigate = vi.fn()) {
  const view = render(<HouseholdBuilder navigate={navigate} />);
  fireEvent.click(await screen.findByRole("radio", { name: "Example household" }));
  return { ...view, navigate };
}

describe("HouseholdBuilder", () => {
  it("confirms the actual periods, household facts, sources and limitations before saving", async () => {
    service.create.mockResolvedValue({ scenario_id: "s", result_id: "r" });
    const { navigate } = await choose();
    expect(screen.getByText(/One household; no population/)).toBeInTheDocument();
    expect(screen.getByText(/assessment week 2026-06-01 to 2026-06-08 \(end exclusive\)/)).toBeInTheDocument();
    expect(screen.getByText("12345")).toBeInTheDocument();
    expect(screen.getByText(/Test primary source · Test locator/)).toBeInTheDocument();
    expect(screen.getByText("Test limitation")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Save & calculate" }));
    await waitFor(() => expect(navigate).toHaveBeenCalledWith("/scenarios/s/runs/r"));
    expect(service.create).toHaveBeenCalledWith(EXAMPLE.request, expect.any(AbortSignal));
  });

  it("shows an unavailable storage error without claiming a successful run", async () => {
    service.create.mockRejectedValue(new ApiError("unavailable", "Storage unavailable", { status: 503 }));
    const { navigate } = await choose();
    fireEvent.click(screen.getByRole("button", { name: "Save & calculate" }));
    expect(await screen.findByText("Storage unavailable")).toBeInTheDocument();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("aborts a pending calculation when leaving and ignores its late response", async () => {
    let finish!: (value: { scenario_id: string; result_id: string }) => void;
    service.create.mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
    const { navigate, unmount } = await choose();
    fireEvent.click(screen.getByRole("button", { name: "Save & calculate" }));
    expect(screen.getByRole("radio", { name: "Example household" })).toBeDisabled();
    const signal = service.create.mock.calls[0]?.[1];
    unmount();
    expect(signal?.aborted).toBe(true);
    await act(async () => { finish({ scenario_id: "s", result_id: "r" }); });
    expect(navigate).not.toHaveBeenCalled();
  });

  it("edits copied facts without replacing the original requested version or period", async () => {
    const copied = { ...EXAMPLE.request, wff: { ...EXAMPLE.request.wff, requested_policy_version: "historical", modelled_date: "2025-06-01" } };
    service.create.mockResolvedValue({ scenario_id: "new_s", result_id: "new_r" });
    render(<HouseholdBuilder initial={copied} navigate={() => undefined} />);
    const textarea = await screen.findByLabelText("Copied household facts");
    const edited = { ...copied, wff: { ...copied.wff, family_income: "54321" } };
    fireEvent.change(textarea, { target: { value: JSON.stringify(edited) } });
    expect(screen.getByText(/Version historical · per tax year; policy lookup date 2025-06-01/)).toBeInTheDocument();
    expect(screen.getByText(/currently deployed policies/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Save & calculate" }));
    await waitFor(() => expect(service.create).toHaveBeenCalledWith(edited, expect.any(AbortSignal)));
    expect(copied.wff.family_income).toBe("12345");
  });

  it("disables calculation when copied facts contain invalid JSON", async () => {
    render(<HouseholdBuilder initial={EXAMPLE.request} navigate={() => undefined} />);
    fireEvent.change(await screen.findByLabelText("Copied household facts"), { target: { value: "{" } });
    expect(screen.getByRole("alert")).toHaveTextContent("Enter valid JSON");
    expect(screen.getByRole("button", { name: "Save & calculate" })).toBeDisabled();
    expect(service.create).not.toHaveBeenCalled();
  });
});
