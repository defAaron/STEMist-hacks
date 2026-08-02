"use client";

import { useState } from "react";
import { Play, LoaderCircle } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { postSimulate } from "@/lib/api";
import { SCENARIOS } from "@/lib/labels";
import type { HoneyEvent, ScenarioId } from "@/lib/types";
import { ApiError } from "@/lib/types";

export function ReplayControls({
  onSimulated,
}: {
  onSimulated: (event: HoneyEvent) => void;
}) {
  const [pending, setPending] = useState<ScenarioId | null>(null);

  async function run(scenarioId: ScenarioId) {
    setPending(scenarioId);
    try {
      const event = await postSimulate(scenarioId);
      onSimulated(event);
      toast.success(`${scenarioId} replayed`, {
        description: "Pipeline complete — check the feed.",
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Replay failed. Is the API running?";
      toast.error("Replay failed", { description: message });
    } finally {
      setPending(null);
    }
  }

  return (
    <div
      className="flex flex-wrap items-center gap-2"
      role="group"
      aria-label="Replay seeded scenarios"
    >
      {SCENARIOS.map((scenario) => {
        const isBusy = pending === scenario.id;
        return (
          <Tooltip key={scenario.id}>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                disabled={pending !== null}
                onClick={() => void run(scenario.id)}
                aria-label={`${scenario.label}: ${scenario.description}`}
              >
                {isBusy ? (
                  <LoaderCircle
                    className="animate-spin"
                    data-icon="inline-start"
                  />
                ) : (
                  <Play data-icon="inline-start" />
                )}
                {scenario.label}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{scenario.description}</TooltipContent>
          </Tooltip>
        );
      })}
    </div>
  );
}
