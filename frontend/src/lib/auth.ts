/** Client-side session token helpers for HoneyDesk accounts. */

const TOKEN_KEY = "honeydesk_token";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const token = sessionStorage.getItem(TOKEN_KEY);
    return token?.trim() || null;
  } catch {
    return null;
  }
}

export function setAuthToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  try {
    sessionStorage.removeItem(TOKEN_KEY);
  } catch {
    // ignore storage failures
  }
}

export function authHeaders(): Record<string, string> {
  const token = getAuthToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}
