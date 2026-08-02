import Link from "next/link";

import { cn } from "@/lib/utils";

export function BrandMark({
  href = "/",
  size = "md",
  className,
  linked = true,
}: {
  href?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
  linked?: boolean;
}) {
  const sizeClass =
    size === "lg"
      ? "text-4xl sm:text-6xl"
      : size === "sm"
        ? "text-lg"
        : "text-xl";

  const classes = cn(
    "font-heading inline-flex items-center gap-2 font-semibold tracking-tight text-foreground",
    linked && "transition-opacity hover:opacity-80",
    sizeClass,
    className
  );

  const content = (
    <>
      <span
        aria-hidden
        className={cn(
          "inline-block rounded-full bg-honey ring-1 ring-ring/40",
          size === "lg" ? "size-3.5" : size === "sm" ? "size-2" : "size-2.5"
        )}
      />
      HoneyDesk
    </>
  );

  if (!linked) {
    return (
      <p className={classes} aria-label="HoneyDesk">
        {content}
      </p>
    );
  }

  return (
    <Link href={href} className={classes} aria-label="HoneyDesk home">
      {content}
    </Link>
  );
}
