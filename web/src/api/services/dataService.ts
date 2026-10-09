import { getJson } from "../client";
import { DatasetCatalogueSchema, DatasetDetailSchema } from "../schemas";
import type { DatasetCatalogue, DatasetDetail } from "@/domain";

export function listDatasets(signal?: AbortSignal): Promise<DatasetCatalogue> {
  return getJson("/api/v1/datasets", DatasetCatalogueSchema, signal);
}

export function getDataset(datasetId: string, signal?: AbortSignal): Promise<DatasetDetail> {
  return getJson(`/api/v1/datasets/${encodeURIComponent(datasetId)}`, DatasetDetailSchema, signal);
}
