"use client";

import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";
import { forwardRef, useState } from "react";

export type InputSize = "sm" | "md" | "lg";

interface InputProps {
  name: string;
  label?: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  showPasswordToggle?: boolean;
  size?: InputSize;
  className?: string;
}

const sizeClasses: Record<InputSize, string> = {
  sm: "px-3 py-2 text-sm",
  md: "px-4 py-2.5 text-sm",
  lg: "px-4 py-3 text-base",
};

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      name,
      label,
      type = "text",
      placeholder,
      value,
      onChange,
      error,
      disabled = false,
      required = false,
      showPasswordToggle = false,
      size = "md",
      className = "",
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.value);
    };

    const isPasswordType = type === "password";
    const inputType =
      isPasswordType && showPasswordToggle && showPassword ? "text" : type;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={name}
            className="block text-sm font-medium text-foreground-secondary mb-1.5"
          >
            {label}
            {required && <span className="text-primary-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          <input
            ref={ref}
            id={name}
            name={name}
            type={inputType}
            value={value}
            onChange={handleChange}
            placeholder={placeholder}
            disabled={disabled}
            required={required}
            className={`
              block w-full border rounded-xl
              bg-input text-foreground-primary
              placeholder:text-foreground-muted
              focus:outline-none focus:ring-1 focus:ring-primary-500/50 focus:border-primary-500
              transition-all duration-200
              ${sizeClasses[size]}
              ${isPasswordType && showPasswordToggle ? "pr-11" : ""}
              ${error ? "border-red-500 focus:ring-1 focus:ring-red-500/50 focus:border-red-500" : "border-input-border"}
              ${disabled ? "opacity-50 cursor-not-allowed" : ""}
              ${className}
            `}
            aria-invalid={error ? "true" : "false"}
            aria-describedby={error ? `${name}-error` : undefined}
          />

          {showPasswordToggle && isPasswordType && (
            <button
              type="button"
              tabIndex={-1}
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-foreground-muted hover:text-foreground-secondary transition-colors"
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          )}
        </div>

        {error && (
          <p id={`${name}-error`} className="mt-1.5 text-sm text-red-500">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
