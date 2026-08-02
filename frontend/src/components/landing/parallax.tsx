"use client";

import {
  useEffect,
  useRef,
  type HTMLAttributes,
  type ReactNode,
} from "react";

import { usePrefersReducedMotion } from "@/hooks/use-prefers-reduced-motion";
import { cn } from "@/lib/utils";

type ParallaxProps = {
  children: ReactNode;
  className?: string;
  /**
   * Scroll factor in px per viewport-height of offset from center.
   * Positive = moves with scroll direction (slower layer feel when small).
   * Keep |speed| under ~40 for a comfortable effect.
   */
  speed?: number;
} & Omit<HTMLAttributes<HTMLDivElement>, "children" | "className" | "style">;

/**
 * Subtle scroll-linked vertical shift. Disabled when reduced motion is preferred.
 * Updates transform via the DOM (no React re-renders on scroll).
 */
export function Parallax({
  children,
  className,
  speed = 24,
  ...rest
}: ParallaxProps) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    const el = ref.current;
    if (!el || reduced) {
      if (el) {
        el.style.transform = "";
        el.style.willChange = "";
      }
      return;
    }

    let frame = 0;
    el.style.willChange = "transform";

    const update = () => {
      const rect = el.getBoundingClientRect();
      const viewH = window.innerHeight || 1;
      const centerOffset = (rect.top + rect.height / 2 - viewH / 2) / viewH;
      const y = centerOffset * speed;
      el.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0)`;
    };

    const onScroll = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(update);
    };

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      el.style.transform = "";
      el.style.willChange = "";
    };
  }, [reduced, speed]);

  return (
    <div ref={ref} className={cn(className)} {...rest}>
      {children}
    </div>
  );
}
