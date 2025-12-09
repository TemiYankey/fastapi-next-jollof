"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

/**
 * Layout for all authenticated app routes.
 * This wraps all routes in (app)/ with authentication protection.
 *
 * Route groups in Next.js:
 * - (app) = authenticated user area
 * - Doesn't affect URL structure
 * - Allows shared layouts for protected routes
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}
