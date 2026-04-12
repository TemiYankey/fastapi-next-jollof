"use client";

import { supabase } from "@/lib/supabase";
import {
  ArrowPathIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type ErrorType = "expired" | "used" | "invalid" | "network" | null;

export default function AuthCallback() {
  const router = useRouter();
  const [status, setStatus] = useState("Processing...");
  const [error, setError] = useState<ErrorType>(null);
  const [userEmail, setUserEmail] = useState<string>("");
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const hashParams = new URLSearchParams(
          window.location.hash.substring(1)
        );

        const code = urlParams.get("code") || hashParams.get("code");
        const type = urlParams.get("type") || hashParams.get("type");
        const email = urlParams.get("email") || hashParams.get("email") || "";

        if (email) {
          setUserEmail(email);
        }

        if (code) {
          setStatus("Completing setup...");

          const { data, error } = await supabase.auth.exchangeCodeForSession(
            window.location.href
          );

          if (error) {
            if (
              error.message.includes("code verifier") ||
              error.message.includes("expired")
            ) {
              setError("expired");
              setStatus("Link expired");
            } else if (
              error.message.includes("invalid_grant") ||
              error.message.includes("already")
            ) {
              setError("used");
              setStatus("Link already used");
            } else if (error.message.includes("invalid")) {
              setError("invalid");
              setStatus("Invalid link");
            } else {
              setError("network");
              setStatus("Connection error");
            }
            return;
          }

          if (data.session) {
            setStatus("Success! Redirecting...");

            if (type === "recovery") {
              router.push("/auth/reset-password");
            } else {
              router.push("/auth/signin");
            }
            return;
          }
        }

        setStatus("Checking authentication...");
        const {
          data: { session },
          error: sessionError,
        } = await supabase.auth.getSession();

        if (session && !sessionError) {
          setStatus("Success! Redirecting...");
          router.push("/auth/signin");
          return;
        }

        setError("invalid");
        setStatus("No authentication data found");
      } catch {
        setStatus("Error occurred...");
        router.push("/auth/signin?error=An unexpected error occurred");
      }
    };

    const timer = setTimeout(handleAuthCallback, 100);
    return () => clearTimeout(timer);
  }, [router]);

  const handleResendConfirmation = async () => {
    if (!userEmail) {
      setStatus("Please sign up again to get a new confirmation email.");
      setTimeout(() => {
        router.push("/auth/signup");
      }, 2000);
      return;
    }

    setIsResending(true);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email: userEmail,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) {
        throw new Error(error.message);
      }

      setStatus("New confirmation email sent!");
      setTimeout(() => {
        router.push(
          "/auth/signin?message=Check your email for the new confirmation link"
        );
      }, 2000);
    } catch (err) {
      console.error("Resend error:", err);
      setStatus("Failed to send email. Please try signing up again.");
      setTimeout(() => {
        router.push("/auth/signup");
      }, 2000);
    } finally {
      setIsResending(false);
    }
  };

  if (error) {
    return (
      <div className="fixed inset-0 bg-background z-50 flex flex-col items-center justify-center p-6">
        <div className="max-w-md text-center">
          <div className="mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full mb-4">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            <h1 className="text-xl font-semibold text-foreground-primary mb-2">
              {error === "expired" && "Confirmation Link Failed"}
              {error === "used" && "Link Already Used"}
              {error === "invalid" && "Invalid Confirmation Link"}
              {error === "network" && "Connection Problem"}
            </h1>
            <p className="text-foreground-tertiary mb-4">
              {error === "expired" &&
                "For your security, confirmation links must be opened in the same browser you used to sign up."}
              {error === "used" &&
                "For your security, confirmation links can only be used once."}
              {error === "invalid" &&
                "This confirmation link is invalid or malformed."}
              {error === "network" &&
                "There was a problem connecting to our servers. Please try again."}
            </p>
          </div>

          <div className="space-y-3">
            {(error === "expired" || error === "used") && (
              <>
                {!userEmail && (
                  <input
                    type="email"
                    value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                    placeholder="Enter your email address"
                    className="w-full px-4 py-3 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-background"
                  />
                )}
                <button
                  onClick={handleResendConfirmation}
                  disabled={isResending || !userEmail}
                  className="w-full flex justify-center items-center py-3 px-4 bg-primary hover:opacity-90 text-white rounded-xl font-medium transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isResending ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <ArrowPathIcon className="w-4 h-4 mr-2" />
                      Send New Confirmation Email
                    </>
                  )}
                </button>
              </>
            )}

            <Link
              href="/auth/signup"
              className="block w-full py-3 px-4 bg-muted hover:bg-border text-foreground-secondary rounded-xl font-medium text-center transition-colors"
            >
              Sign Up Again
            </Link>

            <Link
              href="/auth/signin"
              className="block w-full py-3 px-4 border border-border hover:bg-muted text-foreground-secondary rounded-xl font-medium text-center transition-colors"
            >
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-background z-50 flex flex-col items-center justify-center">
      <div className="w-8 h-8 border-2 border-border border-t-primary-600 rounded-full animate-spin mb-4"></div>
      <p className="text-foreground-tertiary text-sm">{status}</p>
    </div>
  );
}
