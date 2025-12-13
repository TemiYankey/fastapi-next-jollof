/**
 * Template processing functions.
 */

import Handlebars from "handlebars";
import { COLOR_THEMES, COLOR_HEX } from "./constants.js";
import type { ProjectConfig, TemplateContext } from "./types.js";

/**
 * Create a template context from project config.
 * @param config - The project configuration
 * @returns Template context for Handlebars
 */
export function createTemplateContext(config: ProjectConfig): TemplateContext {
  return {
    appName: config.appName,
    dbName: config.projectName.replace(/-/g, "_"),
    primaryColor: COLOR_THEMES[config.colorTheme].primary,
    primaryColorHex: COLOR_THEMES[config.colorTheme].hex,
    frontendPort: config.frontendPort,
    backendPort: config.backendPort,
    // Payment flags
    isNomba: config.paymentProvider === "nomba",
    isStripe: config.paymentProvider === "stripe",
    isPaystack: config.paymentProvider === "paystack",
    // Email flags
    isResend: config.emailProvider === "resend",
    isBrevo: config.emailProvider === "brevo",
    noEmail: config.emailProvider === "none",
  };
}

/**
 * Render a Handlebars template string with context.
 * @param templateContent - The template content
 * @param context - The template context
 * @returns Rendered string
 */
export function renderTemplateString(templateContent: string, context: TemplateContext): string {
  const template = Handlebars.compile(templateContent);
  return template(context);
}

/**
 * Convert a project name to a display name.
 * @param projectName - The project name (e.g., "my-awesome-app")
 * @returns Display name (e.g., "My Awesome App")
 */
export function projectNameToDisplayName(projectName: string): string {
  return projectName
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

/**
 * Generate a logo SVG.
 * @param appName - The app name
 * @param color - The color theme name
 * @returns SVG string
 */
export function generateLogoSvg(appName: string, color: string): string {
  const initials = appName
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const hexColor = COLOR_HEX[color] || COLOR_HEX.indigo;

  return `<svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:${hexColor};stop-opacity:1" />
      <stop offset="100%" style="stop-color:${hexColor}dd;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="96" fill="url(#bgGradient)"/>
  <text x="256" y="300" font-family="system-ui, -apple-system, sans-serif" font-size="200" font-weight="700" fill="white" text-anchor="middle">${initials}</text>
</svg>`;
}

/**
 * Generate a favicon SVG.
 * @param appName - The app name
 * @param color - The color theme name
 * @returns SVG string
 */
export function generateFaviconSvg(appName: string, color: string): string {
  const initial = appName[0].toUpperCase();
  const hexColor = COLOR_HEX[color] || COLOR_HEX.indigo;

  return `<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="6" fill="${hexColor}"/>
  <text x="16" y="22" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="700" fill="white" text-anchor="middle">${initial}</text>
</svg>`;
}

/**
 * Update tailwind config content with new primary color.
 * @param content - The tailwind config content
 * @param primaryColor - The primary color name
 * @returns Updated content
 */
export function updateTailwindConfig(content: string, primaryColor: string): string {
  return content.replace(/primary:\s*colors\.\w+/g, `primary: colors.${primaryColor}`);
}

/**
 * Get the list of template files to apply.
 * @param includeDocker - Whether to include Docker files
 * @returns Array of [templateName, outputPath] tuples
 */
export function getTemplateFiles(includeDocker: boolean): [string, string][] {
  const baseTemplates: [string, string][] = [
    ["backend.env.hbs", "backend/.env.example"],
    ["backend.env.test.hbs", "backend/.env.test"],
    ["frontend.env.hbs", "frontend/.env.example"],
    ["requirements.txt.hbs", "backend/requirements.txt"],
    ["config.py.hbs", "backend/app/core/config.py"],
    ["billing-providers-init.py.hbs", "backend/app/billing/providers/__init__.py"],
    ["billing-enums.py.hbs", "backend/app/billing/enums.py"],
    ["billing-models.py.hbs", "backend/app/billing/models.py"],
    ["billing-routes.py.hbs", "backend/app/billing/routes.py"],
    ["email-providers-init.py.hbs", "backend/app/emails/providers/__init__.py"],
    ["email-enums.py.hbs", "backend/app/emails/enums.py"],
    ["email-service.py.hbs", "backend/app/emails/service.py"],
    ["backend-makefile.hbs", "backend/Makefile"],
    ["frontend-makefile.hbs", "frontend/Makefile"],
    ["test-email-providers.py.hbs", "backend/tests/unit/emails/test_providers.py"],
    ["test-email-factories.py.hbs", "backend/tests/unit/emails/factories.py"],
    ["test-email-service.py.hbs", "backend/tests/unit/emails/test_service.py"],
    ["test-email-schemas.py.hbs", "backend/tests/unit/emails/test_schemas.py"],
    ["test-billing-enums.py.hbs", "backend/tests/unit/billing/test_enums.py"],
    ["test-billing-models.py.hbs", "backend/tests/unit/billing/test_models.py"],
    ["test-billing-routes.py.hbs", "backend/tests/unit/billing/test_routes.py"],
    ["test-config.py.hbs", "backend/tests/unit/core/test_config.py"],
    ["conftest.py.hbs", "backend/tests/conftest.py"],
    ["gitignore.hbs", ".gitignore"],
  ];

  if (includeDocker) {
    return [
      ...baseTemplates,
      ["docker-compose.yml.hbs", "docker-compose.yml"],
      ["backend-dockerfile.hbs", "backend/Dockerfile"],
      ["frontend-dockerfile.hbs", "frontend/Dockerfile"],
      ["backend-dockerignore.hbs", "backend/.dockerignore"],
      ["frontend-dockerignore.hbs", "frontend/.dockerignore"],
    ];
  }

  return baseTemplates;
}

/**
 * Get files to remove based on provider selection.
 */
export function getFilesToRemove(
  paymentProvider: string,
  emailProvider: string
): { paymentFiles: string[]; emailFiles: string[]; paymentTestFiles: string[] } {
  const paymentFiles: Record<string, string> = {
    nomba: "nomba.py",
    stripe: "stripe.py",
    paystack: "paystack.py",
  };

  const emailFiles: Record<string, string> = {
    resend: "resend.py",
    brevo: "brevo.py",
  };

  const paymentTestFiles: Record<string, string> = {
    nomba: "test_nomba_provider.py",
    stripe: "test_stripe_provider.py",
    paystack: "test_paystack_provider.py",
  };

  // Payment files to remove
  const removePaymentFiles = Object.entries(paymentFiles)
    .filter(([provider]) => provider !== paymentProvider)
    .map(([, filename]) => filename);

  // Email files to remove
  let removeEmailFiles: string[] = [];
  if (emailProvider === "none") {
    removeEmailFiles = Object.values(emailFiles);
  } else {
    removeEmailFiles = Object.entries(emailFiles)
      .filter(([provider]) => provider !== emailProvider)
      .map(([, filename]) => filename);
  }

  // Payment test files to remove
  const removePaymentTestFiles = Object.entries(paymentTestFiles)
    .filter(([provider]) => provider !== paymentProvider)
    .map(([, filename]) => filename);

  return {
    paymentFiles: removePaymentFiles,
    emailFiles: removeEmailFiles,
    paymentTestFiles: removePaymentTestFiles,
  };
}
