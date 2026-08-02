"use client";

import { useState, type FormEvent } from "react";
import { LoaderCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCaptureSubmit } from "@/hooks/use-capture-submit";

export default function PackageDecoyPage() {
  const { state, submit, reset } = useCaptureSubmit();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [bank, setBank] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void phone;
    void address;
    void bank;
    await submit({
      decoy_id: "package",
      path: "/decoy/package/confirm-now",
      fields_present: ["full_name", "school_email", "phone", "address", "bank"],
      password_entered: false,
      bank_data_entered: bank.length > 0,
      email,
      campaign: "practice-package",
    });
  }

  return (
    <div className="min-h-full bg-[#fff7ed] text-stone-800">
      <header className="bg-[#c2410c] text-white">
        <div className="mx-auto max-w-xl px-4 py-5">
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-orange-100">
            Parcel notice
          </p>
          <h1 className="mt-1 text-2xl font-bold">Delivery held at facility</h1>
          <p className="mt-1 text-sm text-orange-50/90">
            Tracking #HD-928441 · Reschedule before 8:00 PM or package returns.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-xl px-4 py-8">
        <div className="rounded-xl border-2 border-dashed border-orange-300 bg-white p-6">
          {state === "failed" ? (
            <Alert variant="destructive">
              <AlertTitle>Unable to verify</AlertTitle>
              <AlertDescription>
                We could not confirm your delivery details right now. Please try
                again later.
              </AlertDescription>
              <Button type="button" variant="outline" size="sm" className="mt-3" onClick={reset}>
                Try again
              </Button>
            </Alert>
          ) : (
            <form className="space-y-4" onSubmit={(e) => void onSubmit(e)}>
              <div className="space-y-2">
                <Label htmlFor="full_name">Recipient name</Label>
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
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
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
                <Label htmlFor="address">Delivery address</Label>
                <Input
                  id="address"
                  required
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  disabled={state === "submitting"}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bank">Card / account for $2.99 redelivery fee</Label>
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
                className="w-full bg-[#c2410c] hover:bg-[#9a3412]"
                disabled={state === "submitting"}
              >
                {state === "submitting" ? (
                  <>
                    <LoaderCircle className="animate-spin" data-icon="inline-start" />
                    Scheduling…
                  </>
                ) : (
                  "Pay fee & release package"
                )}
              </Button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
