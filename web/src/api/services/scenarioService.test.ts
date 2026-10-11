import { afterEach, describe, expect, it, vi } from "vitest";

import { getScenarioDefinition, rerunHouseholdScenario } from "./scenarioService";

function respond(body: unknown) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve(body) }));
}
afterEach(() => vi.unstubAllGlobals());

describe("scenario editing and household rerun services", () => {
  it("retains every override in a loaded definition", async () => {
    const definition = { title: "Saved", description: "", options: [{ label: "A", reform: { reform_id: "a", description: "", overrides: [
      { policy_id: "test", parameter_id: "one", operation: "set", value: "20" },
      { policy_id: "test", parameter_id: "two", operation: "add", value: "30" },
    ] } }] };
    respond(definition);
    await expect(getScenarioDefinition("scenario")).resolves.toEqual(definition);
    expect(fetch).toHaveBeenCalledWith("/api/v1/scenarios/scenario/definition", expect.objectContaining({ method: "GET" }));
  });

  it("rejects malformed saved settings at the service boundary", async () => {
    respond({ title: "Saved", description: "", options: [{ label: "A", reform: { reform_id: "a", description: "", overrides: [{ policy_id: "test", parameter_id: "one", operation: "set", value: 20 }] } }] });
    await expect(getScenarioDefinition("scenario")).rejects.toMatchObject({ kind: "invalid_response" });
  });

  it("uses the legacy household rerun endpoint and validates its returned ID", async () => {
    respond({ original_result_id: "original", new_result_id: "next", changed_artifacts: [], result_changed: false });
    await expect(rerunHouseholdScenario("original")).resolves.toMatchObject({ new_result_id: "next" });
    expect(fetch).toHaveBeenCalledWith("/scenarios/original/rerun", expect.objectContaining({ method: "POST" }));
  });
});
