import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { ModelDetail } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

import { ModelDetailPage } from "./ModelDetailPage";

const service = vi.hoisted(() => ({ getModel: (): Promise<unknown> => Promise.resolve(undefined) }));
vi.mock("@/api/services/modelService", () => ({ getModel: () => service.getModel() }));
const route = vi.hoisted(() => ({ ids: { modelId: "combined_runner" } as { modelId?: string } }));
vi.mock("@/lib/useRouteIds", () => ({ useRouteIds: () => route.ids }));

const DETAIL: ModelDetail = {
  label: "not_validated",
  used_by: ["api_service"],
  validation_levels: ["not_validated", "spec_validated"],
  model: {
    id: "combined_runner",
    name: "Combined runner",
    kind: "runner",
    version: "0.1.0",
    version_basis: "package version",
    policy_versions: { working_for_families: "0.1.0" },
    owner: "Poltika",
    purpose: "Runs both engines for one household.",
    entry_points: [{ module: "poltika.runner", function: "run" }],
    depends_on: ["wff_engine"],
    validation: {
      level: "spec_validated",
      basis: "Spec cases only.",
      cases: [
        { kind: "spec", path: "policy_specs/x/spec_cases.yaml", count: 12 },
        { kind: "golden", path: "tests/golden.yaml", count: "unknown" },
      ],
      tests: ["tests/unit/test_runner.py"],
      reviews: [],
      open_items: ["Benchmark pending."],
    },
    evidence_classes_consumed: ["Rule", "Scenario"],
    evidence_note: "Reads cited rules and caller scenarios.",
    limitations: [{ text: "Two engines only.", source: "specification.md" }],
    model_risks: [],
    change_log: [
      { date: "2026-10-01", change: "Added runner", why: "Combined run", evidence: "PR 1", validation_rerun: "yes", approval: "Pete" },
    ],
  },
};

describe("ModelDetailPage", () => {
  it("shows status, version basis, cases, tests, limitations, dependencies, used by and change log", async () => {
    service.getModel = () => Promise.resolve(DETAIL);
    render(<ModelDetailPage />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading model");

    expect(await screen.findByRole("heading", { name: "Combined runner" })).toBeInTheDocument();
    expect(screen.getByText("(package version)")).toBeInTheDocument();
    expect(screen.getByText(/weakest along its dependencies: Not validated/)).toBeInTheDocument();
    expect(screen.getByText("Not recorded")).toBeInTheDocument();
    expect(screen.getByRole("table", { name: "Validation cases" })).toBeInTheDocument();
    expect(screen.getByText("tests/unit/test_runner.py")).toBeInTheDocument();
    expect(screen.getByText("No reviews are listed.")).toBeInTheDocument();
    expect(screen.getByText("Two engines only.")).toBeInTheDocument();
    expect(screen.getByText("No risks are listed.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "wff_engine" })).toHaveAttribute("href", "/models/wff_engine");
    expect(screen.getByRole("link", { name: "api_service" })).toHaveAttribute("href", "/models/api_service");
    expect(within(screen.getByRole("table", { name: "Change log" })).getByText("Added runner")).toBeInTheDocument();
  });

  it("shows the server's message for an unknown model", async () => {
    const error = new ApiError("not_found", "No model 'x' is registered.", { code: "model_not_found", status: 404 });
    service.getModel = () => new Promise((_, reject) => setTimeout(() => reject(error), 0));
    render(<ModelDetailPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No model 'x' is registered.");
  });

  it("has no axe violations", async () => {
    service.getModel = () => Promise.resolve(DETAIL);
    const { container } = render(<ModelDetailPage />);
    await screen.findByRole("heading", { name: "Combined runner" });
    await expectNoAxeViolations(container);
  });
});
