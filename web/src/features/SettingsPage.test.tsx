import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

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

const state: { meta: { status: "loading" } | { status: "ready"; data: Meta } } = { meta: { status: "loading" } };

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
});
