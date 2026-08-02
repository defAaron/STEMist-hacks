import { Check, CircleDashed, LoaderCircle, X } from "lucide-react";

import {
  PIPELINE_STEP_LABELS,
  PIPELINE_STEP_ORDER,
} from "@/lib/labels";
import type { HoneyEvent, PipelineStep } from "@/lib/types";
import { cn } from "@/lib/utils";

function stepStatus(
  steps: PipelineStep[],
  name: string,
  pipelineStatus: string
): "pending" | "running" | "ok" | "failed" {
  const match = [...steps].reverse().find((step) => step.step === name);
  if (match) {
    if (match.status === "failed" || match.status === "error") return "failed";
    return "ok";
  }

  if (pipelineStatus === "failed") return "pending";

  const firstMissing = PIPELINE_STEP_ORDER.find(
    (step) => !steps.some((entry) => entry.step === step)
  );
  if (firstMissing === name && pipelineStatus === "running") return "running";
  return "pending";
}

export function PipelinePanel({ event }: { event: HoneyEvent | null }) {
  const steps = event?.pipeline_steps ?? [];
  const status = event?.pipeline_status ?? "running";

  return (
    <div aria-label="Analysis pipeline">
      <ol className="grid gap-2 sm:grid-cols-5">
        {PIPELINE_STEP_ORDER.map((name, index) => {
          const state = event
            ? stepStatus(steps, name, status)
            : "pending";
          return (
            <li
              key={name}
              className={cn(
                "relative flex min-h-16 flex-col justify-between rounded-xl border px-3 py-2 transition-colors",
                state === "ok" && "border-honey/80 bg-honey-soft",
                state === "running" && "border-ring/50 bg-surface",
                state === "failed" && "border-destructive/40 bg-destructive/5",
                state === "pending" && "border-border bg-muted/40"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <StatusIcon state={state} />
              </div>
              <p className="font-heading text-sm font-semibold text-foreground">
                {PIPELINE_STEP_LABELS[name] ?? name}
              </p>
            </li>
          );
        })}
      </ol>
      {!event ? (
        <p className="mt-3 text-xs text-muted-foreground">
          Select an event to watch Capture → Classify → Enrich → Brief.
        </p>
      ) : null}
    </div>
  );
}

function StatusIcon({
  state,
}: {
  state: "pending" | "running" | "ok" | "failed";
}) {
  if (state === "ok") {
    return <Check className="size-3.5 text-ring" aria-label="Complete" />;
  }
  if (state === "running") {
    return (
      <LoaderCircle
        className="size-3.5 animate-spin text-ring"
        aria-label="Running"
      />
    );
  }
  if (state === "failed") {
    return <X className="size-3.5 text-destructive" aria-label="Failed" />;
  }
  return (
    <CircleDashed className="size-3.5 text-muted-foreground" aria-label="Pending" />
  );
}
