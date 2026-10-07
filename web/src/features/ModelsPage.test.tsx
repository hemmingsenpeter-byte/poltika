import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { ModelCatalogue } from "@/domain";

import { ModelsPage } from "./ModelsPage";

// A plain function rather than vi.fn(): vitest 4 reports a rejection from a
// spied function's result as unhandled, though the page handles it.
const service = vi.hoisted(() => ({ listModels: (): Promise<unknown> => Promise.resolve(undefined) }));
vi.mock("@/api/services/modelService", () => ({ listModels: () => service.listModels() }));

const CATALOGUE: ModelCatalogue = {
  validation_levels: ["not_validated", "spec_validated"],
  models: [
    {
      id: "wff_engine",
      name: "Working for Families engine",
      kind: "engine",
      version: "0.1.0",
      purpose: "Calculates Working for Families entitlements.",
      policy_versions: { working_for_families: "0.1.0" },
      depends_on: [],
      validation_level: "spec_validated",
      label: "spec_validated",
    },
    {
      id: "combined_runner",
      name: "Combined runner",
      kind: "runner",
      version: "0.1.0",
      purpose: "Runs both engines for one household.",
      policy_versions: {},
      depends_on: ["wff_engine"],
      validation_level: "not_validated",
      label: "not_validated",
    },
  ],
};


describe("ModelsPage", () => {
  it("shows a loading state, then cards grouped by kind with a validation pill", async () => {
    service.listModels = () => Promise.resolve(CATALOGUE);
    render(<ModelsPage />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading models");

    expect(await screen.findByText("Working for Families engine")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Engines" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Runners" })).toBeInTheDocument();
    expect(screen.getByText("Spec validated")).toBeInTheDocument();
    expect(screen.getByText("Not validated")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Working for Families engine/ })).toHaveAttribute(
      "href",
      "/models/wff_engine",
    );
  });

  it("shows the server's message when the catalogue is unavailable", async () => {
    const error = new ApiError("unavailable", "The model registry here is invalid.", {
      code: "catalogue_unavailable",
      status: 503,
    });
    // Rejected on a later tick, as a real network call would be.
    service.listModels = () => new Promise((_, reject) => setTimeout(() => reject(error), 0));
    render(<ModelsPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("The model registry here is invalid.");
  });

  it("shows an empty state for no models", async () => {
    service.listModels = () => Promise.resolve({ validation_levels: [], models: [] });
    render(<ModelsPage />);
    expect(await screen.findByText("No models are registered")).toBeInTheDocument();
  });
});
