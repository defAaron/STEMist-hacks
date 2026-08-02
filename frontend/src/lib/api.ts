import type {
  AuthResponse,
  AuthUser,
  CapturePayload,
  CaptureResponse,
  HealthResponse,
  HoneyEvent,
  ScenarioId,
  Stats,
} from "@/lib/types";
import { ApiError } from "@/lib/types";
import { authHeaders, clearAuthToken, setAuthToken } from "@/lib/auth";

const DEFAULT_API_URL = "http://127.0.0.1:8000";

export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!raw) return DEFAULT_API_URL;
  return raw.replace(/\/$/, "");
}

export function getSimulateToken(): string | undefined {
  const token = process.env.NEXT_PUBLIC_SIMULATE_TOKEN?.trim();
  return token || undefined;
}

async function parseError(response: Response): Promise<ApiError> {
  let detail = `Request failed (${response.status})`;
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail.trim()) {
      detail = body.detail;
    }
  } catch {
    // keep generic message
  }
  return new ApiError(detail, response.status);
}

async function request<T>(
  path: string,
  init?: RequestInit & { parseJson?: boolean; auth?: boolean }
): Promise<T> {
  const { parseJson = true, auth = false, headers, ...rest } = init ?? {};
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...rest,
    headers: {
      Accept: "application/json",
      ...(auth ? authHeaders() : {}),
      ...headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    if (response.status === 401 && auth) {
      clearAuthToken();
    }
    throw await parseError(response);
  }

  if (!parseJson) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function fetchStats(): Promise<Stats> {
  return request<Stats>("/stats", { auth: true });
}

export async function fetchEvents(limit = 50): Promise<HoneyEvent[]> {
  const safeLimit = Math.min(100, Math.max(1, limit));
  return request<HoneyEvent[]>(`/events?limit=${safeLimit}`, { auth: true });
}

export async function fetchEvent(eventId: string): Promise<HoneyEvent> {
  return request<HoneyEvent>(`/events/${encodeURIComponent(eventId)}`, {
    auth: true,
  });
}

export async function postCapture(
  payload: CapturePayload
): Promise<CaptureResponse> {
  return request<CaptureResponse>("/capture", {
    method: "POST",
    auth: true,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function postSimulate(scenarioId: ScenarioId): Promise<HoneyEvent> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getSimulateToken();
  if (token) {
    headers["X-Simulate-Token"] = token;
  }

  return request<HoneyEvent>("/simulate", {
    method: "POST",
    auth: true,
    headers,
    body: JSON.stringify({ scenario_id: scenarioId }),
  });
}

export async function downloadStixExport(eventId: string): Promise<void> {
  const response = await fetch(
    `${getApiBaseUrl()}/export/stix/${encodeURIComponent(eventId)}`,
    {
      cache: "no-store",
      headers: {
        ...authHeaders(),
      },
    }
  );

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken();
    }
    throw await parseError(response);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = /filename="?([^"]+)"?/i.exec(disposition);
  const filename = match?.[1] ?? `honeydesk-${eventId}.stix.json`;

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export async function signup(
  email: string,
  password: string
): Promise<AuthResponse> {
  const result = await request<AuthResponse>("/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(result.token);
  return result;
}

export async function login(
  email: string,
  password: string
): Promise<AuthResponse> {
  const result = await request<AuthResponse>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(result.token);
  return result;
}

export async function logout(): Promise<void> {
  try {
    await request<void>("/auth/logout", {
      method: "POST",
      auth: true,
      parseJson: false,
    });
  } finally {
    clearAuthToken();
  }
}

export async function fetchMe(): Promise<AuthUser> {
  return request<AuthUser>("/auth/me", { auth: true });
}

export function extractEmailDomain(email: string): string | null {
  const trimmed = email.trim().toLowerCase();
  const at = trimmed.lastIndexOf("@");
  if (at <= 0 || at === trimmed.length - 1) return null;
  const domain = trimmed.slice(at + 1).replace(/\.$/, "");
  return domain || null;
}
