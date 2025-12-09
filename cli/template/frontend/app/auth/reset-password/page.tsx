"use client";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { supabase } from "@/lib/supabase";
import { CheckCircleIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isValidSession, setIsValidSession] = useState<boolean | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        setIsValidSession(false);
        return;
      }

      // Check if this is a recovery session
      try {
        const payload = JSON.parse(
          atob(session.access_token.split(".")[1])
        );
        const isRecovery = payload.amr?.some(
          (method: { method: string }) => method.method === "recovery"
        );
        setIsValidSession(isRecovery);
      } catch {
        setIsValidSession(false);
      }
    };

    checkSession();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");

    // Validation
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      setIsSubmitting(false);
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      setIsSubmitting(false);
      return;
    }

    try {
      const { error } = await supabase.auth.updateUser({ password });

      if (error) {
        setError(error.message);
      } else {
        setSuccess(true);
        // Sign out after password reset
        await supabase.auth.signOut();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset password");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Loading state
  if (isValidSession === null) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-border border-t-primary-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  // Invalid session
  if (isValidSession === false) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full mb-4">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h1 className="text-2xl font-semibold text-foreground-primary mb-2">
            Invalid Reset Link
          </h1>
          <p className="text-foreground-tertiary mb-6">
            This password reset link is invalid or has expired. Please request a
            new one.
          </p>
          <Link
            href="/auth/forgot-password"
            className="inline-block px-6 py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Request New Link
          </Link>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full mb-4">
            <CheckCircleIcon className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-2xl font-semibold text-foreground-primary mb-2">
            Password Reset Successful
          </h1>
          <p className="text-foreground-tertiary mb-6">
            Your password has been reset successfully. You can now sign in with
            your new password.
          </p>
          <Link
            href="/auth/signin"
            className="inline-block px-6 py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-foreground-primary mb-2">
            Reset your password
          </h1>
          <p className="text-sm text-foreground-tertiary">
            Enter your new password below.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            name="password"
            label="New Password"
            type="password"
            value={password}
            onChange={setPassword}
            placeholder="Enter new password"
            required
            showPasswordToggle
          />

          <Input
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={setConfirmPassword}
            placeholder="Confirm new password"
            required
            showPasswordToggle
          />

          {/* Password requirements */}
          <p className="text-xs text-foreground-muted">
            Password must be at least 8 characters long.
          </p>

          <Button
            type="submit"
            disabled={isSubmitting}
            loading={isSubmitting}
            className="w-full"
            variant="primary"
          >
            Reset Password
          </Button>
        </form>
      </div>
    </div>
  );
}
