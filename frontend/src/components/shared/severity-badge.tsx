import { Badge } from "@/components/ui/badge";
import { severityLabel } from "@/lib/labels";
import { cn } from "@/lib/utils";

const SEVERITY_CLASS: Record<string, string> = {
  critical: "border-severity-critical/30 bg-severity-critical/10 text-severity-critical",
  high: "border-severity-high/30 bg-severity-high/10 text-severity-high",
  medium: "border-severity-medium/25 bg-severity-medium/10 text-severity-medium",
  low: "border-severity-low/25 bg-severity-low/10 text-severity-low",
};

export function SeverityBadge({
  severity,
  className,
}: {
  severity: string;
  className?: string;
}) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-md capitalize",
        SEVERITY_CLASS[severity] ?? SEVERITY_CLASS.medium,
        className
      )}
    >
      {severityLabel(severity)}
    </Badge>
  );
}
