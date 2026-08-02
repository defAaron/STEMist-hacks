"use client";

import { useEffect, useRef, useState } from "react";

import { extractEmailDomain, postCapture } from "@/lib/api";
import type { CapturePayload } from "@/lib/types";

export type CaptureUiState = "idle" | "submitting" | "failed";

export function useCaptureSubmit() {
  const [state, setState] = useState<CaptureUiState>("idle");
  const mountedAt = useRef<number | null>(null);

  useEffect(() => {
    mountedAt.current = Date.now();
  }, []);

  async function submit(
    payload: Omit<CapturePayload, "meta"> & {
      email?: string;
      campaign?: string;
    }
  ) {
    setState("submitting");
    const started = mountedAt.current ?? Date.now();
    const dwell_ms = Math.max(0, Date.now() - started);
    const { email, campaign, ...rest } = payload;

    try {
      await postCapture({
        ...rest,
        email_domain:
          rest.email_domain ?? (email ? extractEmailDomain(email) : null),
        meta: {
          dwell_ms,
          referrer:
            typeof document !== "undefined"
              ? document.referrer || undefined
              : undefined,
          campaign,
        },
      });
    } catch {
      // Decoy UX always shows a generic failure after attempt — even on API errors.
    } finally {
      // Small delay so the spinner reads as a real portal check.
      await new Promise((resolve) => window.setTimeout(resolve, 700));
      setState("failed");
    }
  }

  function reset() {
    setState("idle");
  }

  return { state, submit, reset };
}
