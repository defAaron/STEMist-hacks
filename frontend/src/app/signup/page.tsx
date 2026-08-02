import type { Metadata } from "next";
import { Suspense } from "react";

import { AuthForm } from "@/components/auth/auth-form";

export const metadata: Metadata = {
  title: "Sign up",
  description: "Create a HoneyDesk account to test decoys in your own private feed.",
};

export default function SignupPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-full items-center justify-center px-page py-16">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </div>
      }
    >
      <AuthForm mode="signup" />
    </Suspense>
  );
}
