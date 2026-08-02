"use client";

import Link from "next/link";
import { useState } from "react";
import { Check, Copy, ExternalLink } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PRACTICE_DECOYS } from "@/lib/practice-decoys";

function absoluteUrl(path: string): string {
  if (typeof window === "undefined") return path;
  return `${window.location.origin}${path}`;
}

export function PracticeDecoysPanel() {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  async function copyLink(id: string, href: string) {
    const url = absoluteUrl(href);
    try {
      await navigator.clipboard.writeText(url);
      setCopiedId(id);
      window.setTimeout(() => {
        setCopiedId((current) => (current === id ? null : current));
      }, 1600);
    } catch {
      // Clipboard may be blocked; open is still available.
    }
  }

  return (
    <Card id="practice-decoys" className="scroll-mt-6 bg-surface/90">
      <CardHeader className="border-b">
        <CardTitle className="font-heading">Practice decoys</CardTitle>
        <CardDescription>
          Share these training links with students. Submissions land in your
          private feed with a victim brief — authorized practice only.
        </CardDescription>
      </CardHeader>
      <CardContent className="divide-y pt-0">
        {PRACTICE_DECOYS.map((decoy) => (
          <div
            key={decoy.id}
            className="flex flex-col gap-3 py-4 sm:flex-row sm:items-start sm:justify-between"
          >
            <div className="min-w-0 space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="font-medium text-foreground">{decoy.title}</p>
                <span className="text-xs text-muted-foreground">
                  {decoy.techniqueLabel}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{decoy.blurb}</p>
              <p className="truncate font-mono text-xs text-muted-foreground">
                {decoy.href}
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => void copyLink(decoy.id, decoy.href)}
              >
                {copiedId === decoy.id ? (
                  <>
                    <Check data-icon="inline-start" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy data-icon="inline-start" />
                    Copy link
                  </>
                )}
              </Button>
              <Button variant="secondary" size="sm" asChild>
                <Link href={decoy.href} target="_blank" rel="noreferrer">
                  Open
                  <ExternalLink data-icon="inline-end" />
                </Link>
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
