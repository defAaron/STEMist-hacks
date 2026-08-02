"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function TextbookDecoyPage() {
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
      decoy_id: "textbook",
      path: "/decoy/textbook/confirm-now",
      fields_present: ["full_name", "school_email", "ssn", "bank", "routing"],
      password_entered: false,
      ssn_entered: ssn.length > 0,
      bank_data_entered: bank.length > 0 || routing.length > 0,
      email,
      campaign: "practice-textbook",
    });
  }

  return (
    <div className="min-h-full bg-[#faf5ff] text-violet-950">
      <header className="border-b border-violet-200 bg-white">
        <div className="mx-auto flex max-w-xl items-end justify-between gap-4 px-4 py-5">
          <div>
            <p className="text-sm font-medium text-violet-600">CampusBuyback</p>
            <h1 className="text-2xl font-bold tracking-tight">
              $214 refund ready
            </h1>
          </div>
          <p className="rounded bg-violet-100 px-2 py-1 text-xs font-semibold text-violet-800">
            Ends tonight
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-xl px-4 py-8">
        <div className="overflow-hidden rounded-2xl border border-violet-200 bg-white shadow-sm">
          <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 px-6 py-4 text-white">
            <p className="text-sm text-violet-100">Spring semester buyback</p>
            <p className="text-lg font-semibold">Confirm deposit details to claim</p>
          </div>
          <div className="p-6">
            {state === "failed" ? (
              <Alert variant="destructive">
                <AlertTitle>Unable to verify</AlertTitle>
                <AlertDescription>
                  We could not process your refund claim right now. Please try
                  again later.
                </AlertDescription>
                <Button type="button" variant="outline" size="sm" className="mt-3" onClick={reset}>
                  Try again
                </Button>
              </Alert>
            ) : (
              <form className="space-y-4" onSubmit={(e) => void onSubmit(e)}>
                <div className="space-y-2">
                  <Label htmlFor="full_name">Student name</Label>
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
                  <Label htmlFor="ssn">Last 4 of SSN (identity match)</Label>
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
                    <Label htmlFor="bank">Account number</Label>
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
                  className="w-full bg-violet-700 hover:bg-violet-800"
                  disabled={state === "submitting"}
                >
                  {state === "submitting" ? (
                    <>
                      <LoaderCircle className="animate-spin" data-icon="inline-start" />
                      Claiming…
                    </>
                  ) : (
                    "Claim textbook refund"
                  )}
                </Button>
              </form>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
