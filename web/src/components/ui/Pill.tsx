import { AlertTriangle, CheckCircle2, CircleSlash, Info, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

export type PillTone = "ok" | "warn" | "bad" | "info" | "neutral";

const TONES: Record<PillTone, { classes: string; icon: LucideIcon }> = {
  ok: { classes: "bg-ok-bg text-ok-fg", icon: CheckCircle2 },
  warn: { classes: "bg-warn-bg text-warn-fg", icon: AlertTriangle },
  bad: { classes: "bg-bad-bg text-bad-fg", icon: CircleSlash },
  info: { classes: "bg-accent-soft text-accent", icon: Info },
  neutral: { classes: "bg-neutral-bg text-neutral-fg", icon: Info },
};

/** A status is never colour alone: every pill carries an icon and its text. */
export function Pill({ tone, children, className }: { tone: PillTone; children: ReactNode; className?: string }) {
  const { classes, icon: Icon } = TONES[tone];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-sm px-2 py-0.5 text-xs font-semibold whitespace-nowrap",
        classes,
        className,
      )}
    >
      <Icon aria-hidden="true" className="size-3.5 shrink-0" />
      {children}
    </span>
  );
}
