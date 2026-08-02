import { ShieldCheck } from "lucide-react";

import { cn } from "@/lib/utils";

export function EthicsFooter({ className }: { className?: string }) {
  return (
    <footer
      className={cn(
        "border-t border-border/80 bg-surface/70 px-page py-3 text-xs text-muted-foreground backdrop-blur",
        className
      )}
    >
      <div className="mx-auto flex max-w-7xl items-start gap-2 sm:items-center">
        <ShieldCheck
          className="mt-0.5 size-3.5 shrink-0 text-ring sm:mt-0"
          aria-hidden
        />
        <p>
          Authorized training / defensive honeypot only. HoneyDesk never stores
          plaintext passwords — only redacted signals and educational briefs.
        </p>
      </div>
    </footer>
  );
}
