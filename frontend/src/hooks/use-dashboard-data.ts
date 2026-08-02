"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchEvent, fetchEvents, fetchStats } from "@/lib/api";
import type { HoneyEvent, Stats } from "@/lib/types";
import { ApiError } from "@/lib/types";

const POLL_MS = 1000;
const HIGHLIGHT_MS = 2000;

export type LoadState = "loading" | "ready" | "empty" | "error";

interface DashboardData {
  events: HoneyEvent[];
  stats: Stats | null;
  selectedId: string | null;
  selectedEvent: HoneyEvent | null;
  highlightedIds: Set<string>;
  state: LoadState;
  error: string | null;
  selectEvent: (id: string) => void;
  refreshNow: () => Promise<void>;
  upsertEvent: (event: HoneyEvent) => void;
}

function mergeById(existing: HoneyEvent[], incoming: HoneyEvent[]): HoneyEvent[] {
  const map = new Map<string, HoneyEvent>();
  for (const event of existing) map.set(event.id, event);
  for (const event of incoming) map.set(event.id, event);
  return Array.from(map.values()).sort(
    (a, b) => Date.parse(b.created_at) - Date.parse(a.created_at)
  );
}

export function useDashboardData(): DashboardData {
  const [events, setEvents] = useState<HoneyEvent[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detailById, setDetailById] = useState<Record<string, HoneyEvent>>({});
  const [highlightedIds, setHighlightedIds] = useState<Set<string>>(new Set());
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const knownIdsRef = useRef<Set<string>>(new Set());
  const bootstrappedRef = useRef(false);
  const highlightTimers = useRef<Map<string, number>>(new Map());

  const markHighlighted = useCallback((ids: string[]) => {
    if (ids.length === 0) return;
    setHighlightedIds((prev) => {
      const next = new Set(prev);
      for (const id of ids) next.add(id);
      return next;
    });

    for (const id of ids) {
      const existing = highlightTimers.current.get(id);
      if (existing) window.clearTimeout(existing);
      const timer = window.setTimeout(() => {
        setHighlightedIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
        highlightTimers.current.delete(id);
      }, HIGHLIGHT_MS);
      highlightTimers.current.set(id, timer);
    }
  }, []);

  const upsertEvent = useCallback(
    (event: HoneyEvent) => {
      const isNew = !knownIdsRef.current.has(event.id);
      knownIdsRef.current.add(event.id);
      setEvents((prev) => mergeById(prev, [event]));
      setDetailById((prev) => ({ ...prev, [event.id]: event }));
      setSelectedId((current) => current ?? event.id);
      if (isNew) markHighlighted([event.id]);
      setState("ready");
      setError(null);
    },
    [markHighlighted]
  );

  const refreshNow = useCallback(async () => {
    try {
      const [nextEvents, nextStats] = await Promise.all([
        fetchEvents(50),
        fetchStats(),
      ]);

      const freshIds: string[] = [];
      for (const event of nextEvents) {
        if (bootstrappedRef.current && !knownIdsRef.current.has(event.id)) {
          freshIds.push(event.id);
        }
        knownIdsRef.current.add(event.id);
      }
      bootstrappedRef.current = true;

      setEvents(nextEvents);
      setStats(nextStats);
      setError(null);

      if (nextEvents.length === 0) {
        setState("empty");
        setSelectedId(null);
        return;
      }

      setState("ready");
      markHighlighted(freshIds);
      setSelectedId((current) => {
        if (current && nextEvents.some((event) => event.id === current)) {
          return current;
        }
        return nextEvents[0].id;
      });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Unable to reach the HoneyDesk API.";
      setError(message);
      setState((prev) => (prev === "ready" || prev === "empty" ? prev : "error"));
    }
  }, [markHighlighted]);

  useEffect(() => {
    const timers = highlightTimers.current;
    const poll = () => {
      void refreshNow();
    };

    const initial = window.setTimeout(poll, 0);
    const interval = window.setInterval(poll, POLL_MS);

    return () => {
      window.clearTimeout(initial);
      window.clearInterval(interval);
      for (const timer of timers.values()) {
        window.clearTimeout(timer);
      }
      timers.clear();
    };
  }, [refreshNow]);

  const selectedUpdatedAt =
    events.find((event) => event.id === selectedId)?.updated_at ?? null;

  useEffect(() => {
    if (!selectedId) return;

    let cancelled = false;
    const requestId = selectedId;

    void fetchEvent(requestId)
      .then((detail) => {
        if (cancelled) return;
        setDetailById((prev) => ({ ...prev, [detail.id]: detail }));
        setEvents((prev) => mergeById(prev, [detail]));
      })
      .catch(() => {
        // Keep list snapshot if detail fetch fails transiently.
      });

    return () => {
      cancelled = true;
    };
  }, [selectedId, selectedUpdatedAt]);

  const selectEvent = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  const selectedEvent = useMemo(() => {
    if (!selectedId) return null;
    return (
      detailById[selectedId] ??
      events.find((event) => event.id === selectedId) ??
      null
    );
  }, [selectedId, detailById, events]);

  return {
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
  };
}
