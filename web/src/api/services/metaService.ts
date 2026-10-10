import { getJson } from "../client";
import { MetaSchema, RegistrySchema } from "../schemas";
import type { Meta, Registry } from "@/domain";

export function getMeta(signal?: AbortSignal): Promise<Meta> {
  return getJson("/api/v1/meta", MetaSchema, signal);
}

/** The supported instruments and parameters (the Workbench registry). */
export function getRegistry(signal?: AbortSignal): Promise<Registry> {
  return getJson("/workbench/registry", RegistrySchema, signal);
}
