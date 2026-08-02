"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function FafsaDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [ssn, setSsn] = useState("");
  const [dob, setDob] = useState("");
  const [bank, setBank] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void ssn;
    void dob;
    void bank;
    await submit({
      decoy_id: "fafsa",
      path: "/decoy/fafsa/confirm-now",
      fields_present: ["full_name", "school_email", "ssn", "dob", "bank"],
      password_entered: false,
      ssn_entered: ssn.length > 0,
      bank_data_entered: bank.length > 0,
      email,
      campaign: "practice-fafsa",
    });
  }

  return (
    <div className="min-h-full bg-[#eef3f8] text-slate-900">
      <header className="bg-[#112e51] text-white">
        <div className="mx-auto max-w-2xl px-4 py-4">
          <p className="text-xs uppercase tracking-[0.18em] text-blue-200">
            Official-looking aid notice
          </p>
          <h1 className="mt-1 text-xl font-semibold sm:text-2xl">
            FAFSA correction required
          </h1>
          <p className="mt-1 text-sm text-blue-100">
            Your aid package is on hold until identity fields are updated.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4 py-8">
        <div className="grid gap-4 md:grid-cols-[1fr_1.4fr]">
          <aside className="rounded border border-slate-300 bg-white p-4 text-sm text-slate-600">
            <p className="font-semibold text-slate-900">Status</p>
            <ul className="mt-3 space-y-2">
              <li>• Application received</li>
              <li className="font-medium text-amber-800">• Correction pending</li>
              <li>• Award not released</li>
            </ul>
            <p className="mt-4 text-xs text-slate-500">
              Deadline: 11:59 PM today
            </p>
          </aside>

          <div className="rounded border border-slate-300 bg-white p-5">
            {state === "failed" ? (
              <Alert variant="destructive">
                <AlertTitle>Unable to verify</AlertTitle>
                <AlertDescription>
                  We could not process your correction right now. Please try again
                  later.
                </AlertDescription>
                <Button type="button" variant="outline" size="sm" className="mt-3" onClick={reset}>
                  Try again
                </Button>
              </Alert>
            ) : (
              <form className="space-y-4" onSubmit={(e) => void onSubmit(e)}>
                <div className="space-y-2">
                  <Label htmlFor="full_name">Legal name</Label>
                  <Input
                    id="full_name"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={state === "submitting"}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="school_email">Email</Label>
                  <Input
                    id="school_email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={state === "submitting"}
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="ssn">SSN</Label>
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
                    <Label htmlFor="dob">Date of birth</Label>
                    <Input
                      id="dob"
                      placeholder="MM/DD/YYYY"
                      required
                      value={dob}
                      onChange={(e) => setDob(e.target.value)}
                      disabled={state === "submitting"}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bank">Direct deposit account</Label>
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
                  className="w-full bg-[#112e51] hover:bg-[#0c2340]"
                  disabled={state === "submitting"}
                >
                  {state === "submitting" ? (
                    <>
                      <LoaderCircle className="animate-spin" data-icon="inline-start" />
                      Submitting…
                    </>
                  ) : (
                    "Submit correction"
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
