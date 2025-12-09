#!/usr/bin/env node

import * as p from "@clack/prompts";
import chalk from "chalk";
import gradient from "gradient-string";
import { Command } from "commander";
import fs from "fs-extra";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";
import Handlebars from "handlebars";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Beautiful gradients
const jollofGradient = gradient(["#ff6b35", "#f7c59f", "#ff6b35"]);
const successGradient = gradient(["#00d4aa", "#7c3aed"]);

// Tailwind color themes
const COLOR_THEMES = {
  indigo: {
    name: "Indigo",
    description: "Professional & trustworthy",
    primary: "indigo",
    preview: chalk.hex("#6366f1")("████"),
  },
  violet: {
    name: "Violet",
    description: "Creative & modern",
    primary: "violet",
    preview: chalk.hex("#8b5cf6")("████"),
  },
  blue: {
    name: "Blue",
    description: "Classic & reliable",
    primary: "blue",
    preview: chalk.hex("#3b82f6")("████"),
  },
  emerald: {
    name: "Emerald",
    description: "Fresh & growth-focused",
    primary: "emerald",
    preview: chalk.hex("#10b981")("████"),
  },
  rose: {
    name: "Rose",
    description: "Bold & energetic",
    primary: "rose",
    preview: chalk.hex("#f43f5e")("████"),
  },
  amber: {
    name: "Amber",
    description: "Warm & inviting",
    primary: "amber",
    preview: chalk.hex("#f59e0b")("████"),
  },
  cyan: {
    name: "Cyan",
    description: "Tech & futuristic",
    primary: "cyan",
    preview: chalk.hex("#06b6d4")("████"),
  },
  orange: {
    name: "Orange (Jollof)",
    description: "Vibrant & appetizing",
    primary: "orange",
    preview: chalk.hex("#f97316")("████"),
  },
} as const;

