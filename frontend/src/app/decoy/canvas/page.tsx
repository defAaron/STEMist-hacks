"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function CanvasDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void password;
    await submit({
      decoy_id: "canvas",
      path: "/decoy/canvas",
      fields_present: ["email", "password"],
      password_entered: password.length > 0,
      email,
      campaign: "practice-canvas",
    });
  }

  return (
    <div className="min-h-full bg-[#f5f5f5] text-neutral-800">
      <header className="bg-[#e03c31]">
        <div className="mx-auto flex max-w-md items-center gap-3 px-4 py-4 text-white">
          <div
            aria-hidden
            className="flex size-9 items-center justify-center rounded bg-white/15 text-sm font-bold"
          >
            C
          </div>
          <div>
            <p className="text-sm font-semibold">Campus Learning</p>
            <p className="text-xs text-white/80">Sign in to view your courses</p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-md px-4 py-10">
        <div className="rounded border border-neutral-200 bg-white p-6 shadow-sm">
          <h1 className="text-xl font-semibold text-neutral-900">Log in</h1>
          <p className="mt-1 text-sm text-neutral-600">
            Use your school credentials to access assignments and grades.
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
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
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
                className="w-full bg-[#e03c31] hover:bg-[#c4342a]"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle
                      className="animate-spin"
                      data-icon="inline-start"
                    />
                    Signing in…
                  </>
                ) : (
                  "Log in"
                )}
              </Button>
            </form>
          )}
        </div>
        <p className="mt-6 text-center text-xs text-neutral-500">
          Having trouble? Contact campus support through the official school site.
        </p>
      </main>
    </div>
  );
}
