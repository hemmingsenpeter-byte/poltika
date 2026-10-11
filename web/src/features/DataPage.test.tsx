import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { DatasetCatalogue } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

import { DataPage } from "./DataPage";

const service = vi.hoisted(() => ({ listDatasets: (): Promise<unknown> => Promise.resolve(undefined) }));
vi.mock("@/api/services/dataService", () => ({ listDatasets: () => service.listDatasets() }));

const NOTE = "Preserved sources are not yet exposed (ADR-0022).";
const CATALOGUE: DatasetCatalogue = {
  datasets: [
    {
      dataset_id: "stats_nz_hes",
      source_organisation: "Stats NZ",
      dataset_series: "Household Economic Survey",
      latest_snapshot_version: 2,
      latest_vintage: "2024",
      latest_retrieval_date: "2026-09-01",
      observation_reference_period: { from: "2023-07-01", to: "2024-07-01" },
      snapshots: 2,
      variables: 5,
    },
  ],
  populations: [
    { population_id: "synthetic_nz", version: 1, synthetic: true, households: 1000, sources: ["Assumption A"] },
  ],
  preserved_sources: { exposed: false, note: NOTE },
};

describe("DataPage", () => {
  it("lists datasets with vintage, retrieval, coverage, a synthetic population and the not-yet-exposed archive", async () => {
    service.listDatasets = () => Promise.resolve(CATALOGUE);
    render(<DataPage />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading datasets");
    expect(await screen.findByText("Household Economic Survey")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Household Economic Survey/ })).toHaveAttribute("href", "/data/stats_nz_hes");
    expect(screen.getByText("from 2023-07-01, up to but not including 2024-07-01")).toBeInTheDocument();
    expect(screen.getByText("2026-09-01")).toBeInTheDocument();
    expect(screen.getByText("Synthetic: not an estimate for New Zealand")).toBeInTheDocument();
    expect(screen.getByText("Not yet available")).toBeInTheDocument();
    expect(screen.getByText(NOTE)).toBeInTheDocument();
  });

  it("shows an empty state and a server error", async () => {
    service.listDatasets = () => Promise.resolve({ ...CATALOGUE, datasets: [], populations: [] });
    const { unmount } = render(<DataPage />);
    expect(await screen.findByText("No datasets are registered")).toBeInTheDocument();
    expect(screen.getByText("No population specification is registered")).toBeInTheDocument();
    unmount();

    const { ApiError } = await import("@/api/errors");
    const error = new ApiError("unavailable", "The dataset catalogue here is invalid.", { code: "catalogue_unavailable", status: 503 });
    service.listDatasets = () => new Promise((_, reject) => setTimeout(() => reject(error), 0));
    render(<DataPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("The dataset catalogue here is invalid.");
  });

  it("has no axe violations", async () => {
    service.listDatasets = () => Promise.resolve(CATALOGUE);
    const { container } = render(<DataPage />);
    await screen.findByText("Household Economic Survey");
    await expectNoAxeViolations(container);
  });
});
