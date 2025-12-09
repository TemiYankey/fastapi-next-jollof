"use client";

import Button from "@/components/ui/Button";
import { GoogleSignInButton } from "@/components/ui/GoogleSignInButton";
import Input from "@/components/ui/Input";
import { useAuth } from "@/contexts/AuthContext";
import { config } from "@/lib/config";
import { ArrowRightIcon } from "@heroicons/react/24/outline";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const getErrorMessage = (error: string): string => {
  const lowerError = error.toLowerCase();

  if (
    lowerError.includes("invalid login credentials") ||
    lowerError.includes("invalid email or password")
  ) {
    return "Invalid email or password. Please check your credentials and try again.";
  }
  if (lowerError.includes("email not confirmed")) {
    return "Please check your email and click the confirmation link to activate your account.";
  }
  if (lowerError.includes("too many requests")) {
    return "Too many login attempts. Please wait a few minutes before trying again.";
  }
  if (lowerError.includes("user not found")) {
    return "No account found with this email address. Please sign up first.";
  }

  return error;
};

export default function SignInPage() {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    if (!authLoading) {
      if (isAuthenticated) {
        router.push("/dashboard");
      } else {
        setShowForm(true);
      }
    }
  }, [authLoading, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      await login(formData.email, formData.password);

      const urlParams = new URLSearchParams(window.location.search);
      const nextUrl = urlParams.get("next");

      if (nextUrl) {
        router.push(decodeURIComponent(nextUrl));
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      const rawMessage =
        err instanceof Error ? err.message : "Invalid email or password";
      const friendlyMessage = getErrorMessage(rawMessage);
      setError(friendlyMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (name: string, value: string) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  if (!showForm) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-border border-t-primary-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-foreground-primary mb-2">
            Sign in to {config.appName}
          </h1>
          <p className="text-sm text-foreground-tertiary">
            Enter your credentials to access your account.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Google Sign In */}
        <div className="mb-6">
          <GoogleSignInButton size="md" />

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-background text-foreground-muted">
                Or continue with email
              </span>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            name="email"
            label="Email address"
            type="email"
            value={formData.email}
            onChange={(value) => handleChange("email", value)}
            placeholder="Enter your email"
            required
          />

          <Input
            name="password"
            label="Password"
            type="password"
            value={formData.password}
            onChange={(value) => handleChange("password", value)}
            placeholder="Enter your password"
            required
            showPasswordToggle
          />

          {/* Forgot password */}
          <div className="flex justify-end">
            <Link
              href="/auth/forgot-password"
              className="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              Forgot password?
            </Link>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting}
            loading={isSubmitting}
            className="w-full"
            variant="primary"
          >
            Sign in
            <ArrowRightIcon className="ml-2 h-4 w-4" />
          </Button>
        </form>

        {/* Sign up link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-foreground-tertiary">
            Don&apos;t have an account?{" "}
            <Link
              href="/auth/signup"
              className="font-medium text-primary-600 hover:text-primary-700"
            >
              Create one now
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
