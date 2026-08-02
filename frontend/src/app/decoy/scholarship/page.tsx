"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function ScholarshipDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [ssn, setSsn] = useState("");
  const [bank, setBank] = useState("");
  const [routing, setRouting] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void ssn;
    void bank;
    void routing;
    await submit({
      decoy_id: "scholarship",
      path: "/decoy/scholarship",
      fields_present: ["full_name", "school_email", "ssn", "bank", "routing"],
      password_entered: false,
      ssn_entered: ssn.length > 0,
      bank_data_entered: bank.length > 0 || routing.length > 0,
      email,
      campaign: "demo-scholarship",
    });
  }

  return (
    <div className="min-h-full bg-[#fff8ef] text-stone-800">
      <header className="border-b border-amber-200/80 bg-[#fff1d6]">
        <div className="mx-auto max-w-xl px-4 py-5">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-900/70">
            Priority notice
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-amber-950">
            Merit Award Confirmation
          </h1>
          <p className="mt-1 text-sm text-amber-950/80">
            Complete within 24 hours to reserve your disbursement window.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-xl px-4 py-8">
        <div className="rounded-lg border border-amber-200 bg-white p-6 shadow-sm">
          {state === "failed" ? (
            <Alert variant="destructive">
              <AlertTitle>Unable to verify</AlertTitle>
              <AlertDescription>
                We could not confirm your award details right now. Please try
                again later.
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
                <Label htmlFor="full_name">Full legal name</Label>
                <Input
                  id="full_name"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="school_email">School email</Label>
                <Input
                  id="school_email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ssn">SSN (for award matching)</Label>
                <Input
                  id="ssn"
                  inputMode="numeric"
                  autoComplete="off"
                  required
                  value={ssn}
                  onChange={(e) => setSsn(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="bank">Bank account</Label>
                  <Input
                    id="bank"
                    autoComplete="off"
                    required
                    value={bank}
                    onChange={(e) => setBank(e.target.value)}
                    disabled={state === "submitting"}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="routing">Routing number</Label>
                  <Input
                    id="routing"
                    autoComplete="off"
                    required
                    value={routing}
                    onChange={(e) => setRouting(e.target.value)}
                    disabled={state === "submitting"}
                  />
                </div>
              </div>
              <Button
                type="submit"
                className="w-full bg-amber-800 hover:bg-amber-900"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle
                      className="animate-spin"
                      data-icon="inline-start"
                    />
                    Confirming…
                  </>
                ) : (
                  "Confirm award now"
                )}
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
