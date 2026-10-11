import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { parseRouteIds, useRouteIds } from "./useRouteIds";

const pathname = vi.hoisted(() => ({ current: "/" }));
vi.mock("next/navigation", () => ({ usePathname: () => pathname.current }));

const SID = "a".repeat(64);
const RID = "b".repeat(64);

describe("parseRouteIds", () => {
  it("reads a scenario id", () => {
    expect(parseRouteIds(`/scenarios/${SID}`)).toEqual({ scenarioId: SID });
  });

  it("reads scenario and run ids", () => {
    expect(parseRouteIds(`/scenarios/${SID}/runs/${RID}`)).toEqual({ scenarioId: SID, runId: RID });
  });

  it("reads model and dataset ids, ignoring a trailing slash", () => {
    expect(parseRouteIds("/models/wff_engine")).toEqual({ modelId: "wff_engine" });
    expect(parseRouteIds("/data/stats_nz_household_net_worth/")).toEqual({
      datasetId: "stats_nz_household_net_worth",
    });
  });

  it("finds no ids on list pages or unknown paths", () => {
    expect(parseRouteIds("/")).toEqual({});
    expect(parseRouteIds("/models")).toEqual({});
    expect(parseRouteIds("/models/a/b")).toEqual({});
  });

  it("does not accept characters outside the id alphabet", () => {
    expect(parseRouteIds("/models/a%20b")).toEqual({});
    expect(parseRouteIds("/models/a b")).toEqual({});
  });
});

describe("useRouteIds", () => {
  beforeEach(() => {
    pathname.current = "/";
  });

  it("derives ids from usePathname", () => {
    pathname.current = `/scenarios/${SID}/runs/${RID}`;
    const { result } = renderHook(() => useRouteIds());
    expect(result.current).toEqual({ scenarioId: SID, runId: RID });
  });
});
