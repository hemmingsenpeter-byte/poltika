import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("rounded-md border border-border bg-surface p-4 shadow-card", className)} {...props} />
  );
}

export function Section({
  title,
  id,
  children,
  aside,
}: {
  title: string;
  id: string;
  children: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <section aria-labelledby={id} className="mt-8">
      <div className="mb-2 flex items-baseline justify-between gap-4">
        <h2 id={id} className="text-base font-semibold">
          {title}
        </h2>
        {aside}
      </div>
      {children}
    </section>
  );
}
