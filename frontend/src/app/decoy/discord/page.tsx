"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function DiscordDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [username, setUsername] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // Username is collected for realism only — never sent as a secret value.
    void username;
    await submit({
      decoy_id: "discord",
      path: "/decoy/discord",
      fields_present: ["discord_username", "verify_button"],
      password_entered: false,
      token_entered: true,
      campaign: "demo-discord",
    });
  }

  return (
    <div className="flex min-h-full items-center justify-center bg-[#313338] px-4 py-10 text-[#f2f3f5]">
      <main className="w-full max-w-md rounded-lg bg-[#2b2d31] p-6 shadow-xl ring-1 ring-black/20">
        <div className="mb-5 flex items-center gap-3">
          <div
            aria-hidden
            className="flex size-12 items-center justify-center rounded-full bg-[#5865f2] text-lg font-bold"
          >
            S
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[#b5bac1]">
              Server verification
            </p>
            <h1 className="text-lg font-semibold">Keep your access</h1>
          </div>
        </div>

        <p className="text-sm leading-relaxed text-[#dbdee1]">
          This community requires a quick verification check. Confirm your
          username to restore member channels.
        </p>

        {state === "failed" ? (
          <Alert className="mt-5 border-[#da373c]/40 bg-[#da373c]/10 text-[#f23f43]">
            <AlertTitle>Unable to verify</AlertTitle>
            <AlertDescription className="text-[#f2f3f5]/80">
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
              <Label htmlFor="discord_username" className="text-[#b5bac1]">
                Discord username
              </Label>
              <Input
                id="discord_username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="student#1234"
                disabled={state === "submitting"}
                className="border-transparent bg-[#1e1f22] text-white placeholder:text-[#6d6f78]"
              />
            </div>
            <Button
              type="submit"
              className="w-full bg-[#5865f2] hover:bg-[#4752c4]"
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
                "Verify to continue"
              )}
            </Button>
          </form>
        )}
      </main>
    </div>
  );
}
