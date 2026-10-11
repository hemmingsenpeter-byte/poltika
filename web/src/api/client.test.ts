import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { getJson, parseErrorBody } from "./client";
import { ApiError } from "./errors";

const Schema = z.object({ ok: z.boolean() });

function respond(status: number, body: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: status < 400, status, json: () => Promise.resolve(body) }),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("parseErrorBody", () => {
  it("maps a coded 503 to unavailable", () => {
    const error = parseErrorBody(503, {
      detail: { code: "scenario_storage_unavailable", message: "Scenario storage is not configured here." },
    });
    expect(error).toMatchObject({
      kind: "unavailable",
      code: "scenario_storage_unavailable",
      message: "Scenario storage is not configured here.",
      status: 503,
    });
  });

  it("maps 404 to not_found, 429 to busy and 422 to invalid", () => {
    expect(parseErrorBody(404, { detail: { code: "x", message: "No such model." } }).kind).toBe("not_found");
    expect(parseErrorBody(429, { detail: { code: "busy", message: "Another analysis is running." } }).kind).toBe("busy");
    expect(parseErrorBody(422, { detail: [{ loc: ["body"], msg: "bad" }] }).kind).toBe("invalid");
    expect(parseErrorBody(500, {}).kind).toBe("server");
  });

  it("accepts a plain string detail from a legacy route", () => {
    const error = parseErrorBody(404, { detail: "Run not found" });
    expect(error).toMatchObject({ kind: "not_found", message: "Run not found" });
    expect(error.code).toBeUndefined();
  });

  it("falls back to a fixed message without a usable body", () => {
    expect(parseErrorBody(503, undefined).message).toMatch(/not available/i);
  });
});

describe("getJson", () => {
  it("sends a same-origin JSON request and returns parsed data", async () => {
    respond(200, { ok: true });
    await expect(getJson("/x", Schema)).resolves.toEqual({ ok: true });
    expect(fetch).toHaveBeenCalledWith(
      "/x",
      expect.objectContaining({ credentials: "same-origin", headers: { Accept: "application/json" } }),
    );
  });

  it("raises invalid_response when the body does not match the schema", async () => {
    respond(200, { ok: "yes" });
    await expect(getJson("/x", Schema)).rejects.toMatchObject({ kind: "invalid_response" });
  });

  it("raises a typed error for an HTTP failure", async () => {
    respond(503, { detail: { code: "catalogue_unavailable", message: "The model registry here is invalid." } });
    const error = await getJson("/x", Schema).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ kind: "unavailable", code: "catalogue_unavailable" });
  });

  it("raises network when fetch itself fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockImplementation(() => Promise.reject(new TypeError("Failed to fetch"))));
    await expect(getJson("/x", Schema)).rejects.toMatchObject({ kind: "network" });
  });
});
