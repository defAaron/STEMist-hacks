import type { Metadata } from "next";

import { DashboardGated } from "@/components/dashboard/dashboard-gated";

export const metadata: Metadata = {
  title: "Ops dashboard",
  description:
    "Watch HoneyDesk traps spring in real time, replay scenarios, and export STIX briefs.",
};

export default function DashboardPage() {
  return <DashboardGated />;
}
