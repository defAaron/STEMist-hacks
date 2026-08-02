import {
  EmptyPanel,
  LoadingPanel,
} from "@/components/shared/state-panels";
import { SeverityBadge } from "@/components/shared/severity-badge";
import { TechniqueBadge } from "@/components/shared/technique-badge";
import { BriefCard } from "@/components/dashboard/brief-card";
import { PipelinePanel } from "@/components/dashboard/pipeline-panel";
import { Separator } from "@/components/ui/separator";
import { formatClock, shortId } from "@/lib/format";
import { formatDataTarget } from "@/lib/labels";
import type { HoneyEvent } from "@/lib/types";
import type { LoadState } from "@/hooks/use-dashboard-data";

export function DetailPanel({
  event,
  state,
}: {
  event: HoneyEvent | null;
  state: LoadState;
}) {
  if (state === "loading" && !event) {
    return <LoadingPanel label="Loading event detail…" className="min-h-80" />;
  }

  if (!event) {
    return (
      <EmptyPanel
        title="Select an event"
        description="Pick a row from the feed to inspect technique, pipeline, and the victim brief."
        className="min-h-80"
      />
    );
  }

  return (
    <div className="space-y-5 fade-rise">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <TechniqueBadge technique={event.technique} />
          <SeverityBadge severity={event.severity} />
          <span className="rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">
            score {event.score}
          </span>
          <span className="rounded-md bg-muted px-2 py-0.5 text-xs uppercase tracking-wide text-muted-foreground">
            {event.pipeline_status}
          </span>
        </div>
        <div>
          <h2 className="font-heading text-xl font-semibold tracking-tight">
            {event.decoy_id}
            {event.scenario_id ? ` · ${event.scenario_id}` : ""}
          </h2>
          <p className="mt-1 font-mono text-xs text-muted-foreground">
            {shortId(event.id)} · {formatClock(event.created_at)} ·{" "}
            {event.source}
          </p>
        </div>
      </header>

      <section className="space-y-2" aria-labelledby="pipeline-heading">
        <h3
          id="pipeline-heading"
          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
        >
          Pipeline
        </h3>
        <PipelinePanel event={event} />
      </section>

      <Separator />

      <section className="space-y-2" aria-labelledby="reasons-heading">
        <h3
          id="reasons-heading"
          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
        >
          Why it matched
        </h3>
        {event.reasons.length > 0 ? (
          <ul className="space-y-1.5 text-sm text-foreground">
            {event.reasons.map((reason) => (
              <li key={reason} className="flex gap-2">
                <span
                  className="mt-2 size-1.5 shrink-0 rounded-full bg-ring"
                  aria-hidden
                />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">No reasons yet.</p>
        )}
      </section>

      <section className="space-y-2" aria-labelledby="data-heading">
        <h3
          id="data-heading"
          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
        >
          Data they tried to steal
        </h3>
        {event.data_targeted.length > 0 ? (
          <ul className="flex flex-wrap gap-2">
            {event.data_targeted.map((item) => (
              <li
                key={item}
                className="rounded-md bg-secondary px-2.5 py-1 text-xs text-secondary-foreground"
              >
                {formatDataTarget(item)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">None listed.</p>
        )}
      </section>

      {(event.geo?.label || event.email_domain) && (
        <section className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
          {event.geo?.label ? (
            <p>
              <span className="font-medium text-foreground">Geo · </span>
              {event.geo.label}
            </p>
          ) : null}
          {event.email_domain ? (
            <p>
              <span className="font-medium text-foreground">Email domain · </span>
              {event.email_domain}
            </p>
          ) : null}
        </section>
      )}

      <Separator />

      <section className="space-y-2" aria-labelledby="brief-heading">
        <h3
          id="brief-heading"
          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
        >
          Brief
        </h3>
        <BriefCard event={event} />
      </section>
    </div>
  );
}
