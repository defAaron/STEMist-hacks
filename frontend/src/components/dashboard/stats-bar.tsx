"use client";

import { Activity, Radio } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { formatRelativeTime } from "@/lib/format";
import { techniqueLabel } from "@/lib/labels";
import type { Stats } from "@/lib/types";

export function StatsBar({
  stats,
  loading,
}: {
  stats: Stats | null;
  loading?: boolean;
}) {
  if (loading && !stats) {
    return (
      <div className="flex flex-wrap items-center gap-3">
        <Skeleton className="h-9 w-36" />
        <Skeleton className="h-9 w-48" />
      </div>
    );
  }

  const attacks = stats?.attacks_caught ?? 0;
  const topTechniques = Object.entries(stats?.by_technique ?? {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
      <div
        className="inline-flex items-center gap-2 rounded-lg bg-honey-soft px-3 py-1.5 ring-1 ring-honey/70"
        aria-live="polite"
      >
        <Activity className="size-3.5 text-ring" aria-hidden />
        <span className="text-muted-foreground">Attacks caught</span>
        <span className="font-heading text-base font-semibold text-foreground tabular-nums">
          {attacks}
        </span>
      </div>

      {stats?.last_event_at ? (
        <div className="inline-flex items-center gap-1.5 text-muted-foreground">
          <Radio className="size-3.5 text-ring" aria-hidden />
          <span>
            Last event {formatRelativeTime(stats.last_event_at)}
            <span className="sr-only"> (includes live captures and replays)</span>
          </span>
        </div>
      ) : null}

      {topTechniques.length > 0 ? (
        <ul className="flex flex-wrap gap-2" aria-label="Technique breakdown">
          {topTechniques.map(([technique, count]) => (
            <li
              key={technique}
              className="rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground"
            >
              {techniqueLabel(technique)} · {count}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
