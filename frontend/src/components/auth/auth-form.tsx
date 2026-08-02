"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { BrandMark } from "@/components/shared/brand-mark";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login, signup } from "@/lib/api";
import { ApiError } from "@/lib/types";

type Mode = "login" | "signup";

function safeNext(raw: string | null): string {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//")) {
    return "/dashboard";
  }
  return raw;
}

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = safeNext(searchParams.get("next"));

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const isSignup = mode === "signup";

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      if (isSignup) {
        await signup(email, password);
      } else {
        await login(email, password);
      }
      router.replace(next);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong. Try again.");
      }
      setPending(false);
    }
  }

  return (
    <div className="flex min-h-full flex-col">
      <header className="px-page py-5">
        <div className="mx-auto flex max-w-md items-center justify-between">
          <BrandMark href="/" size="sm" />
          <Button variant="ghost" size="sm" asChild>
            <Link href={isSignup ? `/login?next=${encodeURIComponent(next)}` : `/signup?next=${encodeURIComponent(next)}`}>
              {isSignup ? "Log in" : "Create account"}
            </Link>
          </Button>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-page pb-16">
        <Card className="bg-surface/90">
          <CardHeader className="border-b">
            <CardTitle className="font-heading">
              {isSignup ? "Create your HoneyDesk account" : "Log in to HoneyDesk"}
            </CardTitle>
            <CardDescription>
              {isSignup
                ? "Each tester gets a private dashboard and decoy feed."
                : "Your captures and replays stay in your own space."}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <form className="space-y-4" onSubmit={onSubmit}>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@school.edu"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete={isSignup ? "new-password" : "current-password"}
                  required
                  minLength={8}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder={isSignup ? "At least 8 characters" : "Your password"}
                />
              </div>
              {error ? (
                <p className="text-sm text-destructive" role="alert">
                  {error}
                </p>
              ) : null}
              <Button
                type="submit"
                className="w-full bg-honey text-honey-foreground hover:bg-honey/90"
                disabled={pending}
              >
                {pending
                  ? isSignup
                    ? "Creating account…"
                    : "Logging in…"
                  : isSignup
                    ? "Create account"
                    : "Log in"}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="text-sm text-muted-foreground">
            {isSignup ? (
              <p>
                Already have an account?{" "}
                <Link
                  className="text-foreground underline-offset-4 hover:underline"
                  href={`/login?next=${encodeURIComponent(next)}`}
                >
                  Log in
                </Link>
              </p>
            ) : (
              <p>
                New here?{" "}
                <Link
                  className="text-foreground underline-offset-4 hover:underline"
                  href={`/signup?next=${encodeURIComponent(next)}`}
                >
                  Create an account
                </Link>
              </p>
            )}
          </CardFooter>
        </Card>
      </main>
    </div>
  );
}
