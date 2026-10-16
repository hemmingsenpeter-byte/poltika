import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

const button = cva(
  "inline-flex items-center justify-center gap-2 rounded-md border text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-55",
  {
    variants: {
      variant: {
        primary: "border-accent bg-accent text-accent-contrast hover:border-accent-hover hover:bg-accent-hover",
        secondary: "border-border-strong bg-surface text-ink hover:border-ink hover:bg-surface-muted",
        ghost: "border-transparent bg-transparent text-ink hover:bg-surface-muted",
      },
      // Taller on touch widths (about 40px) and compact from md up.
      size: { sm: "h-9 px-2.5 md:h-8", md: "h-10 px-4 md:h-9", lg: "h-12 px-5 text-base" },
    },
    defaultVariants: { variant: "secondary", size: "md" },
  },
);

export function buttonClasses(options: VariantProps<typeof button> = {}, className?: string): string {
  return cn(button(options), className);
}

export function Button({
  variant,
  size,
  className,
  type = "button",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof button>) {
  return <button type={type} className={buttonClasses({ variant, size }, className)} {...props} />;
}
