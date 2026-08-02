"use client";

import { AuthGate } from "@/components/auth/auth-gate";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";

export function DashboardGated() {
  return (
    <AuthGate>
      {(user) => <DashboardShell user={user} />}
    </AuthGate>
  );
}
