"use client";

import Link from "next/link";
import { ExternalLink } from "lucide-react";

import { BrandMark } from "@/components/shared/brand-mark";
import { EthicsFooter } from "@/components/shared/ethics-footer";
import { DetailPanel } from "@/components/dashboard/detail-panel";
import { EventFeed } from "@/components/dashboard/event-feed";
import { ReplayControls } from "@/components/dashboard/replay-controls";
import { StatsBar } from "@/components/dashboard/stats-bar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useDashboardData } from "@/hooks/use-dashboard-data";

export function DashboardShell() {
  const {
    events,
    stats,
    selectedId,
    selectedEvent,
    highlightedIds,
    state,
    error,
    selectEvent,
    refreshNow,
    upsertEvent,
  } = useDashboardData();

  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-border/80 bg-surface/80 px-page py-4 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <BrandMark href="/" size="sm" />
            <div className="flex flex-wrap items-center gap-2">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/decoy/portal">
                  Open portal decoy
                  <ExternalLink data-icon="inline-end" />
                </Link>
              </Button>
            </div>
          </div>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <StatsBar stats={stats} loading={state === "loading"} />
            <ReplayControls onSimulated={upsertEvent} />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-page py-6">
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
          <Card className="bg-surface/90">
            <CardHeader className="border-b">
              <CardTitle className="font-heading">Live feed</CardTitle>
              <CardDescription>
                Newest traps first. Fresh rows highlight for two seconds.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-3">
              <EventFeed
                events={events}
                selectedId={selectedId}
                highlightedIds={highlightedIds}
                state={state}
                error={error}
                onSelect={selectEvent}
                onRetry={() => void refreshNow()}
              />
            </CardContent>
          </Card>

          <Card className="bg-surface/90">
            <CardHeader className="border-b">
              <CardTitle className="font-heading">Event detail</CardTitle>
              <CardDescription>
                Technique, pipeline, victim brief, and school IT export.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <DetailPanel event={selectedEvent} state={state} />
            </CardContent>
          </Card>
        </div>
      </main>

      <EthicsFooter />
    </div>
  );
}
