import { Badge } from "@/components/ui/badge";
import { techniqueLabel } from "@/lib/labels";
import { cn } from "@/lib/utils";

export function TechniqueBadge({
  technique,
  className,
}: {
  technique: string;
  className?: string;
}) {
  return (
    <Badge
      variant="secondary"
      className={cn(
        "rounded-md bg-honey-soft text-honey-foreground ring-1 ring-honey/60",
        className
      )}
    >
      {techniqueLabel(technique)}
    </Badge>
  );
}
