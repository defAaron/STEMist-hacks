"use client";

import { useState } from "react";
import { Download, LoaderCircle } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { downloadStixExport } from "@/lib/api";
import type { HoneyEvent } from "@/lib/types";
import { ApiError } from "@/lib/types";

export function BriefCard({ event }: { event: HoneyEvent }) {
  const [exporting, setExporting] = useState(false);
  const victim =
    event.brief_victim ||
    event.brief?.victim ||
    "Brief is still generating for this event.";
  const it =
    event.brief_it ||
    event.brief?.it ||
    "No IT brief available for this event yet.";
  const actions = event.brief?.actions ?? [];

  async function onExport() {
    setExporting(true);
    try {
      await downloadStixExport(event.id);
      toast.success("STIX export downloaded", {
        description: "Share this JSON with school IT.",
      });
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Export failed unexpectedly.";
      toast.error("Export failed", { description: message });
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="space-y-4">
      <Tabs defaultValue="victim">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <TabsList aria-label="Brief audience">
            <TabsTrigger value="victim">Victim brief</TabsTrigger>
            <TabsTrigger value="it">IT brief</TabsTrigger>
          </TabsList>
          {event.brief_source ? (
            <span className="text-xs text-muted-foreground">
              Source: {event.brief_source}
            </span>
          ) : null}
        </div>
        <TabsContent value="victim" className="mt-3">
          <p className="text-sm leading-relaxed text-foreground text-pretty">
            {victim}
          </p>
        </TabsContent>
        <TabsContent value="it" className="mt-3">
          <p className="text-sm leading-relaxed text-foreground text-pretty">
            {it}
          </p>
        </TabsContent>
      </Tabs>

      {actions.length > 0 ? (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            What to do
          </p>
          <ol className="list-decimal space-y-1 pl-5 text-sm text-foreground">
            {actions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ol>
        </div>
      ) : null}

      <Button
        variant="secondary"
        onClick={() => void onExport()}
        disabled={exporting}
        aria-label="Download STIX JSON to share with school IT"
      >
        {exporting ? (
          <LoaderCircle className="animate-spin" data-icon="inline-start" />
        ) : (
          <Download data-icon="inline-start" />
        )}
        Share with school IT
      </Button>
    </div>
  );
}
