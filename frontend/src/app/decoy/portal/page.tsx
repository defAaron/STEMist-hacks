"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function PortalDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // Never send the password value — only a boolean flag + field names.
    void password;
    await submit({
      decoy_id: "portal",
      path: "/decoy/portal",
      fields_present: ["email", "password"],
      password_entered: password.length > 0,
      email,
      campaign: "demo",
    });
  }

  return (
    <div className="min-h-full bg-[#eef2f7] text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-lg items-center gap-3 px-4 py-4">
          <div
            aria-hidden
            className="flex size-9 items-center justify-center rounded bg-[#1e3a5f] text-sm font-semibold text-white"
          >
            SA
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Student Aid Portal
            </p>
            <p className="text-xs text-slate-500">
              Secure sign-in · Financial Aid Services
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-lg px-4 py-10">
        <div className="rounded-md border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-xl font-semibold text-slate-900">Sign in</h1>
          <p className="mt-1 text-sm text-slate-600">
            Use your school email to continue to award status and aid documents.
          </p>

          {state === "failed" ? (
            <Alert className="mt-6" variant="destructive">
              <AlertTitle>Unable to verify</AlertTitle>
              <AlertDescription>
                We could not verify your credentials right now. Please try again
                later.
              </AlertDescription>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={reset}
              >
                Try again
              </Button>
            </Alert>
          ) : (
            <form className="mt-6 space-y-4" onSubmit={(e) => void onSubmit(e)}>
              <div className="space-y-2">
                <Label htmlFor="email">School email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="username"
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
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-[#1e3a5f] hover:bg-[#16304f]"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle
                      className="animate-spin"
                      data-icon="inline-start"
                    />
                    Verifying…
                  </>
                ) : (
                  "Sign in"
                )}
              </Button>
            </form>
          )}
        </div>
        <p className="mt-6 text-center text-xs text-slate-500">
          © Campus Financial Aid · Do not share your password
        </p>
      </main>
    </div>
  );
}
