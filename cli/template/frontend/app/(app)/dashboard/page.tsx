"use client";

import { useAuth } from "@/contexts/AuthContext";
import { config } from "@/lib/config";
import { useUserStore } from "@/stores/userStore";

export default function DashboardPage() {
  const { logout } = useAuth();
  const { user } = useUserStore();

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-semibold text-foreground-primary">
              Welcome to {config.appName}
            </h1>
            <p className="text-foreground-tertiary">
              {user?.email || "Loading..."}
            </p>
          </div>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm font-medium text-foreground-secondary hover:text-foreground-primary border border-border rounded-lg hover:bg-muted transition-colors"
          >
            Sign Out
          </button>
        </div>

        {/* Content */}
        <div className="bg-muted rounded-xl p-6 border border-border">
          <h2 className="text-lg font-medium text-foreground-primary mb-4">
            Dashboard
          </h2>
          <p className="text-foreground-tertiary">
            You&apos;re successfully authenticated! This is a protected route
            that only authenticated users can access.
          </p>

          {/* User info */}
          {user && (
            <div className="mt-6 p-4 bg-background rounded-lg border border-border">
              <h3 className="text-sm font-medium text-foreground-secondary mb-2">
                User Information
              </h3>
              <dl className="space-y-2 text-sm">
                <div className="flex">
                  <dt className="text-foreground-muted w-24">Name:</dt>
                  <dd className="text-foreground-primary">{user.fullName}</dd>
                </div>
                <div className="flex">
                  <dt className="text-foreground-muted w-24">Email:</dt>
                  <dd className="text-foreground-primary">{user.email}</dd>
                </div>
                <div className="flex">
                  <dt className="text-foreground-muted w-24">Joined:</dt>
                  <dd className="text-foreground-primary">
                    {new Date(user.createdAt).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
