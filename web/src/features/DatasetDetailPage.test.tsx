import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@/api/errors";
import type { DatasetDetail } from "@/domain";
import { expectNoAxeViolations } from "@/test/axe";

import { DatasetDetailPage } from "./DatasetDetailPage";

const NOTE = "Preserved sources are not yet exposed (ADR-0022).";
const service = vi.hoisted(() => ({ getDataset: (): Promise<unknown> => Promise.resolve(undefined) }));
vi.mock("@/api/services/dataService", () => ({
  getDataset: () => service.getDataset(),
  listDatasets: () => Promise.resolve({ datasets: [], populations: [], preserved_sources: { exposed: false, note: NOTE } }),
}));
vi.mock("@/lib/useRouteIds", () => ({ useRouteIds: () => ({ datasetId: "stats_nz_hes" }) }));

const SHA = "a".repeat(64);
const DETAIL: DatasetDetail = {
  dataset_id: "stats_nz_hes",
  snapshots: [
    {
      raw_snapshot_version: 1,
      vintage: "2024",
      sha256: SHA,
      raw_file: "data/raw/x.csv",
      transformation_id: "hes_clean",
      transformation_version: 3,
      source_organisation: "Stats NZ",
      dataset_series: "Household Economic Survey",
      source_url_or_identifier: "https://example.test/hes",
      retrieval_date: "2026-09-01",
      retrieval_method: "manual download",
      observation_reference_period: { from: "2023-07-01", to: "2024-07-01" },
      units: "NZD per year",
      geography_population: "New Zealand households",
      canonical_variable_mapping: ["household_income"],
    },
  ],
  variables: [
    {
      id: "household_income",
      meaning: "Annual household income",
      unit: "NZD",
      frequency: "annual",
      price_basis: "nominal",
      price_base: null,
      measure: "mean",
      geography_population: "New Zealand households",
      valid_from: "2020-01-01",
      valid_to: null,
    },
  ],
  undefined_variables: ["mystery_var"],
  raw_bytes_note: "Raw bytes are not served here.",
};

describe("DatasetDetailPage", () => {
  it("shows publisher, coverage, vintage, retrieval, checksum, transformation, variables, used by and the archive state", async () => {
    service.getDataset = () => Promise.resolve(DETAIL);
    render(<DatasetDetailPage />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading dataset");

    expect(await screen.findByRole("heading", { name: "Household Economic Survey" })).toBeInTheDocument();
    expect(screen.getAllByText("Stats NZ").length).toBeGreaterThan(0);
    expect(screen.getByText("from 2023-07-01, up to but not including 2024-07-01")).toBeInTheDocument();
    expect(screen.getByText("2024")).toBeInTheDocument();
    expect(screen.getByText("2026-09-01")).toBeInTheDocument();
    expect(screen.getByText(`${SHA.slice(0, 12)}…`)).toHaveAttribute("title", SHA);
    expect(screen.getByText("hes_clean v3")).toBeInTheDocument();
    expect(screen.getByText("NZD per year")).toBeInTheDocument();
    expect(screen.getByRole("table", { name: "Canonical variables" })).toBeInTheDocument();
    expect(screen.getByText("2020-01-01 to open")).toBeInTheDocument();
    expect(screen.getByText("mystery_var")).toBeInTheDocument();
    expect(screen.getByText("Raw bytes are not served here.")).toBeInTheDocument();
    expect(screen.getByText("Not recorded")).toBeInTheDocument();
    expect(await screen.findByText("Not yet exposed")).toBeInTheDocument();
    expect(await screen.findByText(NOTE)).toBeInTheDocument();
  });

  it("says plainly when no variables are mapped", async () => {
    service.getDataset = () => Promise.resolve({ ...DETAIL, variables: [], undefined_variables: [] });
    render(<DatasetDetailPage />);
    expect(await screen.findByText("No variables are mapped.")).toBeInTheDocument();
  });

  it("shows the server's message for an unknown dataset", async () => {
    const error = new ApiError("not_found", "No dataset 'x' is catalogued.", { code: "dataset_not_found", status: 404 });
    service.getDataset = () => new Promise((_, reject) => setTimeout(() => reject(error), 0));
    render(<DatasetDetailPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No dataset 'x' is catalogued.");
  });

  it("has no axe violations", async () => {
    service.getDataset = () => Promise.resolve(DETAIL);
    const { container } = render(<DatasetDetailPage />);
    await screen.findByText("Raw bytes are not served here.");
    await expectNoAxeViolations(container);
  });
});
