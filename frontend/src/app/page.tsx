import Link from "next/link";
import { ArrowRight, Hexagon } from "lucide-react";

import { BrandMark } from "@/components/shared/brand-mark";
import { EthicsFooter } from "@/components/shared/ethics-footer";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-full flex-col">
      <div className="relative flex flex-1 flex-col overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10"
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_#FDF6D8_0%,_transparent_55%)]" />
          <div className="soft-drift absolute -right-16 top-10 size-[28rem] rounded-full bg-honey/40 blur-3xl" />
          <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-background to-transparent" />
          <svg
            className="absolute inset-0 h-full w-full opacity-[0.07]"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <pattern
                id="grid"
                width="32"
                height="32"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M32 0H0V32"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        <header className="px-page py-5">
          <div className="mx-auto flex max-w-6xl items-center justify-between">
            <BrandMark size="sm" />
            <nav aria-label="Primary">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/dashboard">Dashboard</Link>
              </Button>
            </nav>
          </div>
        </header>

        <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col justify-center px-page pb-16 pt-6">
          <section className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="fade-rise max-w-xl space-y-7">
              <BrandMark size="lg" linked={false} />
              <h1 className="font-heading text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
                Trap the scammer. Teach the student. Brief the school.
              </h1>
              <p className="max-w-md text-pretty text-base leading-relaxed text-muted-foreground sm:text-lg">
                A defensive honeypot that springs on fake student portals — then
                turns the catch into a plain-English brief.
              </p>
              <div className="flex flex-wrap gap-3">
                <Button size="lg" asChild>
                  <Link href="/dashboard">
                    Open ops dashboard
                    <ArrowRight data-icon="inline-end" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href="/decoy/portal">Try portal decoy</Link>
                </Button>
              </div>
            </div>

            <div
              aria-hidden
              className="relative mx-auto aspect-[4/3] w-full max-w-md fade-rise lg:max-w-none"
            >
              <div className="absolute inset-0 rounded-[2rem] bg-gradient-to-br from-honey via-honey-soft to-secondary honey-glow" />
              <div className="absolute inset-6 rounded-[1.5rem] border border-border/70 bg-surface/85 p-6 shadow-sm backdrop-blur">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="size-2 rounded-full bg-ring" />
                  Live trap spring
                </div>
                <p className="mt-6 font-heading text-2xl font-semibold tracking-tight text-foreground">
                  Capture → Classify → Enrich → Brief
                </p>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                  Judges see the pipeline move. Students get actions they can
                  take. School IT gets a STIX export.
                </p>
                <div className="mt-8 flex items-center gap-3 text-sm text-foreground">
                  <Hexagon className="size-5 text-ring" />
                  Authorized deception for defense class.
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      <EthicsFooter />
    </div>
  );
}
