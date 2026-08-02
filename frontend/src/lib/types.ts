/** Types mirrored from HoneyDesk API responses (backend contracts). */

export type Technique =
  | "credential_harvest"
  | "urgency_pii_scam"
  | "social_verify"
  | "typosquat"
  | "bot_probe"
  | "unknown";

export type Severity = "low" | "medium" | "high" | "critical";
export type PipelineStatus = "running" | "complete" | "failed";
export type EventSource = "live" | "simulate" | "replay";
export type ScenarioId = "SC-1" | "SC-2" | "SC-3";

export interface PipelineStep {
  step: string;
  status: string;
  ts: string;
  detail?: string;
}

export interface EventGeo {
  lat?: number;
  lon?: number;
  label?: string;
}

export interface EventBrief {
  victim?: string | null;
  it?: string | null;
  actions?: string[];
  source?: string | null;
}

export interface HoneyEvent {
  id: string;
  created_at: string;
  updated_at: string;
  source: EventSource | string;
  scenario_id: string | null;
  decoy_id: string;
  ip: string;
  user_agent: string;
  path: string | null;
  geo: EventGeo;
  fields_present: string[];
  password_entered: boolean;
  email_domain: string | null;
  meta: Record<string, unknown>;
  technique: Technique | string;
  severity: Severity | string;
  score: number;
  reasons: string[];
  data_targeted: string[];
  brief: EventBrief;
  brief_victim: string | null;
  brief_it: string | null;
  brief_source: string | null;
  pipeline_status: PipelineStatus | string;
  pipeline_steps: PipelineStep[];
}

export interface Stats {
  attacks_caught: number;
  by_technique: Record<string, number>;
  by_severity?: Record<string, number>;
  by_source?: Record<string, number>;
  last_event_at: string | null;
}

export interface CapturePayload {
  decoy_id: string;
  path?: string;
  fields_present: string[];
  password_entered?: boolean;
  ssn_entered?: boolean;
  token_entered?: boolean;
  bank_data_entered?: boolean;
  email_domain?: string | null;
  meta?: {
    dwell_ms?: number;
    referrer?: string;
    campaign?: string;
  };
}

export interface CaptureResponse {
  event_id: string;
  status: "accepted";
}

export interface HealthResponse {
  ok: boolean;
  version: string;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}
