"use client";

import { CheckIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useMemo } from "react";

interface PasswordRequirement {
  label: string;
  validator: (password: string) => boolean;
}

interface PasswordStrengthProps {
  password: string;
  className?: string;
}

const requirements: PasswordRequirement[] = [
  {
    label: "At least 8 characters",
    validator: (pw) => pw.length >= 8,
  },
  {
    label: "Contains uppercase letter",
    validator: (pw) => /[A-Z]/.test(pw),
  },
  {
    label: "Contains lowercase letter",
    validator: (pw) => /[a-z]/.test(pw),
  },
  {
    label: "Contains a number",
    validator: (pw) => /\d/.test(pw),
  },
];

export function validatePassword(password: string): boolean {
  return requirements.every((req) => req.validator(password));
}

export function getPasswordStrength(password: string): {
  score: number;
  label: string;
  color: string;
} {
  const passed = requirements.filter((req) => req.validator(password)).length;
  const score = (passed / requirements.length) * 100;

  if (score === 0) return { score, label: "", color: "bg-border" };
  if (score <= 25) return { score, label: "Weak", color: "bg-red-500" };
  if (score <= 50) return { score, label: "Fair", color: "bg-orange-500" };
  if (score <= 75) return { score, label: "Good", color: "bg-yellow-500" };
  return { score, label: "Strong", color: "bg-green-500" };
}

export default function PasswordStrength({
  password,
  className = "",
}: PasswordStrengthProps) {
  const strength = useMemo(() => getPasswordStrength(password), [password]);
  const passedCount = useMemo(
    () => requirements.filter((req) => req.validator(password)).length,
    [password]
  );

  if (!password) return null;

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Strength bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between items-center">
          <span className="text-xs text-foreground-muted">Password strength</span>
          {strength.label && (
            <span
              className={`text-xs font-medium ${
                strength.score === 100
                  ? "text-green-600 dark:text-green-400"
                  : strength.score >= 50
                  ? "text-yellow-600 dark:text-yellow-400"
                  : "text-red-600 dark:text-red-400"
              }`}
            >
              {strength.label}
            </span>
          )}
        </div>
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ease-out ${strength.color}`}
            style={{ width: `${strength.score}%` }}
          />
        </div>
      </div>

      {/* Requirements checklist */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
        {requirements.map((req) => {
          const passed = req.validator(password);
          return (
            <div
              key={req.label}
              className={`flex items-center gap-1.5 text-xs transition-colors ${
                passed
                  ? "text-green-600 dark:text-green-400"
                  : "text-foreground-muted"
              }`}
            >
              {passed ? (
                <CheckIcon className="h-3.5 w-3.5 flex-shrink-0" />
              ) : (
                <XMarkIcon className="h-3.5 w-3.5 flex-shrink-0" />
              )}
              <span>{req.label}</span>
            </div>
          );
        })}
      </div>

      {/* Progress indicator */}
      <p className="text-xs text-foreground-muted">
        {passedCount} of {requirements.length} requirements met
      </p>
    </div>
  );
}
