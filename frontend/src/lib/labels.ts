import type { ScenarioId, Severity, Technique } from "@/lib/types";

export const TECHNIQUE_LABELS: Record<Technique, string> = {
  credential_harvest: "Credential harvest",
  urgency_pii_scam: "Urgency / PII scam",
  social_verify: "Social verify",
  typosquat: "Typosquat",
  bot_probe: "Bot probe",
  unknown: "Unknown",
};

export const SEVERITY_LABELS: Record<Severity, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

export const PIPELINE_STEP_ORDER = [
  "capture",
  "classify",
  "enrich",
  "brief",
  "persist",
] as const;

export const PIPELINE_STEP_LABELS: Record<string, string> = {
  capture: "Capture",
  classify: "Classify",
  enrich: "Enrich",
  brief: "Brief",
  persist: "Persist",
};

export const SCENARIOS: {
  id: ScenarioId;
  label: string;
  description: string;
}[] = [
  {
    id: "SC-1",
    label: "Replay SC-1",
    description: "Aid portal credential harvest",
  },
  {
    id: "SC-2",
    label: "Replay SC-2",
    description: "Scholarship urgency / PII",
  },
  {
    id: "SC-3",
    label: "Replay SC-3",
    description: "Discord social verify",
  },
];

export function techniqueLabel(technique: string): string {
  return TECHNIQUE_LABELS[technique as Technique] ?? technique.replaceAll("_", " ");
}

export function severityLabel(severity: string): string {
  return SEVERITY_LABELS[severity as Severity] ?? severity;
}

export function formatDataTarget(value: string): string {
  return value.replaceAll("_", " ");
}
