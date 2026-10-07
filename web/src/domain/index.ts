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
export type {
  CheckResult,
  HouseholdExample,
  Instrument,
  Registry,
  RegistryParameter,
  ValidInstrument,
} from "@/api/schemas";

/** The scenario workspace, as generated from the backend contract. */
export type Workspace = Omit<S["Workspace"], "tabs"> & { tabs: Tab[] };
export type Tab = Omit<S["Tab"], "blocks"> & { blocks: Block[] };
export type TabId = Tab["id"];
type KnownBlock = S["Tab"]["blocks"][number];
/** Future block types keep their common fields so the renderer can name the
 * unsupported type. Known block bodies are validated at the service boundary. */
export type UnknownBlock = { id: string; type: string; title?: string | null };
export type Block = KnownBlock | UnknownBlock;
export type BlockType = KnownBlock["type"];
export type BlockOf<T extends BlockType> = Extract<KnownBlock, { type: T }>;
export type MetricBlock = S["MetricBlock"];
export type MetricValue = S["MetricValue"];
export type RunCreated = S["RunCreated"];
