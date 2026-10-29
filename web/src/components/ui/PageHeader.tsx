import type { ReactNode } from "react";

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <header className="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-border pb-5">
      <div className="min-w-0">
        <h1 className="text-3xl font-semibold tracking-tight break-words">{title}</h1>
        {description ? <p className="mt-2 max-w-3xl text-base text-muted">{description}</p> : null}
      </div>
      {actions}
    </header>
  );
}
