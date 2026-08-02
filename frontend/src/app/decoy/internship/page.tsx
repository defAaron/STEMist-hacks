"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function InternshipDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [ssn, setSsn] = useState("");
  const [bank, setBank] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void phone;
    void ssn;
    void bank;
    await submit({
      decoy_id: "internship",
      path: "/decoy/internship/confirm-now",
      fields_present: ["full_name", "school_email", "phone", "ssn", "bank"],
      password_entered: false,
      ssn_entered: ssn.length > 0,
      bank_data_entered: bank.length > 0,
      email,
      campaign: "practice-internship",
    });
  }

  return (
    <div className="min-h-full bg-[#f3f7fb] text-slate-800">
      <header className="border-b border-sky-200 bg-white">
        <div className="mx-auto max-w-xl px-4 py-5">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-sky-700">
            Remote internship offer
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">
            Confirm your onboarding packet
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Spots close tonight. Complete identity and payment setup to receive
            your first stipend deposit.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-xl px-4 py-8">
        <div className="rounded-lg border border-sky-100 bg-white p-6 shadow-sm">
          <div className="mb-5 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
            Action required within 6 hours or your offer may be reassigned.
          </div>

          {state === "failed" ? (
            <Alert variant="destructive">
              <AlertTitle>Unable to verify</AlertTitle>
              <AlertDescription>
                We could not complete onboarding verification right now. Please
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
                <Label htmlFor="phone">Mobile phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ssn">SSN (background check)</Label>
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
              <div className="space-y-2">
                <Label htmlFor="bank">Bank account (stipend deposit)</Label>
                <Input
                  id="bank"
                  autoComplete="off"
                  required
                  value={bank}
                  onChange={(e) => setBank(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-sky-700 hover:bg-sky-800"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle
                      className="animate-spin"
                      data-icon="inline-start"
                    />
                    Submitting…
                  </>
                ) : (
                  "Accept offer & confirm deposit"
                )}
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
