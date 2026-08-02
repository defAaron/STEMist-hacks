export function formatRelativeTime(iso: string, now = Date.now()): string {
  const then = Date.parse(iso);
  if (Number.isNaN(then)) return "—";

  const deltaSec = Math.round((then - now) / 1000);
  const abs = Math.abs(deltaSec);
  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

  if (abs < 60) return rtf.format(deltaSec, "second");
  const deltaMin = Math.round(deltaSec / 60);
  if (Math.abs(deltaMin) < 60) return rtf.format(deltaMin, "minute");
  const deltaHr = Math.round(deltaMin / 60);
  if (Math.abs(deltaHr) < 24) return rtf.format(deltaHr, "hour");
  const deltaDay = Math.round(deltaHr / 24);
  return rtf.format(deltaDay, "day");
}

export function formatClock(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("en", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

export function shortId(id: string): string {
  return id.slice(0, 8);
}
