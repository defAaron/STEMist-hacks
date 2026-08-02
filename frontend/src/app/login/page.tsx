import type { Metadata } from "next";
import { Suspense } from "react";

import { AuthForm } from "@/components/auth/auth-form";

export const metadata: Metadata = {
  title: "Log in",
  description: "Log in to your HoneyDesk tester account.",
};

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-full items-center justify-center px-page py-16">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </div>
      }
    >
      <AuthForm mode="login" />
    </Suspense>
  );
}
