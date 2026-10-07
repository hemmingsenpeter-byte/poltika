/** Domain types: the generated OpenAPI schema, re-exported under the names
 *  components use. Components import from here, never from `schema.gen.ts`. */
import type { components } from "@/api/schema.gen";

type S = components["schemas"];

export type Meta = S["Meta"];
export type PolicyVersion = S["PolicyVersion"];
export type Period = S["Period"];

export type ModelSummary = S["ModelSummary"];
export type ModelCatalogue = S["ModelCatalogue"];
export type ModelDetail = S["ModelDetail"];
export type Model = S["Model"];
export type ValidationCase = S["ValidationCase"];

export type DatasetSummary = S["DatasetSummary"];
export type DatasetCatalogue = S["DatasetCatalogue"];
export type DatasetDetail = S["DatasetDetail"];
export type DatasetSnapshot = S["DatasetSnapshot"];
export type Variable = S["Variable"];
export type PopulationSpecSummary = S["PopulationSpecSummary"];

/** `created_at` is declared `Any` by the backend; it is an ISO timestamp. */
export type ScenarioItem = Omit<S["ScenarioItem"], "created_at"> & { created_at: string };
export type ScenarioList = { items: ScenarioItem[]; total: number };
export type ScenarioKind = ScenarioItem["kind"];

/** `GET /workbench/registry` is an untyped payload on the backend, so these
 *  are described by the zod schema in `api/schemas.ts`. */
export type { Instrument, Registry, RegistryParameter } from "@/api/schemas";
