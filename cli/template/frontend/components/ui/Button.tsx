"use client";

import { forwardRef, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps {
  children: ReactNode;
  type?: "button" | "submit" | "reset";
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      type = "button",
      variant = "primary",
      size = "md",
      disabled = false,
      loading = false,
      className = "",
      onClick,
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]";

    const variants: Record<ButtonVariant, string> = {
      primary:
        "text-white bg-primary-600 hover:bg-primary-700 focus-visible:ring-primary-500 shadow-sm hover:shadow-md",
      secondary:
        "text-foreground-primary bg-muted hover:bg-border focus-visible:ring-primary-500 shadow-sm",
      outline:
        "text-primary-600 dark:text-primary-400 bg-transparent border border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-950 focus-visible:ring-primary-500",
      ghost:
        "text-foreground-secondary bg-transparent hover:bg-muted focus-visible:ring-primary-500",
      danger:
        "text-white bg-red-600 hover:bg-red-700 focus-visible:ring-red-500 shadow-sm hover:shadow-md",
    };

    const sizes: Record<ButtonSize, string> = {
      sm: "px-3 py-2 text-sm",
      md: "px-4 py-2.5 text-sm",
      lg: "px-6 py-3 text-base",
    };

    const handleClick = () => {
      if (!disabled && !loading && onClick) {
        onClick();
      }
    };

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={handleClick}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      >
        {loading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
