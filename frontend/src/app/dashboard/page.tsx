import type { Metadata } from "next";

import { DashboardShell } from "@/components/dashboard/dashboard-shell";

export const metadata: Metadata = {
  title: "Ops dashboard",
  description:
    "Watch HoneyDesk traps spring in real time, replay scenarios, and export STIX briefs.",
};

export default function DashboardPage() {
  return <DashboardShell />;
}
