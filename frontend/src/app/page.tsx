import Link from "next/link";
import {
  ArrowRight,
  GraduationCap,
  Radio,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { ProductVisual } from "@/components/landing/product-visual";
import { BrandMark } from "@/components/shared/brand-mark";
import { EthicsFooter } from "@/components/shared/ethics-footer";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const STEPS = [
  {
    title: "Deploy a decoy",
    body: "Open a fake aid portal, scholarship form, or Discord verify page built for authorized training.",
  },
  {
    title: "Watch the spring",
    body: "The ops dashboard lights up with technique, severity, and a live Capture → Classify → Enrich → Brief pipeline.",
  },
  {
    title: "Brief & share",
    body: "Students get plain-English actions. School IT gets a STIX-shaped JSON export in one click.",
  },
];

const FEATURES = [
  {
    title: "Credible student traps",
    benefit: "Practice against the scams teens actually see — not Hollywood APT theater.",
    detail: "Portal, scholarship, and Discord decoys capture redacted signals only.",
  },
  {
    title: "Visible AI pipeline",
    benefit: "Judges and learners can name every step — not a black-box chat alert.",
    detail: "Pipeline status updates as each event is classified, enriched, and briefed.",
  },
  {
    title: "Victim-ready briefs",
    benefit: "Turn a catch into something a 15-year-old can act on in under a minute.",
    detail: "Cached scenario briefs keep demos reliable; live LLM optional when keyed.",
  },
  {
    title: "School IT export",
    benefit: "Hand off structured intel without pasting screenshots into email.",
    detail: "Download a STIX 2.1-shaped bundle from any completed event.",
  },
];

const STATS = [
  { value: "<2s", label: "Trap-to-dashboard spring" },
  { value: "3", label: "One-click replay scenarios" },
  { value: "4", label: "Visible pipeline stages" },
  { value: "0", label: "Plaintext passwords stored" },
];

const USE_CASES = [
  {
    name: "Student practice",
    blurb: "Run decoys locally and read victim briefs.",
    features: [
      "Portal decoy + dashboard",
      "Victim brief for each catch",
      "Ethics notice built in",
    ],
  },
  {
    name: "Club demo",
    blurb: "The full 90-second spring for live judging.",
    features: [
      "Live feed + pipeline panel",
      "Replay SC-1 · SC-2 · SC-3",
      "STIX export for IT share-out",
      "Scholarship & Discord decoys",
    ],
  },
  {
    name: "School IT pack",
    blurb: "Classroom-ready framing for blue-team clubs.",
    features: [
      "Authorized-training posture",
      "Technique + severity tags",
      "Shareable incident JSON",
      "No secret retention by design",
    ],
  },
];

const FAQS = [
  {
    q: "Is this a phishing kit?",
    a: "No. HoneyDesk is an authorized defensive honeypot for training and demos. Ethics copy is visible in the product, and captures never store plaintext passwords.",
  },
  {
    q: "Who is HoneyDesk for?",
    a: "Students (13–19), school cyber clubs, and school IT personas who need a teachable incident brief — plus judges who need a visceral security demo in under 90 seconds.",
  },
  {
    q: "What happens when someone submits a decoy?",
    a: "The frontend sends field names and boolean flags only (for example password_entered: true). The API redacts secrets, classifies the technique, and generates a brief for the dashboard.",
  },
  {
    q: "Do I need live attackers for a demo?",
    a: "No. Replay SC-1, SC-2, and SC-3 inject seeded scenarios through the same pipeline so the spring is reliable every time.",
  },
  {
    q: "Can school IT use the export?",
    a: "Yes. “Share with school IT” downloads a STIX 2.1-shaped JSON bundle for the selected event.",
  },
  {
    q: "Is there a paid plan?",
    a: "HoneyDesk is completely free to run locally. The use cases above describe intended classroom, club, and IT workflows — not billing.",
  },
];

export default function HomePage() {
  return (
    <div className="flex min-h-full flex-col">
      {/* —— Hero (above the fold) —— */}
      <header className="relative isolate overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_20%_0%,_#FDF6D8_0%,_transparent_50%)]" />
          <div className="soft-drift absolute -right-24 top-0 size-[32rem] rounded-full bg-honey/35 blur-3xl" />
          <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-background to-transparent" />
        </div>

        <div className="px-page py-5">
          <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
            <BrandMark size="sm" />
            <nav className="flex items-center gap-1 sm:gap-2" aria-label="Primary">
              <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
                <Link href="#how-it-works">How it works</Link>
              </Button>
              <Button variant="ghost" size="sm" asChild className="hidden md:inline-flex">
                <Link href="#pricing">Access</Link>
              </Button>
              <Button
                size="sm"
                className="bg-honey text-honey-foreground hover:bg-honey/90 ring-1 ring-ring/35"
                asChild
              >
                <Link href="/dashboard">Open ops dashboard</Link>
              </Button>
            </nav>
          </div>
        </div>

        <section className="mx-auto grid max-w-6xl items-end gap-10 px-page pb-16 pt-8 lg:grid-cols-[1fr_1.05fr] lg:pb-20 lg:pt-12">
          <div className="fade-rise max-w-xl space-y-6">
            <BrandMark size="lg" linked={false} />
            <h1 className="font-heading text-balance text-3xl font-semibold tracking-tight text-foreground sm:text-4xl lg:text-[2.75rem] lg:leading-[1.15]">
              For student cyber clubs — catch school-targeted scams and teach the
              fix in one spring.
            </h1>
            <p className="max-w-md text-pretty text-base leading-relaxed text-muted-foreground sm:text-lg">
              HoneyDesk deploys fake student surfaces, classifies the attack in
              real time, and delivers a plain-English brief plus a STIX export
              schools can share with IT.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button
                size="lg"
                className="bg-honey text-honey-foreground hover:bg-honey/90 ring-1 ring-ring/40"
                asChild
              >
                <Link href="/dashboard">
                  Open ops dashboard
                  <ArrowRight data-icon="inline-end" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/decoy/portal">Start free trial</Link>
              </Button>
            </div>
          </div>

          <ProductVisual className="fade-rise w-full lg:translate-y-2" />
        </section>
      </header>

      <main>
        {/* —— Trust bar —— */}
        <section
          aria-label="Built for authorized training"
          className="border-y border-border/70 bg-surface/60"
        >
          <div className="mx-auto max-w-6xl px-page py-8">
            <p className="text-center text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
              Built for classrooms & clubs running authorized drills
            </p>
          </div>
        </section>

        {/* —— How it works —— */}
        <section
          id="how-it-works"
          className="border-y border-border/70 bg-surface/50 py-16 sm:py-20"
        >
          <div className="mx-auto max-w-6xl px-page">
            <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
              How it works
            </h2>
            <p className="mt-2 max-w-xl text-muted-foreground">
              Three steps from decoy link to school-ready brief.
            </p>
            <ol className="mt-10 grid gap-10 sm:grid-cols-3">
              {STEPS.map((step, index) => (
                <li key={step.title} className="space-y-3">
                  <span className="font-heading text-sm font-semibold text-ring">
                    Step {index + 1}
                  </span>
                  <h3 className="font-heading text-xl font-semibold tracking-tight">
                    {step.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {step.body}
                  </p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* —— Features —— */}
        <section className="mx-auto max-w-6xl px-page py-16 sm:py-20">
          <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
            Features that map to real outcomes
          </h2>
          <p className="mt-2 max-w-xl text-muted-foreground">
            Each capability exists to trap, teach, or brief — nothing decorative.
          </p>
          <ul className="mt-12 grid gap-12 md:grid-cols-2">
            {FEATURES.map((feature, index) => (
              <li key={feature.title} className="grid gap-4 sm:grid-cols-[auto_1fr] sm:gap-6">
                <div
                  aria-hidden
                  className={cn(
                    "flex size-14 items-center justify-center rounded-2xl ring-1",
                    index % 2 === 0
                      ? "bg-honey-soft text-ring ring-honey/70"
                      : "bg-secondary text-foreground ring-border"
                  )}
                >
                  {index === 0 ? (
                    <Radio className="size-5" />
                  ) : index === 1 ? (
                    <Sparkles className="size-5" />
                  ) : index === 2 ? (
                    <GraduationCap className="size-5" />
                  ) : (
                    <ShieldCheck className="size-5" />
                  )}
                </div>
                <div className="space-y-2">
                  <h3 className="font-heading text-lg font-semibold tracking-tight">
                    {feature.title}
                  </h3>
                  <p className="text-sm font-medium text-foreground">
                    {feature.benefit}
                  </p>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {feature.detail}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* —— Stats —— */}
        <section className="border-y border-border/70 bg-ink text-primary-foreground">
          <div className="mx-auto grid max-w-6xl gap-8 px-page py-14 sm:grid-cols-2 lg:grid-cols-4">
            {STATS.map((stat) => (
              <div key={stat.label} className="space-y-1">
                <p className="font-heading text-3xl font-semibold tracking-tight text-honey sm:text-4xl">
                  {stat.value}
                </p>
                <p className="text-sm text-primary-foreground/70">{stat.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* —— Access / use cases —— */}
        <section id="pricing" className="mx-auto max-w-6xl px-page py-16 sm:py-20">
          <div className="max-w-2xl">
            <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
              Completely free to use
            </h2>
            <p className="mt-2 text-muted-foreground">
              HoneyDesk is free to run locally — no billing, no signup. Pick the
              use case that matches your role and open the ops dashboard to get
              started.
            </p>
          </div>
          <ul className="mt-10 grid gap-4 lg:grid-cols-3">
            {USE_CASES.map((useCase) => (
              <li
                key={useCase.name}
                className="flex flex-col rounded-2xl border border-border/80 bg-surface/80 p-6"
              >
                <h3 className="font-heading text-xl font-semibold">{useCase.name}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{useCase.blurb}</p>
                <ul className="mt-6 flex-1 space-y-2 text-sm text-foreground">
                  {useCase.features.map((feature) => (
                    <li key={feature} className="flex gap-2">
                      <span
                        className="mt-2 size-1.5 shrink-0 rounded-full bg-ring"
                        aria-hidden
                      />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
          <div className="mt-10 flex justify-center">
            <Button
              size="lg"
              className="bg-honey text-honey-foreground hover:bg-honey/90 ring-1 ring-ring/40"
              asChild
            >
              <Link href="/dashboard">
                Open ops dashboard
                <ArrowRight data-icon="inline-end" />
              </Link>
            </Button>
          </div>
        </section>

        {/* —— FAQ —— */}
        <section className="border-t border-border/70 bg-surface/50 py-16 sm:py-20">
          <div className="mx-auto grid max-w-6xl gap-10 px-page lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
                FAQ
              </h2>
              <p className="mt-2 text-muted-foreground">
                Common questions before you spring a trap.
              </p>
            </div>
            <Accordion type="single" collapsible className="w-full">
              {FAQS.map((item) => (
                <AccordionItem key={item.q} value={item.q}>
                  <AccordionTrigger className="text-left text-base">
                    {item.q}
                  </AccordionTrigger>
                  <AccordionContent className="text-muted-foreground">
                    {item.a}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        </section>

        {/* —— Final CTA —— */}
        <section className="relative overflow-hidden px-page py-20">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_center,_#F9E8A2_0%,_transparent_55%)] opacity-70"
          />
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-heading text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              Ready to spring the trap?
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-pretty text-muted-foreground">
              Open the live dashboard, replay a seeded scenario, and walk out with
              a student brief plus a school IT export.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Button
                size="lg"
                className="bg-honey text-honey-foreground hover:bg-honey/90 ring-1 ring-ring/40"
                asChild
              >
                <Link href="/dashboard">
                  Open ops dashboard
                  <ArrowRight data-icon="inline-end" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/decoy/portal">Start free trial</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>

      <EthicsFooter />
    </div>
  );
}
