"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function BankDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void password;
    await submit({
      decoy_id: "bank",
      path: "/decoy/bank/login",
      fields_present: ["email", "password"],
      password_entered: password.length > 0,
      email,
      campaign: "practice-bank",
    });
  }

  return (
    <div className="min-h-full bg-[#0a3d2e] text-white">
      <header className="border-b border-white/10 px-4 py-4">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <p className="text-lg font-semibold tracking-tight">Harbor Student Bank</p>
          <span className="text-xs text-emerald-200/80">Secure access</span>
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 py-10">
        <div className="rounded-2xl bg-[#f7faf8] p-6 text-slate-900 shadow-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-800">
            Security alert
          </p>
          <h1 className="mt-2 text-2xl font-semibold">Unusual login blocked</h1>
          <p className="mt-2 text-sm text-slate-600">
            We paused a transfer of $482.19. Confirm your identity to restore
            account access.
          </p>

          {state === "failed" ? (
            <Alert className="mt-6" variant="destructive">
              <AlertTitle>Unable to verify</AlertTitle>
              <AlertDescription>
                We could not verify your credentials right now. Please try again
                later.
              </AlertDescription>
              <Button type="button" variant="outline" size="sm" className="mt-3" onClick={reset}>
                Try again
              </Button>
            </Alert>
          ) : (
            <form className="mt-6 space-y-4" onSubmit={(e) => void onSubmit(e)}>
              <div className="space-y-2">
                <Label htmlFor="email">Online banking ID</Label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@school.edu"
                  disabled={state === "submitting"}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <Button
                type="submit"
                className="w-full rounded-full bg-[#0a3d2e] hover:bg-[#083226]"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle className="animate-spin" data-icon="inline-start" />
                    Verifying…
                  </>
                ) : (
                  "Unlock my account"
                )}
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
