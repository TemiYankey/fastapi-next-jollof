/**
 * Integration tests for CLI flow.
 * These tests actually scaffold projects and verify the output.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "fs-extra";
import path from "path";
import { execSync } from "child_process";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the built CLI
const CLI_PATH = path.resolve(__dirname, "..", "..", "dist", "index.js");
const TEST_DIR = "/tmp/cli-integration-tests";

describe("CLI Integration Tests", () => {
  beforeEach(() => {
    // Clean up test directory before each test
    fs.removeSync(TEST_DIR);
    fs.ensureDirSync(TEST_DIR);
  });

  afterEach(() => {
    // Clean up after tests
    fs.removeSync(TEST_DIR);
  });

  describe("Provider Selection", () => {
    describe("Email Providers", () => {
      it("scaffolds with Resend provider correctly", () => {
        const projectName = "test-resend";
        execSync(`node ${CLI_PATH} ${projectName} --email resend --no-install --no-git`, {
          cwd: TEST_DIR,
          stdio: "ignore",
        });

        const projectDir = path.join(TEST_DIR, projectName);

        // Verify Resend provider file exists
        expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/resend.py"))).toBe(true);

        // Verify config has resend dependency
        const requirements = fs.readFileSync(path.join(projectDir, "backend/requirements.txt"), "utf-8");
        expect(requirements).toContain("resend==");

        // Verify email service imports Resend
        const emailService = fs.readFileSync(path.join(projectDir, "backend/app/emails/service.py"), "utf-8");
        expect(emailService).toContain("ResendProvider");

        // Verify providers __init__.py exports Resend
        const providersInit = fs.readFileSync(path.join(projectDir, "backend/app/emails/providers/__init__.py"), "utf-8");
        expect(providersInit).toContain("ResendProvider");

        // Verify .env.example has Resend config
        const envExample = fs.readFileSync(path.join(projectDir, "backend/.env.example"), "utf-8");
        expect(envExample).toContain("RESEND_API_KEY");
      });

      it("scaffolds with Brevo provider correctly", () => {
        const projectName = "test-brevo";
        execSync(`node ${CLI_PATH} ${projectName} --email brevo --no-install --no-git`, {
          cwd: TEST_DIR,
          stdio: "ignore",
        });

        const projectDir = path.join(TEST_DIR, projectName);

        // Verify Brevo provider file exists
        expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/brevo.py"))).toBe(true);

        // Verify config has brevo dependency (sib-api-v3-sdk)
        const requirements = fs.readFileSync(path.join(projectDir, "backend/requirements.txt"), "utf-8");
        expect(requirements).toContain("sib-api-v3-sdk");

        // Verify email service imports Brevo
        const emailService = fs.readFileSync(path.join(projectDir, "backend/app/emails/service.py"), "utf-8");
        expect(emailService).toContain("BrevoProvider");

        // Verify providers __init__.py exports Brevo
        const providersInit = fs.readFileSync(path.join(projectDir, "backend/app/emails/providers/__init__.py"), "utf-8");
        expect(providersInit).toContain("BrevoProvider");

        // Verify .env.example has Brevo config
        const envExample = fs.readFileSync(path.join(projectDir, "backend/.env.example"), "utf-8");
        expect(envExample).toContain("BREVO_API_KEY");
      });

      it("scaffolds with no email provider correctly", () => {
        const projectName = "test-no-email";
        execSync(`node ${CLI_PATH} ${projectName} --email none --no-install --no-git`, {
          cwd: TEST_DIR,
          stdio: "ignore",
        });

        const projectDir = path.join(TEST_DIR, projectName);

        // Verify email directory exists but no provider files
        expect(fs.existsSync(path.join(projectDir, "backend/app/emails"))).toBe(true);
      });
    });

    describe("Payment Providers", () => {
      it("scaffolds with Nomba provider correctly", () => {
        const projectName = "test-nomba";
        execSync(`node ${CLI_PATH} ${projectName} --payment nomba --no-install --no-git`, {
          cwd: TEST_DIR,
          stdio: "ignore",
        });

        const projectDir = path.join(TEST_DIR, projectName);

        // Verify Nomba provider file exists
        expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/nomba.py"))).toBe(true);

        // Verify Nomba test file exists
        expect(fs.existsSync(path.join(projectDir, "backend/tests/unit/billing/test_nomba_provider.py"))).toBe(true);

        // Verify billing providers __init__.py exports Nomba
        const providersInit = fs.readFileSync(path.join(projectDir, "backend/app/billing/providers/__init__.py"), "utf-8");
        expect(providersInit).toContain("NombaPaymentProvider");

        // Verify billing enums have NOMBA provider
        const enums = fs.readFileSync(path.join(projectDir, "backend/app/billing/enums.py"), "utf-8");
        expect(enums).toContain('NOMBA = "nomba"');

        // Verify .env.example has Nomba config
        const envExample = fs.readFileSync(path.join(projectDir, "backend/.env.example"), "utf-8");
        expect(envExample).toContain("NOMBA_CLIENT_ID");

        // Verify conftest has Nomba env vars
        const conftest = fs.readFileSync(path.join(projectDir, "backend/tests/conftest.py"), "utf-8");
        expect(conftest).toContain("NOMBA_CLIENT_ID");
      });

      it("scaffolds with Stripe provider correctly", () => {
        const projectName = "test-stripe";
        execSync(`node ${CLI_PATH} ${projectName} --payment stripe --no-install --no-git`, {
          cwd: TEST_DIR,
          stdio: "ignore",
        });

        const projectDir = path.join(TEST_DIR, projectName);

        // Verify Stripe provider file exists
        expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/stripe.py"))).toBe(true);

        // Verify Stripe test file exists
        expect(fs.existsSync(path.join(projectDir, "backend/tests/unit/billing/test_stripe_provider.py"))).toBe(true);

        // Verify billing providers __init__.py exports Stripe
        const providersInit = fs.readFileSync(path.join(projectDir, "backend/app/billing/providers/__init__.py"), "utf-8");
        expect(providersInit).toContain("StripeProvider");

        // Verify billing enums have STRIPE provider
        const enums = fs.readFileSync(path.join(projectDir, "backend/app/billing/enums.py"), "utf-8");
        expect(enums).toContain('STRIPE = "stripe"');

        // Verify .env.example has Stripe config
        const envExample = fs.readFileSync(path.join(projectDir, "backend/.env.example"), "utf-8");
        expect(envExample).toContain("STRIPE_SECRET_KEY");

        // Verify conftest has Stripe env vars
        const conftest = fs.readFileSync(path.join(projectDir, "backend/tests/conftest.py"), "utf-8");
        expect(conftest).toContain("STRIPE_SECRET_KEY");
      });

      it("scaffolds with Paystack provider correctly", () => {
        const projectName = "test-paystack";
        execSync(`node ${CLI_PATH} ${projectName} --payment paystack --no-install --no-git`, {
          cwd: TEST_DIR,
          stdio: "ignore",
        });

        const projectDir = path.join(TEST_DIR, projectName);

        // Verify Paystack provider file exists
        expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/paystack.py"))).toBe(true);

        // Verify Paystack test file exists
        expect(fs.existsSync(path.join(projectDir, "backend/tests/unit/billing/test_paystack_provider.py"))).toBe(true);

        // Verify billing providers __init__.py exports Paystack
        const providersInit = fs.readFileSync(path.join(projectDir, "backend/app/billing/providers/__init__.py"), "utf-8");
        expect(providersInit).toContain("PaystackProvider");

        // Verify billing enums have PAYSTACK provider
        const enums = fs.readFileSync(path.join(projectDir, "backend/app/billing/enums.py"), "utf-8");
        expect(enums).toContain('PAYSTACK = "paystack"');

        // Verify .env.example has Paystack config
        const envExample = fs.readFileSync(path.join(projectDir, "backend/.env.example"), "utf-8");
        expect(envExample).toContain("PAYSTACK_SECRET_KEY");

        // Verify conftest has Paystack env vars
        const conftest = fs.readFileSync(path.join(projectDir, "backend/tests/conftest.py"), "utf-8");
        expect(conftest).toContain("PAYSTACK_SECRET_KEY");
      });
    });

    describe("Color Themes", () => {
      const themes = [
        { name: "indigo", hex: "#6366f1" },
        { name: "rose", hex: "#f43f5e" },
        { name: "emerald", hex: "#10b981" },
        { name: "cyan", hex: "#06b6d4" },
        { name: "amber", hex: "#f59e0b" },
        { name: "violet", hex: "#8b5cf6" },
        { name: "blue", hex: "#3b82f6" },
        { name: "orange", hex: "#f97316" },
      ];

      themes.forEach(({ name, hex }) => {
        it(`scaffolds with ${name} theme correctly`, () => {
          const projectName = `test-${name}`;
          execSync(`node ${CLI_PATH} ${projectName} --theme ${name} --no-install --no-git`, {
            cwd: TEST_DIR,
            stdio: "ignore",
          });

          const projectDir = path.join(TEST_DIR, projectName);

          // Verify backend config has correct hex color
          const config = fs.readFileSync(path.join(projectDir, "backend/app/core/config.py"), "utf-8");
          expect(config).toContain(`primary_color: str = "${hex}"`);

          // Verify tailwind config has correct color
          const tailwindConfig = fs.readFileSync(path.join(projectDir, "frontend/tailwind.config.ts"), "utf-8");
          expect(tailwindConfig).toContain(`primary: colors.${name}`);

          // Verify logo SVG has correct color
          const logo = fs.readFileSync(path.join(projectDir, "frontend/public/logo.svg"), "utf-8");
          expect(logo).toContain(hex);

          // Verify favicon SVG has correct color
          const favicon = fs.readFileSync(path.join(projectDir, "frontend/public/favicon.svg"), "utf-8");
          expect(favicon).toContain(hex);
        });
      });
    });
  });

  describe("Project Structure", () => {
    it("creates all required directories", () => {
      const projectName = "test-structure";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Backend directories
      expect(fs.existsSync(path.join(projectDir, "backend/app"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/core"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/users"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/tests"))).toBe(true);

      // Frontend directories
      expect(fs.existsSync(path.join(projectDir, "frontend/app"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/components"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/public"))).toBe(true);
    });

    it("creates all required config files", () => {
      const projectName = "test-configs";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Backend config files
      expect(fs.existsSync(path.join(projectDir, "backend/.env.example"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/.env.test"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/requirements.txt"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/Makefile"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/tests/conftest.py"))).toBe(true);

      // Frontend config files
      expect(fs.existsSync(path.join(projectDir, "frontend/.env.example"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/package.json"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/tailwind.config.ts"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/Makefile"))).toBe(true);

      // Root files
      expect(fs.existsSync(path.join(projectDir, ".gitignore"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "docker-compose.yml"))).toBe(true);
    });

    it("updates frontend package.json with project name", () => {
      const projectName = "my-custom-app";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const pkg = fs.readJsonSync(path.join(projectDir, "frontend/package.json"));
      expect(pkg.name).toBe(projectName);
    });
  });

  describe("Template Context", () => {
    it("sets correct app name from project name", () => {
      const projectName = "my-awesome-app";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Config should have display name
      const config = fs.readFileSync(path.join(projectDir, "backend/app/core/config.py"), "utf-8");
      expect(config).toContain('app_name: str = "My Awesome App"');
    });

    it("sets correct database name (hyphens to underscores)", () => {
      const projectName = "my-test-app";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Config should have db name with underscores
      const config = fs.readFileSync(path.join(projectDir, "backend/app/core/config.py"), "utf-8");
      expect(config).toContain("my_test_app");
    });

    it("sets correct ports when specified", () => {
      const projectName = "test-ports";
      execSync(`node ${CLI_PATH} ${projectName} --frontend-port 4000 --backend-port 9000 --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Frontend env should have correct port
      const frontendEnv = fs.readFileSync(path.join(projectDir, "frontend/.env.example"), "utf-8");
      expect(frontendEnv).toContain("9000"); // Backend URL with port 9000

      // Backend Makefile should have correct port
      const backendMakefile = fs.readFileSync(path.join(projectDir, "backend/Makefile"), "utf-8");
      expect(backendMakefile).toContain("9000");
    });
  });

  describe("Docker Configuration", () => {
    it("includes Docker files by default", () => {
      const projectName = "test-docker-default";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      expect(fs.existsSync(path.join(projectDir, "docker-compose.yml"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/Dockerfile"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/Dockerfile"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/.dockerignore"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "frontend/.dockerignore"))).toBe(true);
    });
  });

  describe("Email Templates", () => {
    it("includes Jinja2 email templates", () => {
      const projectName = "test-email-templates";
      execSync(`node ${CLI_PATH} ${projectName} --email resend --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const templatesDir = path.join(projectDir, "backend/app/emails/templates");

      // App templates
      expect(fs.existsSync(path.join(templatesDir, "app/base.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "app/welcome.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "app/password_reset.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "app/email_verification.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "app/payment_success.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "app/payment_failed.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "app/generic.html"))).toBe(true);

      // Supabase templates
      expect(fs.existsSync(path.join(templatesDir, "supabase/confirm_email.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "supabase/reset_password.html"))).toBe(true);
      expect(fs.existsSync(path.join(templatesDir, "supabase/magic_link.html"))).toBe(true);
    });

    it("email templates directory NOT included when email is none", () => {
      const projectName = "test-no-email-templates";
      execSync(`node ${CLI_PATH} ${projectName} --email none --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Email templates should still exist (they're part of base template)
      // but the providers won't be present
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/resend.py"))).toBe(false);
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/brevo.py"))).toBe(false);
    });
  });

  describe("Test Safety", () => {
    it("conftest.py has FORCE environment overrides with Tortoise format", () => {
      const projectName = "test-safety";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const conftest = fs.readFileSync(path.join(projectDir, "backend/tests/conftest.py"), "utf-8");

      // Should have FORCE overrides
      expect(conftest).toContain('os.environ["DATABASE_URL"] = "sqlite://:memory:"');
      expect(conftest).toContain('os.environ["ENVIRONMENT"] = "testing"');
    });

    it(".env.test has safe test values", () => {
      const projectName = "test-env-test";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const envTest = fs.readFileSync(path.join(projectDir, "backend/.env.test"), "utf-8");

      expect(envTest).toContain("ENVIRONMENT=testing");
      expect(envTest).toContain("sqlite");
    });
  });

  describe("Billing Enums", () => {
    it("has correct PaymentStatus values", () => {
      const projectName = "test-enums";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const enums = fs.readFileSync(path.join(projectDir, "backend/app/billing/enums.py"), "utf-8");

      // Should have correct status values
      expect(enums).toContain('PENDING = "pending"');
      expect(enums).toContain('SUCCESS = "success"');
      expect(enums).toContain('FAILED = "failed"');
      expect(enums).toContain('CANCELLED = "cancelled"');
      expect(enums).toContain('EXPIRED = "expired"');
    });

    it("has correct PaymentMethod values", () => {
      const projectName = "test-methods";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const enums = fs.readFileSync(path.join(projectDir, "backend/app/billing/enums.py"), "utf-8");

      // Should have correct method values
      expect(enums).toContain('CARD = "card"');
      expect(enums).toContain('BANK_TRANSFER = "bank_transfer"');
      expect(enums).toContain('UNKNOWN = "unknown"');
    });
  });

  describe("FastAPI Lifespan", () => {
    it("main.py uses lifespan context manager", () => {
      const projectName = "test-lifespan";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const mainPy = fs.readFileSync(path.join(projectDir, "backend/app/main.py"), "utf-8");

      // Should use lifespan pattern
      expect(mainPy).toContain("@asynccontextmanager");
      expect(mainPy).toContain("async def lifespan");
      expect(mainPy).toContain("lifespan=lifespan");
    });
  });

  describe("Tortoise ORM", () => {
    it("uses Tortoise ORM async", () => {
      const projectName = "test-tortoise";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Check requirements has Tortoise ORM
      const requirements = fs.readFileSync(path.join(projectDir, "backend/requirements.txt"), "utf-8");
      expect(requirements).toContain("tortoise-orm");
      expect(requirements).toContain("asyncpg");
    });
  });

  describe("Combined Provider Configurations", () => {
    it("scaffolds correctly with Brevo + Nomba + Emerald", () => {
      const projectName = "test-combo-1";
      execSync(`node ${CLI_PATH} ${projectName} --email brevo --payment nomba --theme emerald --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Email: Brevo
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/brevo.py"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/resend.py"))).toBe(false);

      // Payment: Nomba
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/nomba.py"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/stripe.py"))).toBe(false);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/paystack.py"))).toBe(false);

      // Theme: Emerald
      const config = fs.readFileSync(path.join(projectDir, "backend/app/core/config.py"), "utf-8");
      expect(config).toContain('primary_color: str = "#10b981"');
    });

    it("scaffolds correctly with Resend + Stripe + Rose", () => {
      const projectName = "test-combo-2";
      execSync(`node ${CLI_PATH} ${projectName} --email resend --payment stripe --theme rose --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Email: Resend
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/resend.py"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/brevo.py"))).toBe(false);

      // Payment: Stripe
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/stripe.py"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/nomba.py"))).toBe(false);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/paystack.py"))).toBe(false);

      // Theme: Rose
      const config = fs.readFileSync(path.join(projectDir, "backend/app/core/config.py"), "utf-8");
      expect(config).toContain('primary_color: str = "#f43f5e"');
    });

    it("scaffolds correctly with no email + Paystack + Cyan", () => {
      const projectName = "test-combo-3";
      execSync(`node ${CLI_PATH} ${projectName} --email none --payment paystack --theme cyan --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);

      // Email: None
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/resend.py"))).toBe(false);
      expect(fs.existsSync(path.join(projectDir, "backend/app/emails/providers/brevo.py"))).toBe(false);

      // Payment: Paystack
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/paystack.py"))).toBe(true);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/nomba.py"))).toBe(false);
      expect(fs.existsSync(path.join(projectDir, "backend/app/billing/providers/stripe.py"))).toBe(false);

      // Theme: Cyan
      const config = fs.readFileSync(path.join(projectDir, "backend/app/core/config.py"), "utf-8");
      expect(config).toContain('primary_color: str = "#06b6d4"');
    });
  });

  describe("User Routes", () => {
    it("user routes use /me prefix", () => {
      const projectName = "test-user-routes";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const routes = fs.readFileSync(path.join(projectDir, "backend/app/users/routes.py"), "utf-8");

      // Should have /me prefix
      expect(routes).toContain('prefix="/me"');
      // Should have the correct tag
      expect(routes).toContain('tags=["User"]');
    });

    it("user route tests use correct /me prefix", () => {
      const projectName = "test-user-route-tests";
      execSync(`node ${CLI_PATH} ${projectName} --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const testRoutes = fs.readFileSync(path.join(projectDir, "backend/tests/unit/users/test_routes.py"), "utf-8");

      // Test file docstrings should reference /me
      expect(testRoutes).toContain("/me endpoint");
      expect(testRoutes).toContain("/me/dashboard");
      expect(testRoutes).toContain("/me/account");
    });
  });

  describe("Provider-Specific Route Tests", () => {
    it("Nomba routes test file tests Nomba webhook", () => {
      const projectName = "test-nomba-routes";
      execSync(`node ${CLI_PATH} ${projectName} --payment nomba --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const routesTest = fs.readFileSync(path.join(projectDir, "backend/tests/unit/billing/test_routes.py"), "utf-8");

      // Should have webhook tests
      expect(routesTest).toContain("TestPaymentWebhook");
      expect(routesTest).toContain("verify_webhook_signature");
    });

    it("Stripe routes test file tests Stripe webhook", () => {
      const projectName = "test-stripe-routes";
      execSync(`node ${CLI_PATH} ${projectName} --payment stripe --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const routesTest = fs.readFileSync(path.join(projectDir, "backend/tests/unit/billing/test_routes.py"), "utf-8");

      // Should have webhook tests
      expect(routesTest).toContain("TestPaymentWebhook");
    });

    it("Paystack routes test file tests Paystack webhook", () => {
      const projectName = "test-paystack-routes";
      execSync(`node ${CLI_PATH} ${projectName} --payment paystack --no-install --no-git`, {
        cwd: TEST_DIR,
        stdio: "ignore",
      });

      const projectDir = path.join(TEST_DIR, projectName);
      const routesTest = fs.readFileSync(path.join(projectDir, "backend/tests/unit/billing/test_routes.py"), "utf-8");

      // Should have webhook tests
      expect(routesTest).toContain("TestPaymentWebhook");
    });
  });
});
