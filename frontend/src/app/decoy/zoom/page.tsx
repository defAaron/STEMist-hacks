"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function ZoomDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void password;
    await submit({
      decoy_id: "zoom",
      path: "/decoy/zoom/signin",
      fields_present: ["email", "password"],
      password_entered: password.length > 0,
      email,
      campaign: "practice-zoom",
    });
  }

  return (
    <div className="flex min-h-full flex-col bg-[#f7f9fa]">
      <header className="border-b border-slate-200 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-md items-center gap-2">
          <div
            aria-hidden
            className="flex size-8 items-center justify-center rounded-xl bg-[#2d8cff] text-sm font-bold text-white"
          >
            Z
          </div>
          <p className="font-semibold text-slate-800">MeetLink</p>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-4 py-10">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <p className="text-center text-sm text-slate-500">Meeting ID 847 220 1191</p>
          <h1 className="mt-2 text-center text-2xl font-semibold text-slate-900">
            Sign in to join class
          </h1>
          <p className="mt-2 text-center text-sm text-slate-600">
            Your instructor started a required review session. Authenticate to enter.
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
                <Label htmlFor="email">School email</Label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="rounded-xl"
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
                  className="rounded-xl"
                  disabled={state === "submitting"}
                />
              </div>
              <Button
                type="submit"
                className="w-full rounded-full bg-[#2d8cff] hover:bg-[#1f78e0]"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle className="animate-spin" data-icon="inline-start" />
                    Joining…
                  </>
                ) : (
                  "Join meeting"
                )}
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
