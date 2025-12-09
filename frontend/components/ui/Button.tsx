"use client";

import { ReactNode } from "react";

interface ButtonProps {
  children: ReactNode;
  type?: "button" | "submit" | "reset";
  variant?: "primary" | "secondary" | "outline";
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

export default function Button({
  children,
  type = "button",
  variant = "primary",
  disabled = false,
  loading = false,
  className = "",
  onClick,
}: ButtonProps) {
  const baseStyles =
    "inline-flex items-center justify-center px-4 py-3 rounded-xl font-medium text-sm transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed";

  const variants = {
    primary: "bg-primary text-white hover:opacity-90",
    secondary: "bg-muted text-foreground-primary hover:bg-border",
    outline:
      "border border-border text-foreground-primary hover:bg-muted bg-transparent",
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      {loading ? (
        <>
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  );
}
