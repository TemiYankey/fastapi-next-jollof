"use client";

import { LoadingScreen } from "@/components/ui/LoadingScreen";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function ProtectedRoute({
  children,
  redirectTo = "/auth/signin",
}: ProtectedRouteProps) {
  const { isLoading, isAuthenticated } = useAuth();
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !isRedirecting) {
      setIsRedirecting(true);
      router.replace(redirectTo);
    }
  }, [isAuthenticated, isLoading, router, redirectTo, isRedirecting]);

  useEffect(() => {
    if (isAuthenticated && isRedirecting) {
      setIsRedirecting(false);
    }
  }, [isAuthenticated, isRedirecting]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated || isRedirecting) {
    return <LoadingScreen />;
  }

  return <>{children}</>;
}
