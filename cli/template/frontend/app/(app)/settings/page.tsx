"use client";

import { useAuth } from "@/contexts/AuthContext";

export default function SettingsPage() {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-semibold text-foreground-primary mb-8">
          Settings
        </h1>

        {/* Account Section */}
        <div className="bg-muted rounded-xl p-6 border border-border mb-6">
          <h2 className="text-lg font-medium text-foreground-primary mb-4">
            Account
          </h2>
          <p className="text-foreground-tertiary mb-4">
            Manage your account settings and preferences.
          </p>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
          >
            Sign Out
          </button>
        </div>

        {/* Placeholder for more settings */}
        <div className="bg-muted rounded-xl p-6 border border-border">
          <h2 className="text-lg font-medium text-foreground-primary mb-4">
            Preferences
          </h2>
          <p className="text-foreground-tertiary">
            Additional settings coming soon...
          </p>
        </div>
      </div>
    </div>
  );
}
