import { afterEach, describe, expect, it, vi } from "vitest";

import { BLOCKS, workspaceFixture } from "@/test/fixtures/workspace";

import { WorkspaceSchema } from "./schemas";
import { getWorkspace } from "./services/scenarioService";

afterEach(() => vi.unstubAllGlobals());

describe("workspace response validation", () => {
  it("accepts every supported block body", () => {
    const workspace = workspaceFixture();
    workspace.tabs[0]!.blocks = BLOCKS;
    expect(WorkspaceSchema.safeParse(workspace).success).toBe(true);
  });

  it.each([
    ["metric", { values: null }],
    ["table", { columns: null }],
    ["horizon", { years: [{ label: "2026-27", modelled: "yes", note: "" }] }],
    ["list", { items: [null] }],
    ["notice", { tone: "approved" }],
    ["sources", { sources: [{ id: "source" }] }],
    ["audit_record", { fields: [{ label: "ID", value: 123 }] }],
    ["calculation_chain", { steps: [{ result: 123 }] }],
    ["model_ref", { models: {} }],
  ])("rejects a malformed %s body", (type, patch) => {
    const block = BLOCKS.find((b) => b.type === type)!;
    const workspace = workspaceFixture();
    const response = {
      ...workspace,
      tabs: [{ ...workspace.tabs[0], blocks: [{ ...block, ...patch }] }],
    };
    expect(WorkspaceSchema.safeParse(response).success).toBe(false);
  });

  it("rejects a malformed known metric at the service boundary", async () => {
    const workspace = workspaceFixture();
    const response = {
      ...workspace,
      tabs: [{ ...workspace.tabs[0], blocks: [{ id: "broken", type: "metric" }] }],
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true, status: 200, json: () => Promise.resolve(response),
    }));

    await expect(getWorkspace(workspace.scenario.scenario_id))
      .rejects.toMatchObject({ kind: "invalid_response", status: 200 });
  });

  it("keeps an unknown block type available for the unsupported marker", () => {
    const workspace = workspaceFixture();
    workspace.tabs[0]!.blocks = [{ id: "future", type: "heatmap", title: "Future display" }];
    const parsed = WorkspaceSchema.parse(workspace);
    expect(parsed.tabs[0]!.blocks).toEqual([{ id: "future", type: "heatmap", title: "Future display" }]);
  });
});
