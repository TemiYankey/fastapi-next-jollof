"use client";

import { LoadingScreen } from "@/components/ui/LoadingScreen";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";

function AuthLayoutContent({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      const next = searchParams.get("next");
      const redirectTo = next && next.startsWith("/") ? next : "/dashboard";
      router.replace(redirectTo);
    }
  }, [isAuthenticated, isLoading, router, searchParams]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return <LoadingScreen />;
  }

  return <>{children}</>;
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <AuthLayoutContent>{children}</AuthLayoutContent>
    </Suspense>
  );
}
