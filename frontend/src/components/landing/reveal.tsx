"use client";

import { useEffect, useState, type CSSProperties, type ReactNode } from "react";

import { cn } from "@/lib/utils";

type RevealTag = "div" | "li" | "section" | "article";

type RevealProps = {
  children: ReactNode;
  className?: string;
  /** Stagger delay after the element enters the viewport. */
  delayMs?: number;
  as?: RevealTag;
  /** How much of the element must be visible before revealing. */
  threshold?: number;
};

/**
 * One-shot fade/rise when the element enters the viewport.
 * Respects prefers-reduced-motion via CSS.
 */
export function Reveal({
  children,
  className,
  delayMs = 0,
  as = "div",
  threshold = 0.18,
}: RevealProps) {
  const [node, setNode] = useState<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!node) return;

    // CSS already forces full opacity under prefers-reduced-motion.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry?.isIntersecting) return;
        setVisible(true);
        observer.disconnect();
      },
      { threshold, rootMargin: "0px 0px -6% 0px" }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [node, threshold]);

  const style: CSSProperties | undefined =
    delayMs > 0 ? { transitionDelay: `${delayMs}ms` } : undefined;

  const shared = {
    ref: setNode,
    className: cn(
      "scroll-reveal",
      visible && "scroll-reveal-visible",
      className
    ),
    style,
  };

  if (as === "li") {
    return <li {...shared}>{children}</li>;
  }
  if (as === "section") {
    return <section {...shared}>{children}</section>;
  }
  if (as === "article") {
    return <article {...shared}>{children}</article>;
  }
  return <div {...shared}>{children}</div>;
}
