"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function SsoDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void password;
    await submit({
      decoy_id: "sso",
      path: "/decoy/sso/login",
      fields_present: ["email", "password"],
      password_entered: password.length > 0,
      email,
      campaign: "practice-sso",
    });
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-[#f2f2f2] px-4 py-12">
      <main className="w-full max-w-[440px] rounded bg-white px-11 py-10 shadow-md">
        <div className="mb-6 flex items-center gap-2">
          <div
            aria-hidden
            className="grid size-6 grid-cols-2 gap-0.5"
          >
            <span className="bg-[#f25022]" />
            <span className="bg-[#7fba00]" />
            <span className="bg-[#00a4ef]" />
            <span className="bg-[#ffb900]" />
          </div>
          <p className="text-xl text-[#737373]">Campus365</p>
        </div>

        <h1 className="text-[1.7rem] font-semibold text-[#1b1b1b]">Sign in</h1>
        <p className="mt-2 text-sm text-[#616161]">
          Use your school work or student account to continue.
        </p>

        {state === "failed" ? (
          <Alert className="mt-6" variant="destructive">
            <AlertTitle>Unable to verify</AlertTitle>
            <AlertDescription>
              We could not sign you in right now. Please try again later.
            </AlertDescription>
            <Button type="button" variant="outline" size="sm" className="mt-3" onClick={reset}>
              Try again
            </Button>
          </Alert>
        ) : (
          <form className="mt-6 space-y-4" onSubmit={(e) => void onSubmit(e)}>
            <div className="space-y-2">
              <Label htmlFor="email">Email or phone</Label>
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@school.edu"
                disabled={state === "submitting"}
                className="h-11 rounded-none border-neutral-400"
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
                className="h-11 rounded-none border-neutral-400"
              />
            </div>
            <Button
              type="submit"
              className="rounded-none bg-[#0067b8] hover:bg-[#005a9e]"
              disabled={state === "submitting"}
            >
              {state === "submitting" ? (
                <>
                  <LoaderCircle className="animate-spin" data-icon="inline-start" />
                  Signing in…
                </>
              ) : (
                "Next"
              )}
            </Button>
          </form>
        )}
      </main>
    </div>
  );
}
