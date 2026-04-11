/**
 * CLI constants and configuration.
 */

// Tailwind color themes
export const COLOR_THEMES = {
  indigo: {
    name: "Indigo",
    description: "Professional & trustworthy",
    primary: "indigo",
    hex: "#6366f1",
  },
  violet: {
    name: "Violet",
    description: "Creative & modern",
    primary: "violet",
    hex: "#8b5cf6",
  },
  blue: {
    name: "Blue",
    description: "Classic & reliable",
    primary: "blue",
    hex: "#3b82f6",
  },
  emerald: {
    name: "Emerald",
    description: "Fresh & growth-focused",
    primary: "emerald",
    hex: "#10b981",
  },
  rose: {
    name: "Rose",
    description: "Bold & energetic",
    primary: "rose",
    hex: "#f43f5e",
  },
  amber: {
    name: "Amber",
    description: "Warm & inviting",
    primary: "amber",
    hex: "#f59e0b",
  },
  cyan: {
    name: "Cyan",
    description: "Tech & futuristic",
    primary: "cyan",
    hex: "#06b6d4",
  },
  orange: {
    name: "Orange (Jollof)",
    description: "Vibrant & appetizing",
    primary: "orange",
    hex: "#f97316",
  },
} as const;

// Payment providers
export const PAYMENT_PROVIDERS = {
  nomba: {
    name: "Nomba",
    description: "Nigerian payment gateway (cards, transfers)",
    regions: ["Nigeria", "Africa"],
    comingSoon: false,
  },
  paystack: {
    name: "Paystack",
    description: "African payments made simple",
    regions: ["Nigeria", "Ghana", "South Africa", "Kenya"],
    comingSoon: true,
  },
  stripe: {
    name: "Stripe",
    description: "Global payment processing",
    regions: ["Global (190+ countries)"],
    comingSoon: true,
  },
} as const;

// Email providers
export const EMAIL_PROVIDERS = {
  resend: {
    name: "Resend",
    description: "Modern email API, great DX, 3k free/month",
  },
  brevo: {
    name: "Brevo",
    description: "Formerly Sendinblue, 300 free/day",
  },
  none: {
    name: "None (Skip for now)",
    description: "Configure email later",
  },
} as const;

// Project types
export const PROJECT_TYPES = {
  fullstack: {
    name: "Full Stack",
    description: "Both FastAPI backend and Next.js frontend",
  },
  backend: {
    name: "Backend Only",
    description: "FastAPI backend with authentication & payments",
  },
  frontend: {
    name: "Frontend Only",
    description: "Next.js frontend with Supabase auth",
  },
} as const;

// Color hex values for SVG generation
export const COLOR_HEX: Record<string, string> = {
  indigo: "#6366f1",
  violet: "#8b5cf6",
  blue: "#3b82f6",
  emerald: "#10b981",
  rose: "#f43f5e",
  amber: "#f59e0b",
  cyan: "#06b6d4",
  orange: "#f97316",
};

// Type exports
export type ColorTheme = keyof typeof COLOR_THEMES;
export type PaymentProvider = keyof typeof PAYMENT_PROVIDERS;
export type EmailProvider = keyof typeof EMAIL_PROVIDERS;
export type ProjectType = keyof typeof PROJECT_TYPES;
