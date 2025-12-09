"use client";

import Button from "@/components/ui/Button";
import { GoogleSignInButton } from "@/components/ui/GoogleSignInButton";
import Input from "@/components/ui/Input";
import PasswordStrength, { validatePassword } from "@/components/ui/PasswordStrength";
import { useAuth } from "@/contexts/AuthContext";
import { config } from "@/lib/config";
import { ArrowRightIcon, CheckCircleIcon } from "@heroicons/react/24/outline";
import Link from "next/link";
import { useState } from "react";

export default function SignUpPage() {
  const { signup } = useAuth();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");

    // Password validation
    if (!validatePassword(formData.password)) {
      setError("Please meet all password requirements.");
      setIsSubmitting(false);
      return;
    }

    try {
      await signup(formData);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create account");
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

  if (success) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full mb-4">
            <CheckCircleIcon className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-2xl font-semibold text-foreground-primary mb-2">
            Check your email
          </h1>
          <p className="text-foreground-tertiary mb-6">
            We&apos;ve sent a confirmation link to{" "}
            <span className="font-medium text-foreground-primary">
              {formData.email}
            </span>
            . Click the link to activate your account.
          </p>
          <p className="text-sm text-foreground-muted mb-6">
            Make sure to check your spam folder if you don&apos;t see it.
          </p>
          <Link
            href="/auth/signin"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Back to Sign In
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
            Create your account
          </h1>
          <p className="text-sm text-foreground-tertiary">
            Join {config.appName} and get started today.
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
          <div className="grid grid-cols-2 gap-4">
            <Input
              name="firstName"
              label="First name"
              value={formData.firstName}
              onChange={(value) => handleChange("firstName", value)}
              placeholder="John"
              required
            />
            <Input
              name="lastName"
              label="Last name"
              value={formData.lastName}
              onChange={(value) => handleChange("lastName", value)}
              placeholder="Doe"
              required
            />
          </div>

          <Input
            name="email"
            label="Email address"
            type="email"
            value={formData.email}
            onChange={(value) => handleChange("email", value)}
            placeholder="john@example.com"
            required
          />

          <Input
            name="password"
            label="Password"
            type="password"
            value={formData.password}
            onChange={(value) => handleChange("password", value)}
            placeholder="Create a password"
            required
            showPasswordToggle
          />

          {/* Password strength indicator */}
          <PasswordStrength password={formData.password} />

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting}
            loading={isSubmitting}
            className="w-full"
            variant="primary"
          >
            Create account
            <ArrowRightIcon className="ml-2 h-4 w-4" />
          </Button>
        </form>

        {/* Sign in link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-foreground-tertiary">
            Already have an account?{" "}
            <Link
              href="/auth/signin"
              className="font-medium text-primary-600 hover:text-primary-700"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
