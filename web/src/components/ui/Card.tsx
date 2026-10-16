import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("rounded-lg border border-border bg-surface p-5", className)} {...props} />
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
    <section aria-labelledby={id} className="mt-10">
      <div className="mb-3 flex items-baseline justify-between gap-4">
        <h2 id={id} className="text-xl font-semibold">
          {title}
        </h2>
        {aside}
      </div>
      {children}
    </section>
  );
}
