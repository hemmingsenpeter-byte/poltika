import { CopyButton } from "./CopyButton";

/** An identifier in monospace, shortened for the eye, whole for the copy button
 *  and for screen readers. */
export function IdChip({ id, label }: { id: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <span className="font-mono text-xs" title={id}>
        {id.length > 16 ? `${id.slice(0, 12)}…` : id}
        <span className="sr-only"> {id}</span>
      </span>
      <CopyButton text={id} label={`Copy ${label}`} />
    </span>
  );
}
