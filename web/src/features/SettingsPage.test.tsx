import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import { DEFAULT_CAPABILITIES } from "@/config/capabilities";
import type { Meta } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

import { SettingsPage } from "./SettingsPage";

const META: Meta = {
  service: "poltika",
  api_version: "v1",
  package_version: "0.1.0",
  build: { commit: null, note: "The commit the hosting platform reports for this deployment." },
  policies: [
    { policy_id: "working_for_families", policy_version: "0.1.0", status: "approved", reference_period: { from: "2026-04-01", to: "2027-04-01" } },
    { policy_id: "accommodation_supplement", policy_version: "0.1.1", status: "approved", reference_period: { from: "2026-03-02", to: "2027-04-01" } },
  ],
  population: { population_id: "toy_population", version: 1, synthetic: true, label: "Synthetic development population, not an estimate for New Zealand." },
  access: { password_required: false },
  capabilities: {},
} as Meta;

const state: { meta: { status: "loading" } | { status: "error"; error: unknown } | { status: "ready"; data: Meta } } = { meta: { status: "loading" } };

vi.mock("@/components/layout/MetaProvider", () => ({
  useMeta: () => ({ meta: state.meta, capabilities: DEFAULT_CAPABILITIES }),
}));

describe("SettingsPage", () => {
  it("shows each policy version, the population and the build", async () => {
    state.meta = { status: "ready", data: META };
    const { container } = render(<SettingsPage />);
    const policies = within(screen.getByRole("region", { name: "Policy versions" }));
    expect(policies.getByText("Working for families")).toBeInTheDocument();
    expect(policies.getByText("0.1.0")).toBeInTheDocument();
    expect(policies.getByText("0.1.1")).toBeInTheDocument();
    expect(screen.getByText("Synthetic development population, not an estimate for New Zealand.")).toBeInTheDocument();
    expect(screen.getByText("Not reported by the host")).toBeInTheDocument();
    await expectNoAxeViolations(container);
  });

  it("says it is loading until the metadata arrives", () => {
    state.meta = { status: "loading" };
    render(<SettingsPage />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading settings");
  });

  it("shows the API error when the metadata fails", () => {
    state.meta = { status: "error", error: new ApiError("server", "The server failed.", { status: 500, code: "boom" }) };
    render(<SettingsPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("The server failed.");
    expect(screen.getByRole("alert")).toHaveTextContent("boom");
  });

  it("says so when no policy is loaded and no population is configured", () => {
    state.meta = { status: "ready", data: { ...META, policies: [], population: null } as Meta };
    render(<SettingsPage />);
    expect(screen.getByText("No policy is loaded.")).toBeInTheDocument();
    expect(screen.getByText("No population is configured here.")).toBeInTheDocument();
  });

  it("shows Unversioned and a plain status for a policy that is not approved", () => {
    const draft = { policy_id: "draft_policy", policy_version: null, status: "under_review", reference_period: { from: "2026-04-01", to: "2027-04-01" } };
    state.meta = { status: "ready", data: { ...META, policies: [draft] } as Meta };
    render(<SettingsPage />);
    const policies = within(screen.getByRole("region", { name: "Policy versions" }));
    expect(policies.getByText("Unversioned")).toBeInTheDocument();
    expect(policies.getByText("Under review")).toBeInTheDocument();
    expect(policies.queryByText("Approved")).not.toBeInTheDocument();
  });

  it("shows the build commit the API reports", () => {
    state.meta = { status: "ready", data: { ...META, build: { ...META.build, commit: "abc1234def" } } as Meta };
    render(<SettingsPage />);
    expect(screen.getByText("abc1234def")).toBeInTheDocument();
    expect(screen.queryByText("Not reported by the host")).not.toBeInTheDocument();
  });

  it("pins how ids and statuses are shown: humanised, with the API value kept as text", () => {
    state.meta = { status: "ready", data: META };
    render(<SettingsPage />);
    const policies = within(screen.getByRole("region", { name: "Policy versions" }));
    expect(policies.getByText("Accommodation supplement")).toBeInTheDocument();
    expect(policies.queryByText("accommodation_supplement")).not.toBeInTheDocument();
    expect(policies.getAllByText("Approved")).toHaveLength(2);
  });
});