// Payment providers
const PAYMENT_PROVIDERS = {
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
const EMAIL_PROVIDERS = {
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

interface ProjectConfig {
  projectName: string;
  appName: string;
  colorTheme: keyof typeof COLOR_THEMES;
  paymentProvider: keyof typeof PAYMENT_PROVIDERS;
  emailProvider: keyof typeof EMAIL_PROVIDERS;
  frontendPort: number;
  backendPort: number;
  includeExamples: boolean;
  initGit: boolean;
  installDeps: boolean;
}

// Template context for Handlebars
interface TemplateContext {
  appName: string;
  dbName: string;
  primaryColor: string;
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

function createTemplateContext(config: ProjectConfig): TemplateContext {
  return {
    appName: config.appName,
    dbName: config.projectName.replace(/-/g, "_"),
    primaryColor: COLOR_THEMES[config.colorTheme].primary,
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

function renderTemplate(templatePath: string, context: TemplateContext): string {
  const templateContent = fs.readFileSync(templatePath, "utf-8");
  const template = Handlebars.compile(templateContent);
  return template(context);
}

// Color hex values for SVG generation
const COLOR_HEX: Record<string, string> = {
  indigo: "#6366f1",
  violet: "#8b5cf6",
  blue: "#3b82f6",
  emerald: "#10b981",
  rose: "#f43f5e",
  amber: "#f59e0b",
  cyan: "#06b6d4",
  orange: "#f97316",
};

function generateLogoSvg(appName: string, color: string): string {
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

function generateFaviconSvg(appName: string, color: string): string {
  const initial = appName[0].toUpperCase();
  const hexColor = COLOR_HEX[color] || COLOR_HEX.indigo;

  return `<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="32" height="32" rx="6" fill="${hexColor}"/>
  <text x="16" y="22" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="700" fill="white" text-anchor="middle">${initial}</text>
</svg>`;
}

function printBanner() {
  console.clear();
  console.log();
  console.log(
    jollofGradient(`
       ██╗ ██████╗ ██╗     ██╗      ██████╗ ███████╗
       ██║██╔═══██╗██║     ██║     ██╔═══██╗██╔════╝
       ██║██║   ██║██║     ██║     ██║   ██║█████╗
  ██   ██║██║   ██║██║     ██║     ██║   ██║██╔══╝
  ╚█████╔╝╚██████╔╝███████╗███████╗╚██████╔╝██║
   ╚════╝  ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═╝
`)
  );
  console.log();
  console.log(
    chalk.dim("  FastAPI + Next.js • Supabase Auth • Payments • Ready to Ship")
  );
  console.log();
}

function validateProjectName(name: string): string | undefined {
  if (!name || name.trim().length === 0) {
    return "Project name is required";
  }
  if (!/^[a-z0-9-]+$/.test(name)) {
    return "Project name can only contain lowercase letters, numbers, and hyphens";
  }
  if (name.startsWith("-") || name.endsWith("-")) {
    return "Project name cannot start or end with a hyphen";
  }
  return undefined;
}

async function getProjectConfig(): Promise<ProjectConfig | null> {
  p.intro(chalk.bgHex("#ff6b35").white(" Let's cook up your app "));

  const config = await p.group(
    {
      projectName: () =>
        p.text({
          message: "What's your project name?",
          placeholder: "my-awesome-app",
          validate: validateProjectName,
        }),

      appName: ({ results }) =>
        p.text({
          message: "What's your app display name?",
          placeholder: results.projectName
            ? results.projectName
                .split("-")
                .map((w: string) => w.charAt(0).toUpperCase() + w.slice(1))
                .join(" ")
            : "My Awesome App",
          initialValue: results.projectName
            ? results.projectName
                .split("-")
                .map((w: string) => w.charAt(0).toUpperCase() + w.slice(1))
                .join(" ")
            : "",
          validate: (value) => {
            if (!value || value.trim().length === 0) {
              return "App name is required";
            }
            return undefined;
          },
        }),

      colorTheme: () =>
        p.select({
          message: "Pick your brand color",
          options: Object.entries(COLOR_THEMES).map(([key, theme]) => ({
            value: key,
            label: `${theme.preview} ${theme.name}`,
            hint: theme.description,
          })),
          initialValue: "indigo",
        }),

      paymentProvider: () =>
        p.select({
          message: "Choose your payment provider",
          options: Object.entries(PAYMENT_PROVIDERS).map(([key, provider]) => ({
            value: key,
            label: provider.comingSoon
              ? `${provider.name} ${chalk.yellow("(coming soon)")}`
              : provider.name,
            hint: `${provider.description} • ${provider.regions.join(", ")}`,
          })),
          initialValue: "nomba",
        }),

      emailProvider: () =>
        p.select({
          message: "Choose your email provider",
          options: Object.entries(EMAIL_PROVIDERS).map(([key, provider]) => ({
            value: key,
            label: provider.name,
            hint: provider.description,
          })),
          initialValue: "resend",
        }),

      frontendPort: () =>
        p.text({
          message: "Frontend port?",
          placeholder: "3000",
          initialValue: "3000",
          validate: (value) => {
            const port = parseInt(value, 10);
            if (isNaN(port) || port < 1024 || port > 65535) {
              return "Port must be between 1024 and 65535";
            }
            return undefined;
          },
        }),

      backendPort: () =>
        p.text({
          message: "Backend port?",
          placeholder: "8000",
          initialValue: "8000",
          validate: (value) => {
            const port = parseInt(value, 10);
            if (isNaN(port) || port < 1024 || port > 65535) {
              return "Port must be between 1024 and 65535";
            }
            return undefined;
          },
        }),

      includeExamples: () =>
        p.confirm({
          message: "Include example pages & components?",
          initialValue: true,
        }),

      initGit: () =>
        p.confirm({
          message: "Initialize a git repository?",
          initialValue: true,
        }),

      installDeps: () =>
        p.confirm({
          message: "Install dependencies now?",
          initialValue: true,
        }),
    },
    {
      onCancel: () => {
        p.cancel("Operation cancelled.");
        process.exit(0);
      },
    }
  );

  return {
    ...config,
    frontendPort: parseInt(config.frontendPort as unknown as string, 10),
    backendPort: parseInt(config.backendPort as unknown as string, 10),
  } as ProjectConfig;
}

async function scaffoldProject(config: ProjectConfig) {
  const targetDir = path.resolve(process.cwd(), config.projectName);
  const templateDir = path.resolve(__dirname, "..", "template");
  const hbsTemplatesDir = path.resolve(__dirname, "..", "templates");

  // Check if directory exists
  if (fs.existsSync(targetDir)) {
    const overwrite = await p.confirm({
      message: `Directory ${chalk.cyan(config.projectName)} already exists. Overwrite?`,
      initialValue: false,
    });

    if (!overwrite || p.isCancel(overwrite)) {
      p.cancel("Operation cancelled.");
      process.exit(0);
    }

    fs.removeSync(targetDir);
  }

  const spinner = p.spinner();
  const ctx = createTemplateContext(config);

  console.log();
  p.log.step(chalk.dim("Setting up your project..."));
  console.log();

  // Step 1: Copy base template
  spinner.start(chalk.cyan("📁 Copying project files..."));

  if (!fs.existsSync(templateDir)) {
    spinner.stop(chalk.red("Template directory not found"));
    p.log.error(`Template not found at ${templateDir}`);
    process.exit(1);
  }

  fs.copySync(templateDir, targetDir);
  spinner.stop(chalk.green("📁 Project files copied"));

  // Step 2: Apply Handlebars templates
  spinner.start(chalk.cyan("⚙️  Applying configuration..."));

  // Helper to apply template
  const applyTemplate = (templateName: string, outputPath: string) => {
    const templatePath = path.join(hbsTemplatesDir, templateName);
    if (fs.existsSync(templatePath)) {
      const content = renderTemplate(templatePath, ctx);
      fs.writeFileSync(path.join(targetDir, outputPath), content);
    }
  };

  // Apply all templates
  applyTemplate("backend.env.hbs", "backend/.env.example");
  applyTemplate("backend.env.test.hbs", "backend/.env.test");
  applyTemplate("frontend.env.hbs", "frontend/.env.example");
  applyTemplate("requirements.txt.hbs", "backend/requirements.txt");
  applyTemplate("config.py.hbs", "backend/app/core/config.py");
  applyTemplate("billing-providers-init.py.hbs", "backend/app/billing/providers/__init__.py");
  applyTemplate("billing-enums.py.hbs", "backend/app/billing/enums.py");
  applyTemplate("billing-models.py.hbs", "backend/app/billing/models.py");
  applyTemplate("billing-routes.py.hbs", "backend/app/billing/routes.py");
  applyTemplate("email-providers-init.py.hbs", "backend/app/emails/providers/__init__.py");
  applyTemplate("email-enums.py.hbs", "backend/app/emails/enums.py");
  applyTemplate("email-service.py.hbs", "backend/app/emails/service.py");
  applyTemplate("backend-makefile.hbs", "backend/Makefile");
  applyTemplate("frontend-makefile.hbs", "frontend/Makefile");
  applyTemplate("test-email-providers.py.hbs", "backend/tests/unit/emails/test_providers.py");
  applyTemplate("test-email-factories.py.hbs", "backend/tests/unit/emails/factories.py");
  applyTemplate("docker-compose.yml.hbs", "docker-compose.yml");
  applyTemplate("backend-dockerfile.hbs", "backend/Dockerfile");
  applyTemplate("frontend-dockerfile.hbs", "frontend/Dockerfile");
  applyTemplate("backend-dockerignore.hbs", "backend/.dockerignore");
  applyTemplate("frontend-dockerignore.hbs", "frontend/.dockerignore");

  // Remove unused payment provider files
  const paymentProvidersDir = path.join(targetDir, "backend", "app", "billing", "providers");
  const paymentFiles: Record<string, string> = {
    nomba: "nomba.py",
    stripe: "stripe.py",
    paystack: "paystack.py",
  };
  for (const [provider, filename] of Object.entries(paymentFiles)) {
    if (provider !== config.paymentProvider) {
      const filePath = path.join(paymentProvidersDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }
  }

  // Remove unused email provider files
  const emailProvidersDir = path.join(targetDir, "backend", "app", "emails", "providers");
  const emailFiles: Record<string, string> = {
    resend: "resend.py",
    brevo: "brevo.py",
  };
  for (const [provider, filename] of Object.entries(emailFiles)) {
    if (provider !== config.emailProvider && config.emailProvider !== "none") {
      const filePath = path.join(emailProvidersDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }
  }
  if (config.emailProvider === "none") {
    for (const filename of Object.values(emailFiles)) {
      const filePath = path.join(emailProvidersDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }
  }

  // Remove unused payment provider tests
  const billingTestsDir = path.join(targetDir, "backend", "tests", "unit", "billing");
  const paymentTestFiles: Record<string, string> = {
    nomba: "test_nomba_provider.py",
    stripe: "test_stripe_provider.py",
    paystack: "test_paystack_provider.py",
  };
  for (const [provider, filename] of Object.entries(paymentTestFiles)) {
    if (provider !== config.paymentProvider) {
      const filePath = path.join(billingTestsDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }
  }

  // Update tailwind.config.ts with selected color
  const tailwindPath = path.join(targetDir, "frontend", "tailwind.config.ts");
  if (fs.existsSync(tailwindPath)) {
    let content = fs.readFileSync(tailwindPath, "utf-8");
    content = content.replace(/primary:\s*colors\.\w+/g, `primary: colors.${ctx.primaryColor}`);
    fs.writeFileSync(tailwindPath, content);
  }

  // Update frontend package.json name
  const pkgPath = path.join(targetDir, "frontend", "package.json");
  if (fs.existsSync(pkgPath)) {
    const pkg = fs.readJsonSync(pkgPath);
    pkg.name = config.projectName;
    fs.writeJsonSync(pkgPath, pkg, { spaces: 2 });
  }

  // Generate logo and favicon SVGs
  const logoSvg = generateLogoSvg(config.appName, ctx.primaryColor);
  const faviconSvg = generateFaviconSvg(config.appName, ctx.primaryColor);

  // Write logo to frontend public folder
  const publicDir = path.join(targetDir, "frontend", "public");
  fs.ensureDirSync(publicDir);
  fs.writeFileSync(path.join(publicDir, "logo.svg"), logoSvg);
  fs.writeFileSync(path.join(publicDir, "favicon.svg"), faviconSvg);

  // Remove examples if not wanted
  if (!config.includeExamples) {
    const examplesDir = path.join(targetDir, "frontend", "app", "examples");
    if (fs.existsSync(examplesDir)) fs.removeSync(examplesDir);
  }

  spinner.stop(chalk.green("⚙️  Configuration applied"));

  // Step 3: Clean up unused providers
  spinner.start(chalk.cyan("🧹 Cleaning up unused files..."));
  await new Promise((resolve) => setTimeout(resolve, 300)); // Small delay for visual feedback
  spinner.stop(chalk.green("🧹 Project cleaned"));

  // Step 4: Initialize git
  if (config.initGit) {
    spinner.start(chalk.cyan("📦 Initializing git repository..."));
    try {
      execSync("git init", { cwd: targetDir, stdio: "ignore" });
      execSync("git add -A", { cwd: targetDir, stdio: "ignore" });
      execSync('git commit -m "Initial commit from create-jollof-app"', {
        cwd: targetDir,
        stdio: "ignore",
      });
      spinner.stop(chalk.green("📦 Git repository initialized"));
    } catch {
      spinner.stop(chalk.yellow("📦 Git initialization skipped"));
    }
  }

  // Step 5: Install dependencies
  if (config.installDeps) {
    console.log();
    p.log.step(chalk.dim("Installing dependencies (this may take a minute)..."));
    console.log();

    // Frontend
    spinner.start(chalk.cyan("📦 Installing frontend dependencies..."));
    try {
      execSync("npm install", { cwd: path.join(targetDir, "frontend"), stdio: "ignore" });
      spinner.stop(chalk.green("📦 Frontend dependencies installed"));
    } catch {
      spinner.stop(chalk.red("📦 Frontend install failed"));
      p.log.warn("Run 'npm install' manually in frontend/");
    }

    // Backend venv
    spinner.start(chalk.cyan("🐍 Creating backend virtual environment..."));
    try {
      execSync("python3 -m venv venv", { cwd: path.join(targetDir, "backend"), stdio: "ignore" });
      spinner.stop(chalk.green("🐍 Backend virtual environment created"));
    } catch {
      spinner.stop(chalk.red("🐍 Failed to create backend virtual environment"));
      p.log.warn("Run 'python3 -m venv venv' manually in backend/");
    }

    // Backend pip install
    spinner.start(chalk.cyan("🐍 Installing backend dependencies..."));
    try {
      const pip = process.platform === "win32" ? ".\\venv\\Scripts\\pip" : "./venv/bin/pip";
      execSync(`${pip} install -r requirements.txt`, {
        cwd: path.join(targetDir, "backend"),
        stdio: "ignore",
      });
      spinner.stop(chalk.green("🐍 Backend dependencies installed"));
    } catch {
      spinner.stop(chalk.red("🐍 Backend dependencies installation failed"));
      p.log.warn("Run './venv/bin/pip install -r requirements.txt' manually in backend/");
    }
  }

  return targetDir;
}

function printNextSteps(targetDir: string, config: ProjectConfig) {
  const relativePath = path.relative(process.cwd(), targetDir);

  console.log();
  console.log(successGradient("  ✨ Your Jollof app is ready! ✨"));
  console.log();

  // Modern styled next steps box
  const boxWidth = 58;
  const border = chalk.hex("#6366f1");
  const title = chalk.bold.white;
  const cmd = chalk.hex("#22d3ee");
  const comment = chalk.hex("#94a3b8");
  const highlight = chalk.hex("#f472b6");

  console.log(border("  ┌" + "─".repeat(boxWidth) + "┐"));
  console.log(border("  │") + title(" 🚀 Next Steps".padEnd(boxWidth)) + border("│"));
  console.log(border("  ├" + "─".repeat(boxWidth) + "┤"));
  console.log(border("  │") + " ".repeat(boxWidth) + border("│"));
  console.log(border("  │") + comment("  1. Navigate to your project:".padEnd(boxWidth)) + border("│"));
  console.log(border("  │") + `     ${cmd("cd " + relativePath)}`.padEnd(boxWidth + 10) + border("│"));
  console.log(border("  │") + " ".repeat(boxWidth) + border("│"));
  console.log(border("  │") + comment("  2. Set up environment variables:".padEnd(boxWidth)) + border("│"));
  console.log(border("  │") + `     ${cmd("cp")} frontend/.env.example frontend/.env.local`.padEnd(boxWidth + 10) + border("│"));
  console.log(border("  │") + `     ${cmd("cp")} backend/.env.example backend/.env`.padEnd(boxWidth + 10) + border("│"));
  console.log(border("  │") + " ".repeat(boxWidth) + border("│"));
  console.log(border("  │") + comment("  3. Start with Docker (recommended):".padEnd(boxWidth)) + border("│"));
  console.log(border("  │") + `     ${cmd("docker compose up -d")}`.padEnd(boxWidth + 10) + border("│"));
  console.log(border("  │") + " ".repeat(boxWidth) + border("│"));
  console.log(border("  │") + comment("  4. Or run locally:".padEnd(boxWidth)) + border("│"));
  console.log(border("  │") + `     ${highlight("Terminal 1:")} ${cmd("cd")} frontend && ${cmd("make dev")}`.padEnd(boxWidth + 20) + border("│"));
  console.log(border("  │") + `     ${highlight("Terminal 2:")} ${cmd("cd")} backend`.padEnd(boxWidth + 20) + border("│"));
  console.log(border("  │") + `                  ${cmd("source venv/bin/activate")}`.padEnd(boxWidth + 10) + border("│"));
  console.log(border("  │") + `                  ${cmd("make dev")}`.padEnd(boxWidth + 10) + border("│"));
  console.log(border("  │") + " ".repeat(boxWidth) + border("│"));
  console.log(border("  └" + "─".repeat(boxWidth) + "┘"));

  console.log();

  // Configuration summary with modern styling
  console.log(chalk.bold.white("  📋 Configuration"));
  console.log(chalk.hex("#64748b")("  ─".repeat(20)));
  console.log(chalk.hex("#94a3b8")("  App:      ") + chalk.white(config.appName));
  console.log(
    chalk.hex("#94a3b8")("  Color:    ") +
      COLOR_THEMES[config.colorTheme].preview +
      " " +
      chalk.white(COLOR_THEMES[config.colorTheme].name)
  );
  console.log(chalk.hex("#94a3b8")("  Payment:  ") + chalk.white(PAYMENT_PROVIDERS[config.paymentProvider].name));
  console.log(chalk.hex("#94a3b8")("  Email:    ") + chalk.white(EMAIL_PROVIDERS[config.emailProvider].name));
  console.log(chalk.hex("#94a3b8")("  Frontend: ") + chalk.hex("#22d3ee")(`http://localhost:${config.frontendPort}`));
  console.log(chalk.hex("#94a3b8")("  Backend:  ") + chalk.hex("#22d3ee")(`http://localhost:${config.backendPort}`));
  console.log(chalk.hex("#94a3b8")("  Examples: ") + chalk.white(config.includeExamples ? "Yes" : "No"));
  console.log();

  if (config.paymentProvider !== "nomba") {
    p.log.warn(
      `${PAYMENT_PROVIDERS[config.paymentProvider].name} is coming soon. Using Nomba as default.`
    );
  }

  console.log(chalk.hex("#94a3b8")("  📚 Docs: ") + chalk.hex("#22d3ee")("https://github.com/sir-temi/fastapi-next-jollof"));
  console.log();
}

async function main() {
  const program = new Command()
    .name("create-jollof-app")
    .description("Create a full-stack FastAPI + Next.js application")
    .version("1.0.0")
    .argument("[project-name]", "Name of the project")
    .option("-t, --theme <theme>", "Color theme")
    .option("-p, --payment <provider>", "Payment provider (nomba, stripe, paystack)")
    .option("-e, --email <provider>", "Email provider (resend, brevo, none)")
    .option("--frontend-port <port>", "Frontend port (default: 3000)")
    .option("--backend-port <port>", "Backend port (default: 8000)")
    .option("--no-git", "Skip git initialization")
    .option("--no-install", "Skip dependency installation")
    .parse(process.argv);

  printBanner();

  const options = program.opts();
  const args = program.args;

  // Quick mode with arguments
  if (args[0]) {
    const quickConfig: ProjectConfig = {
      projectName: args[0],
      appName: args[0]
        .split("-")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" "),
      colorTheme: (options.theme as keyof typeof COLOR_THEMES) || "indigo",
      paymentProvider: (options.payment as keyof typeof PAYMENT_PROVIDERS) || "nomba",
      emailProvider: (options.email as keyof typeof EMAIL_PROVIDERS) || "resend",
      frontendPort: parseInt(options.frontendPort, 10) || 3000,
      backendPort: parseInt(options.backendPort, 10) || 8000,
      includeExamples: true,
      initGit: options.git !== false,
      installDeps: options.install !== false,
    };

    const targetDir = await scaffoldProject(quickConfig);
    printNextSteps(targetDir, quickConfig);
    p.outro(chalk.green("Happy cooking! 🍲"));
    return;
  }

  // Interactive mode
  const config = await getProjectConfig();
  if (!config) process.exit(1);

  const targetDir = await scaffoldProject(config);
  printNextSteps(targetDir, config);
  p.outro(chalk.green("Happy cooking! 🍲"));
}

main().catch((err) => {
  console.error(chalk.red("Error:"), err.message);
  process.exit(1);
});
