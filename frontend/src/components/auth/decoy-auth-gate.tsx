"use client";

import { AuthGate } from "@/components/auth/auth-gate";

export function DecoyAuthGate({ children }: { children: React.ReactNode }) {
  return <AuthGate>{() => children}</AuthGate>;
}
