import { describe, expect, it } from "vitest";

import { DEFAULT_CAPABILITIES, resolveCapabilities } from "./capabilities";
import { isActive, NAVIGATION, visibleNavigation } from "./navigation";

describe("navigation", () => {
  it("shows Home, Scenarios, Models, Data and Settings by default", () => {
    expect(visibleNavigation(DEFAULT_CAPABILITIES).map((i) => i.label)).toEqual([
      "Home",
      "Scenarios",
      "Models",
      "Data",
      "Settings",
    ]);
  });

  it("declares Explore, Evidence, Assurance and Admin behind capabilities that are off", () => {
    const gated = NAVIGATION.filter((i) => i.capability !== undefined).map((i) => i.label);
    expect(gated).toEqual(["Explore", "Evidence", "Assurance", "Admin"]);
    for (const item of NAVIGATION) {
      if (item.capability) expect(DEFAULT_CAPABILITIES[item.capability]).toBe(false);
    }
  });

  it("shows an item once its capability is on", () => {
    const capabilities = resolveCapabilities({ outcome_explorer: true });
    expect(visibleNavigation(capabilities).map((i) => i.label)).toContain("Explore");
    expect(visibleNavigation(capabilities).map((i) => i.label)).not.toContain("Evidence");
  });

  it("marks a section active from its path", () => {
    const models = NAVIGATION.find((i) => i.id === "models")!;
    const home = NAVIGATION.find((i) => i.id === "home")!;
    expect(isActive(models, "/models/wff_engine")).toBe(true);
    expect(isActive(models, "/modelsx")).toBe(false);
    expect(isActive(home, "/models")).toBe(false);
  });
});

describe("resolveCapabilities", () => {
  it("defaults to policy comparison only", () => {
    expect(Object.entries(resolveCapabilities()).filter(([, on]) => on)).toEqual([["policy_comparison", true]]);
  });

  it("takes values from meta and ignores unknown keys", () => {
    const resolved = resolveCapabilities({ policy_comparison: false, monte_carlo: true, invented: true });
    expect(resolved.policy_comparison).toBe(false);
    expect(resolved.monte_carlo).toBe(true);
    expect("invented" in resolved).toBe(false);
  });
});
