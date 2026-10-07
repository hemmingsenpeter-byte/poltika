import type { ComponentType } from "react";

import type { Block, BlockOf, BlockType } from "@/domain";

import { MetricCard, type OpenBlock } from "./MetricCard";
import {
  AuditRecord,
  CalculationChain,
  HorizonStrip,
  ListBlockView,
  ModelReferences,
  NoticeBlock,
  SourcesList,
  UnsupportedBlock,
} from "./OtherBlocks";
import { TableBlockView } from "./TableBlock";

type Props<T extends BlockType> = { block: BlockOf<T>; onOpen?: OpenBlock | undefined };

/** One component per block type. A new type on the backend needs one entry
 *  here (TypeScript fails to compile until it has one). Components only show
 *  the values they are given. */
const REGISTRY: { [T in BlockType]: ComponentType<Props<T>> } = {
  metric: MetricCard,
  table: TableBlockView,
  horizon: HorizonStrip,
  list: ListBlockView,
  notice: NoticeBlock,
  sources: SourcesList,
  audit_record: AuditRecord,
  calculation_chain: CalculationChain,
  model_ref: ModelReferences,
};

function titleOf(block: Block): string | null {
  return block.type === "metric" ? null : (block.title ?? null);
}

export function BlockRenderer({ block, onOpen }: { block: Block; onOpen?: OpenBlock | undefined }) {
  const Component = (REGISTRY as Record<string, ComponentType<Props<BlockType>> | undefined>)[block.type];
  const title = titleOf(block);
  return (
    <div id={`block-${block.id}`} className="mt-6 scroll-mt-20 first:mt-0">
      {title && block.type !== "notice" ? <h3 className="mb-2 text-sm font-semibold">{title}</h3> : null}
      {Component ? <Component block={block} onOpen={onOpen} /> : <UnsupportedBlock type={String(block.type)} />}
    </div>
  );
}
