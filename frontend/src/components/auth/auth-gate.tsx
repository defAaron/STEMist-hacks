"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { fetchMe } from "@/lib/api";
import { getAuthToken } from "@/lib/auth";
import type { AuthUser } from "@/lib/types";
import { ApiError } from "@/lib/types";

type AuthGateProps = {
  children: (user: AuthUser) => React.ReactNode;
};

export function AuthGate({ children }: AuthGateProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function verify() {
      const token = getAuthToken();
      if (!token) {
        const next = encodeURIComponent(pathname || "/dashboard");
        router.replace(`/login?next=${next}`);
        return;
      }
      try {
        const me = await fetchMe();
        if (!cancelled) {
          setUser(me);
          setError(null);
          setChecking(false);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          const next = encodeURIComponent(pathname || "/dashboard");
          router.replace(`/login?next=${next}`);
          return;
        }
        setError(
          err instanceof ApiError ? err.message : "Could not verify session"
        );
        setChecking(false);
      }
    }

    void verify();
    return () => {
      cancelled = true;
    };
  }, [pathname, router]);

  if (checking) {
    return (
      <div className="flex min-h-full items-center justify-center px-page py-16">
        <p className="text-sm text-muted-foreground">Checking session…</p>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="flex min-h-full flex-col items-center justify-center gap-3 px-page py-16">
        <p className="text-sm text-destructive" role="alert">
          {error ?? "Authentication required"}
        </p>
        <button
          type="button"
          className="text-sm underline-offset-4 hover:underline"
          onClick={() => {
            const next = encodeURIComponent(pathname || "/dashboard");
            router.replace(`/login?next=${next}`);
          }}
        >
          Go to login
        </button>
      </div>
    );
  }

  return <>{children(user)}</>;
}
