"use client";

import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";
import { useState } from "react";

interface InputProps {
  name: string;
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  showPasswordToggle?: boolean;
  error?: string;
  disabled?: boolean;
}

export default function Input({
  name,
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  required = false,
  showPasswordToggle = false,
  error,
  disabled = false,
}: InputProps) {
  const [showPassword, setShowPassword] = useState(false);

  const inputType = showPasswordToggle && showPassword ? "text" : type;

  return (
    <div className="space-y-1.5">
      <label
        htmlFor={name}
        className="block text-sm font-medium text-foreground-primary"
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="relative">
        <input
          id={name}
          name={name}
          type={inputType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          className={`
            w-full px-4 py-3 rounded-xl border bg-background text-foreground-primary
            placeholder:text-foreground-muted text-sm
            focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            ${error ? "border-red-500" : "border-border"}
            ${showPasswordToggle ? "pr-12" : ""}
          `}
        />
        {showPasswordToggle && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-foreground-muted hover:text-foreground-secondary"
          >
            {showPassword ? (
              <EyeSlashIcon className="h-5 w-5" />
            ) : (
              <EyeIcon className="h-5 w-5" />
            )}
          </button>
        )}
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
