import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { CreateScenarioRequest, Reform } from "@/api/services/scenarioService";
import type { CheckResult, Registry } from "@/domain";

import { ReformBuilder } from "./ReformBuilder";

const svc = vi.hoisted(() => ({
  check: (() => Promise.resolve(undefined)) as (reform: Reform, signal?: AbortSignal) => Promise<unknown>,
  create: (() => Promise.resolve(undefined)) as (request: CreateScenarioRequest, signal?: AbortSignal) => Promise<unknown>,
  run: (() => Promise.resolve(undefined)) as (scenarioId: string, signal?: AbortSignal) => Promise<unknown>,
}));
vi.mock("@/api/services/registryService", () => ({
  getRegistry: () => Promise.resolve(REGISTRY),
  checkReform: (reform: Reform, signal?: AbortSignal) => svc.check(reform, signal),
}));
vi.mock("@/api/services/scenarioService", () => ({
  createScenario: (request: CreateScenarioRequest, signal?: AbortSignal) => svc.create(request, signal),
  runScenario: (scenarioId: string, signal?: AbortSignal) => svc.run(scenarioId, signal),
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
  const result = render(<ReformBuilder compare={false} navigate={navigate} />);
  fireEvent.change(await screen.findByLabelText("Title"), { target: { value: "Raise FTC" } });
  fireEvent.change(screen.getByLabelText("Policy"), { target: { value: "working_for_families" } });
  fireEvent.change(screen.getByLabelText("Parameter"), { target: { value: "ftc_rate" } });
  return result;
}
const navigate = vi.fn();

beforeEach(() => vi.clearAllMocks());

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

  it("ignores an old check after editing and submits only the newly confirmed settings", async () => {
    let finishOldCheck!: (result: CheckResult) => void;
    const nextCheck = { ...OK, changes: OK.changes.map((c) => ({ ...c, operand: "8000", resulting: "8000" })) };
    const check = vi.fn<(reform: Reform, signal?: AbortSignal) => Promise<CheckResult>>()
      .mockImplementationOnce(() => new Promise<CheckResult>((resolve) => { finishOldCheck = resolve; }))
      .mockResolvedValue(nextCheck);
    const create = vi.fn<(request: CreateScenarioRequest, signal?: AbortSignal) => Promise<string>>().mockResolvedValue("s1");
    svc.check = check;
    svc.create = create;
    svc.run = () => Promise.resolve({ scenario_id: "s1", run_id: "r1" });
    await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "7000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    const firstSignal = check.mock.calls[0]?.[1] as AbortSignal;

    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "8000" } });
    expect(firstSignal.aborted).toBe(true);
    expect(screen.queryByRole("button", { name: "Run analysis" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    expect(await screen.findByText("8,000")).toBeInTheDocument();
    await act(async () => { finishOldCheck(OK); });
    expect(screen.queryByText("7,000")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Run analysis" }));
    await waitFor(() => expect(create).toHaveBeenCalledOnce());
    const request = create.mock.calls[0]?.[0] as CreateScenarioRequest;
    expect(request.options[0]?.reform.overrides[0]?.value).toBe("8000");
  });

  it("keeps the confirmed settings fixed while a run is pending", async () => {
    svc.check = () => Promise.resolve(OK);
    const create = vi.fn<(request: CreateScenarioRequest, signal?: AbortSignal) => Promise<string>>().mockResolvedValue("s1");
    svc.create = create;
    svc.run = () => new Promise(() => undefined);
    await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "7000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    fireEvent.click(await screen.findByRole("button", { name: "Run analysis" }));
    expect(screen.getByLabelText("Value")).toBeDisabled();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "8000" } });
    expect(screen.getByLabelText("Value")).toHaveValue("7000");
    await waitFor(() => expect(create).toHaveBeenCalledOnce());
    expect((create.mock.calls[0]?.[0] as CreateScenarioRequest).options[0]?.reform.overrides[0]?.value).toBe("7000");
  });

  it("cancels a pending run and does not navigate after the builder unmounts", async () => {
    let finishRun!: (result: { scenario_id: string; run_id: string }) => void;
    svc.check = () => Promise.resolve(OK);
    svc.create = () => Promise.resolve("s1");
    const run = vi.fn<(scenarioId: string, signal?: AbortSignal) => Promise<{ scenario_id: string; run_id: string }>>(() =>
      new Promise((resolve) => { finishRun = resolve; }),
    );
    svc.run = run;
    const view = await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "7000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    fireEvent.click(await screen.findByRole("button", { name: "Run analysis" }));
    await waitFor(() => expect(run).toHaveBeenCalledOnce());
    const signal = run.mock.calls[0]?.[1] as AbortSignal;
    view.unmount();
    expect(signal.aborted).toBe(true);
    await act(async () => { finishRun({ scenario_id: "s1", run_id: "r1" }); });
    expect(navigate).not.toHaveBeenCalled();
  });

  it("checks every retained option before submitting the unchanged comparison definition", async () => {
    const initial: CreateScenarioRequest = {
      title: "Saved comparison", description: "Saved description",
      options: ["A", "B"].map((label) => ({ label, reform: { reform_id: `retained_${label}`, description: `Saved ${label}`, overrides: [{ policy_id: "working_for_families", parameter_id: "ftc_rate", operation: "set", value: "7000" }] } })),
    };
    const check = vi.fn<(reform: Reform, signal?: AbortSignal) => Promise<CheckResult>>().mockResolvedValue(OK);
    const create = vi.fn<(request: CreateScenarioRequest, signal?: AbortSignal) => Promise<string>>().mockResolvedValue("s1");
    svc.check = check; svc.create = create;
    svc.run = () => Promise.resolve({ scenario_id: "s1", run_id: "r1" });
    render(<ReformBuilder compare initial={initial} navigate={navigate} />);
    fireEvent.click(await screen.findByRole("button", { name: "Review before running" }));
    fireEvent.click(await screen.findByRole("button", { name: "Run analysis" }));
    await waitFor(() => expect(create).toHaveBeenCalledOnce());
    expect(check.mock.calls.map(([reform]) => reform)).toEqual(initial.options.map((o) => o.reform));
    expect(create.mock.calls[0]?.[0]).toEqual(initial);
  });

  it("drops a cloned reform id and description once the value is edited", async () => {
    const initial: CreateScenarioRequest = {
      title: "Saved", description: "",
      options: [{ label: "Proposed change", reform: { reform_id: "retained_1", description: "Set to 7000", overrides: [{ policy_id: "working_for_families", parameter_id: "ftc_rate", operation: "set", value: "7000" }] } }],
    };
    const check = vi.fn<(reform: Reform, signal?: AbortSignal) => Promise<CheckResult>>().mockResolvedValue(OK);
    svc.check = check;
    render(<ReformBuilder compare={false} initial={initial} navigate={navigate} />);
    fireEvent.change(await screen.findByLabelText("Value"), { target: { value: "8000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    await waitFor(() => expect(check).toHaveBeenCalledOnce());
    const reform = check.mock.calls[0]![0];
    expect(reform.reform_id).toBe("option_1");
    expect(reform.description).toBe("Proposed change");
    expect(reform.overrides[0]?.value).toBe("8000");
  });

  it("starts only one retry when a busy error is clicked twice", async () => {
    svc.check = () => Promise.resolve(OK);
    const create = vi.fn<(request: CreateScenarioRequest, signal?: AbortSignal) => Promise<string>>().mockResolvedValue("s1");
    const run = vi.fn<(scenarioId: string, signal?: AbortSignal) => Promise<unknown>>()
      .mockRejectedValueOnce(new ApiError("busy", "A run is in progress.", { status: 429 }))
      .mockImplementation(() => new Promise(() => undefined));
    svc.create = create; svc.run = run;
    await fill();
    fireEvent.change(screen.getByLabelText("Value"), { target: { value: "7000" } });
    fireEvent.click(screen.getByRole("button", { name: "Review before running" }));
    fireEvent.click(await screen.findByRole("button", { name: "Run analysis" }));
    const retry = await screen.findByRole("button", { name: "Try again" });
    act(() => { fireEvent.click(retry); fireEvent.click(retry); });
    await waitFor(() => expect(run).toHaveBeenCalledTimes(2));
    expect(create).toHaveBeenCalledTimes(2);
  });
});
