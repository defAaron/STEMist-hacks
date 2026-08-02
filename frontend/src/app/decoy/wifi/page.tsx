"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function WifiDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void password;
    await submit({
      decoy_id: "wifi",
      path: "/decoy/wifi/login",
      fields_present: ["email", "password"],
      password_entered: password.length > 0,
      email,
      campaign: "practice-wifi",
    });
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-gradient-to-b from-[#0b1f33] to-[#16324d] px-4 py-10 text-slate-100">
      <main className="w-full max-w-md rounded-xl border border-white/10 bg-white/95 p-6 text-slate-800 shadow-2xl">
        <div className="mb-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">
            Campus network
          </p>
          <h1 className="mt-1 text-xl font-semibold text-slate-900">
            Reconnect to CampusSecure Wi‑Fi
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Your session expired. Sign in with your school account to restore
            internet access.
          </p>
        </div>

        {state === "failed" ? (
          <Alert variant="destructive">
            <AlertTitle>Unable to verify</AlertTitle>
            <AlertDescription>
              We could not authenticate you on this network right now. Please
              try again later.
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
          <form className="space-y-4" onSubmit={(e) => void onSubmit(e)}>
            <div className="space-y-2">
              <Label htmlFor="email">School email</Label>
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
              <Label htmlFor="password">Network password</Label>
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
              className="w-full bg-[#0b1f33] hover:bg-[#081626]"
              disabled={state === "submitting"}
            >
              {state === "submitting" ? (
                <>
                  <LoaderCircle
                    className="animate-spin"
                    data-icon="inline-start"
                  />
                  Connecting…
                </>
              ) : (
                "Connect to Wi‑Fi"
              )}
            </Button>
          </form>
        )}
      </main>
    </div>
  );
}
