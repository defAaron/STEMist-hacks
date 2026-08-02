"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import {
  EmptyPanel,
  ErrorPanel,
  LoadingPanel,
} from "@/components/shared/state-panels";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { TechniqueBadge } from "@/components/shared/technique-badge";
import { formatClock, formatRelativeTime, shortId } from "@/lib/format";
import type { HoneyEvent } from "@/lib/types";
import type { LoadState } from "@/hooks/use-dashboard-data";
import { cn } from "@/lib/utils";

export function EventFeed({
  events,
  selectedId,
  highlightedIds,
  state,
  error,
  onSelect,
  onRetry,
}: {
  events: HoneyEvent[];
  selectedId: string | null;
  highlightedIds: Set<string>;
  state: LoadState;
  error: string | null;
  onSelect: (id: string) => void;
  onRetry: () => void;
}) {
  if (state === "loading") {
    return <LoadingPanel label="Listening for traps…" className="min-h-80" />;
  }

  if (state === "error" && events.length === 0) {
    return (
      <ErrorPanel
        description={error ?? "Could not load events."}
        onRetry={onRetry}
        className="min-h-80"
      />
    );
  }

  if (state === "empty" || events.length === 0) {
    return (
      <EmptyPanel
        title="No attacks yet"
        description="Open a decoy and submit a test login, or replay SC-1 to spring the trap."
        className="min-h-80"
      />
    );
  }

  return (
    <ScrollArea className="h-[min(70vh,36rem)] pr-3">
      <ul className="flex flex-col gap-1" aria-label="Event feed" role="listbox">
        {events.map((event) => {
          const selected = event.id === selectedId;
          const highlighted = highlightedIds.has(event.id);
          return (
            <li key={event.id} role="option" aria-selected={selected}>
              <button
                type="button"
                onClick={() => onSelect(event.id)}
                className={cn(
                  "w-full rounded-xl border border-transparent px-3 py-3 text-left transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/40",
                  selected
                    ? "bg-surface honey-glow"
                    : "hover:bg-secondary/70",
                  highlighted && "detonate"
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <TechniqueBadge technique={event.technique} />
                      <SeverityBadge severity={event.severity} />
                      <span className="rounded-md bg-muted px-1.5 py-0.5 text-[11px] uppercase tracking-wide text-muted-foreground">
                        {event.source}
                      </span>
                    </div>
                    <p className="truncate text-sm text-foreground">
                      <span className="font-medium">{event.decoy_id}</span>
                      {event.path ? (
                        <span className="text-muted-foreground">
                          {" "}
                          · {event.path}
                        </span>
                      ) : null}
                    </p>
                    <p className="font-mono text-xs text-muted-foreground">
                      {shortId(event.id)} · {event.ip || "no-ip"}
                    </p>
                  </div>
                  <time
                    dateTime={event.created_at}
                    className="shrink-0 text-right text-xs text-muted-foreground"
                    title={formatClock(event.created_at)}
                  >
                    {formatRelativeTime(event.created_at)}
                  </time>
                </div>
              </button>
            </li>
          );
        })}
      </ul>
      {error ? (
        <p className="mt-3 px-1 text-xs text-destructive" role="status">
          Live updates paused: {error}
        </p>
      ) : null}
    </ScrollArea>
  );
}
