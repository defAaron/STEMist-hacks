"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function InstagramDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [username, setUsername] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void username;
    await submit({
      decoy_id: "instagram",
      path: "/decoy/instagram/verify",
      fields_present: ["username", "verify_button", "token"],
      password_entered: false,
      token_entered: true,
      campaign: "practice-instagram",
    });
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-black px-4 py-10 text-white">
      <main className="w-full max-w-sm">
        <div className="rounded-2xl border border-white/10 bg-[#121212] p-6">
          <div className="mb-5 flex justify-center">
            <div
              aria-hidden
              className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#f58529] via-[#dd2a7b] to-[#8134af] text-xl font-bold"
            >
              IG
            </div>
          </div>
          <h1 className="text-center text-xl font-semibold">Confirm it’s you</h1>
          <p className="mt-2 text-center text-sm text-white/70">
            We detected unusual activity on your account. Verify now to keep your
            profile and DMs.
          </p>

          {state === "failed" ? (
            <Alert className="mt-5 border-red-500/40 bg-red-500/10 text-red-300">
              <AlertTitle>Unable to verify</AlertTitle>
              <AlertDescription className="text-white/70">
                Verification failed. Please try again later.
              </AlertDescription>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-3 border-white/20 bg-transparent text-white hover:bg-white/10"
                onClick={reset}
              >
                Try again
              </Button>
            </Alert>
          ) : (
            <form className="mt-5 space-y-4" onSubmit={(e) => void onSubmit(e)}>
              <div className="space-y-2">
                <Label htmlFor="username" className="text-white/70">
                  Username
                </Label>
                <Input
                  id="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="@student"
                  disabled={state === "submitting"}
                  className="border-white/10 bg-[#1a1a1a] text-white placeholder:text-white/35"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-[#f58529] via-[#dd2a7b] to-[#8134af] hover:opacity-90"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle className="animate-spin" data-icon="inline-start" />
                    Verifying…
                  </>
                ) : (
                  "Verify account"
                )}
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
