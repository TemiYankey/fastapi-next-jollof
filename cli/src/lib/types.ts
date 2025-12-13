/**
 * CLI type definitions.
 */

import type { ColorTheme, PaymentProvider, EmailProvider } from "./constants.js";

export interface ProjectConfig {
  projectName: string;
  appName: string;
  colorTheme: ColorTheme;
  paymentProvider: PaymentProvider;
  emailProvider: EmailProvider;
  frontendPort: number;
  backendPort: number;
  includeDocker: boolean;
  includeExamples: boolean;
  initGit: boolean;
  installDeps: boolean;
}

export interface TemplateContext {
  appName: string;
  dbName: string;
  primaryColor: string; // Tailwind color name (e.g., "indigo") for frontend
  primaryColorHex: string; // Hex value (e.g., "#6366f1") for backend emails
  frontendPort: number;
  backendPort: number;
  // Payment
  isNomba: boolean;
  isStripe: boolean;
  isPaystack: boolean;
  // Email
  isResend: boolean;
  isBrevo: boolean;
  noEmail: boolean;
}
