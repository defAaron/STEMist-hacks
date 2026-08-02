/** Decorative product preview used as the hero visual (dashboard mock). */
export function ProductVisual({ className }: { className?: string }) {
  return (
    <div
      className={className}
      role="img"
      aria-label="HoneyDesk ops dashboard preview showing a live credential harvest alert, analysis pipeline, and victim brief"
    >
      <div className="overflow-hidden rounded-2xl border border-border/80 bg-surface shadow-[0_24px_60px_-28px_rgba(28,25,23,0.35)]">
        <div className="flex items-center gap-2 border-b border-border/80 bg-muted/60 px-4 py-2.5">
          <span className="size-2.5 rounded-full bg-[#E8B4B0]" />
          <span className="size-2.5 rounded-full bg-honey" />
          <span className="size-2.5 rounded-full bg-[#B8C9B0]" />
          <span className="ml-3 font-mono text-[11px] text-muted-foreground">
            honeydesk.app/dashboard
          </span>
          <span className="ml-auto inline-flex items-center gap-1.5 rounded-md bg-honey-soft px-2 py-0.5 text-[11px] font-medium text-honey-foreground ring-1 ring-honey/70">
            <span className="size-1.5 animate-pulse rounded-full bg-ring" />
            Live
          </span>
        </div>

        <div className="grid gap-3 p-4 sm:grid-cols-[1fr_1.05fr]">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] text-muted-foreground">
              <span>Attacks caught</span>
              <span className="font-heading text-base font-semibold text-foreground">
                12
              </span>
            </div>
            <div className="rounded-xl border border-honey/80 bg-honey-soft/80 p-3">
              <div className="flex flex-wrap gap-1.5">
                <span className="rounded-md bg-honey px-2 py-0.5 text-[11px] font-medium text-honey-foreground">
                  Credential harvest
                </span>
                <span className="rounded-md bg-severity-high/10 px-2 py-0.5 text-[11px] font-medium text-severity-high">
                  High
                </span>
              </div>
              <p className="mt-2 text-sm font-medium text-foreground">
                portal · /login
              </p>
              <p className="mt-1 font-mono text-[11px] text-muted-foreground">
                just now · replay SC-1
              </p>
            </div>
            <div className="rounded-xl border border-border/70 bg-muted/40 p-3 opacity-80">
              <p className="text-sm text-foreground">urgency_pii_scam</p>
              <p className="mt-1 text-[11px] text-muted-foreground">
                scholarship · 2m ago
              </p>
            </div>
          </div>

          <div className="space-y-3 rounded-xl border border-border/70 bg-muted/30 p-3">
            <div className="grid grid-cols-4 gap-1.5">
              {["Capture", "Classify", "Enrich", "Brief"].map((step, i) => (
                <div
                  key={step}
                  className={
                    i < 3
                      ? "rounded-lg bg-honey-soft px-1 py-2 text-center text-[10px] font-medium text-foreground ring-1 ring-honey/60"
                      : "rounded-lg bg-surface px-1 py-2 text-center text-[10px] font-medium text-muted-foreground ring-1 ring-border"
                  }
                >
                  {step}
                </div>
              ))}
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                Victim brief
              </p>
              <p className="mt-1.5 text-xs leading-relaxed text-foreground">
                This page copied a student aid portal to collect a school email
                and password. Change it from the official site and turn on MFA.
              </p>
            </div>
            <div className="inline-flex rounded-md bg-secondary px-2.5 py-1.5 text-[11px] font-medium text-secondary-foreground">
              Share with school IT ↓
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
