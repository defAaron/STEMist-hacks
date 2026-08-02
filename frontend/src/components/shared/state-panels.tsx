import { AlertCircle, Inbox, LoaderCircle, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export function LoadingPanel({
  label = "Loading…",
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-16 text-muted-foreground",
        className
      )}
    >
      <LoaderCircle className="size-5 animate-spin text-ring" aria-hidden />
      <p className="text-sm">{label}</p>
      <div className="mt-2 flex w-full max-w-sm flex-col gap-2">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-4/5" />
      </div>
    </div>
  );
}

export function EmptyPanel({
  title,
  description,
  action,
  className,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-16 text-center",
        className
      )}
    >
      <div className="flex size-11 items-center justify-center rounded-full bg-honey-soft ring-1 ring-honey/70">
        <Inbox className="size-5 text-ink" aria-hidden />
      </div>
      <div className="space-y-1">
        <p className="font-heading text-base font-semibold text-foreground">
          {title}
        </p>
        <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
      </div>
      {action}
    </div>
  );
}

export function ErrorPanel({
  title = "Something went wrong",
  description,
  onRetry,
  className,
}: {
  title?: string;
  description: string;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-16 text-center",
        className
      )}
    >
      <div className="flex size-11 items-center justify-center rounded-full bg-destructive/10 text-destructive">
        <AlertCircle className="size-5" aria-hidden />
      </div>
      <div className="space-y-1">
        <p className="font-heading text-base font-semibold text-foreground">
          {title}
        </p>
        <p className="max-w-sm text-sm text-muted-foreground">{description}</p>
      </div>
      {onRetry ? (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw data-icon="inline-start" />
          Try again
        </Button>
      ) : null}
    </div>
  );
}
