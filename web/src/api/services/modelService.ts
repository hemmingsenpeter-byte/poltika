import { getJson } from "../client";
import { ModelCatalogueSchema, ModelDetailSchema } from "../schemas";
import type { ModelCatalogue, ModelDetail } from "@/domain";

export function listModels(signal?: AbortSignal): Promise<ModelCatalogue> {
  return getJson("/api/v1/models", ModelCatalogueSchema, signal);
}

export function getModel(modelId: string, signal?: AbortSignal): Promise<ModelDetail> {
  return getJson(`/api/v1/models/${encodeURIComponent(modelId)}`, ModelDetailSchema, signal);
}
