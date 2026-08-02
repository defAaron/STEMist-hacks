import type { Metadata } from "next";

import { DecoyAuthGate } from "@/components/auth/decoy-auth-gate";

export const metadata: Metadata = {
  title: "Sign in",
  robots: {
    index: false,
    follow: false,
  },
};

export default function DecoyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DecoyAuthGate>{children}</DecoyAuthGate>;
}
