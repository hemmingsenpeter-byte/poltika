import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

const button = cva(
  "inline-flex items-center justify-center gap-2 rounded-md border text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-60",
  {
    variants: {
      variant: {
        primary: "border-accent bg-accent text-accent-contrast hover:bg-accent-hover",
        secondary: "border-border-strong bg-surface text-ink hover:bg-surface-muted",
        ghost: "border-transparent bg-transparent text-ink hover:bg-surface-muted",
      },
      size: { sm: "h-8 px-2.5", md: "h-9 px-3.5" },
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
