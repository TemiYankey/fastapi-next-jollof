"use client";

import { useUserStore } from "@/stores/userStore";
import { useEffect } from "react";

export default function ProfilePage() {
  const { user, completeProfile, isProfileLoading, fetchCompleteProfile } =
    useUserStore();

  useEffect(() => {
    if (!completeProfile) {
      fetchCompleteProfile();
    }
  }, [completeProfile, fetchCompleteProfile]);

  if (isProfileLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-border border-t-primary-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  const profile = completeProfile || user;

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-semibold text-foreground-primary mb-8">
          Profile
        </h1>

        {/* Profile Card */}
        <div className="bg-muted rounded-xl p-6 border border-border">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center">
              <span className="text-2xl font-semibold text-primary-600">
                {profile?.fullName?.charAt(0) || "U"}
              </span>
            </div>
            <div>
              <h2 className="text-lg font-medium text-foreground-primary">
                {profile?.fullName || "User"}
              </h2>
              <p className="text-foreground-tertiary">{profile?.email}</p>
            </div>
          </div>

          <dl className="space-y-4">
            <div>
              <dt className="text-sm text-foreground-muted">Member since</dt>
              <dd className="text-foreground-primary">
                {profile?.createdAt
                  ? new Date(profile.createdAt).toLocaleDateString()
                  : "—"}
              </dd>
            </div>
            {completeProfile?.bio && (
              <div>
                <dt className="text-sm text-foreground-muted">Bio</dt>
                <dd className="text-foreground-primary">{completeProfile.bio}</dd>
              </div>
            )}
            {completeProfile?.location && (
              <div>
                <dt className="text-sm text-foreground-muted">Location</dt>
                <dd className="text-foreground-primary">
                  {completeProfile.location}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}
