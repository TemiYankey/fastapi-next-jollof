#!/usr/bin/env node

import * as p from "@clack/prompts";
import chalk from "chalk";
import gradient from "gradient-string";
import { Command } from "commander";
import fs from "fs-extra";
import path from "path";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

import {
  COLOR_THEMES,
  PAYMENT_PROVIDERS,
  EMAIL_PROVIDERS,
  PROJECT_TYPES,
} from "./lib/constants.js";
import type { ProjectConfig, TemplateContext } from "./lib/types.js";
import { validateProjectName, validatePort, validateAppName } from "./lib/validation.js";
import {
  createTemplateContext,
  renderTemplateString,
  projectNameToDisplayName,
  generateLogoSvg,
  generateFaviconSvg,
  updateTailwindConfig,
  getTemplateFiles,
  getFilesToRemove,
} from "./lib/templates.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Beautiful gradients
const jollofGradient = gradient(["#ff6b35", "#f7c59f", "#ff6b35"]);

function renderTemplate(templatePath: string, context: TemplateContext): string {
  const templateContent = fs.readFileSync(templatePath, "utf-8");
  return renderTemplateString(templateContent, context);
}

// Add preview property to color themes for display
const COLOR_THEMES_WITH_PREVIEW = Object.fromEntries(
  Object.entries(COLOR_THEMES).map(([key, theme]) => [
    key,
    { ...theme, preview: chalk.hex(theme.hex)("████") },
  ])
) as Record<keyof typeof COLOR_THEMES, (typeof COLOR_THEMES)[keyof typeof COLOR_THEMES] & { preview: string }>;

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
            ? projectNameToDisplayName(results.projectName)
            : "My Awesome App",
          initialValue: results.projectName
            ? projectNameToDisplayName(results.projectName)
            : "",
          validate: validateAppName,
        }),

      projectType: () =>
        p.select({
          message: "What would you like to scaffold?",
          options: Object.entries(PROJECT_TYPES).map(([key, type]) => ({
            value: key,
            label: type.name,
            hint: type.description,
          })),
          initialValue: "fullstack",
        }),

      colorTheme: ({ results }) =>
        results.projectType === "backend"
          ? Promise.resolve("indigo")
          : p.select({
              message: "Pick your brand color",
              options: Object.entries(COLOR_THEMES_WITH_PREVIEW).map(([key, theme]) => ({
                value: key,
                label: `${theme.preview} ${theme.name}`,
                hint: theme.description,
              })),
              initialValue: "indigo",
            }),

      paymentProvider: ({ results }) =>
        results.projectType === "frontend"
          ? Promise.resolve("nomba")
          : p.select({
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

      emailProvider: ({ results }) =>
        results.projectType === "frontend"
          ? Promise.resolve("none")
          : p.select({
              message: "Choose your email provider",
              options: Object.entries(EMAIL_PROVIDERS).map(([key, provider]) => ({
                value: key,
                label: provider.name,
                hint: provider.description,
              })),
              initialValue: "resend",
            }),

      frontendPort: ({ results }) =>
        results.projectType === "backend"
          ? Promise.resolve("3000")
          : p.text({
              message: "Frontend port?",
              placeholder: "3000",
              initialValue: "3000",
              validate: validatePort,
            }),

      backendPort: ({ results }) =>
        results.projectType === "frontend"
          ? Promise.resolve("8000")
          : p.text({
              message: "Backend port?",
              placeholder: "8000",
              initialValue: "8000",
              validate: validatePort,
            }),

      includeDocker: ({ results }) =>
        results.projectType === "frontend"
          ? Promise.resolve(false)
          : p.confirm({
              message: "Include Docker setup? (docker-compose, Dockerfiles)",
              initialValue: true,
            }),

      includeExamples: ({ results }) =>
        results.projectType === "backend"
          ? Promise.resolve(false)
          : p.confirm({
              message: "Include example pages & components?",
              initialValue: true,
            }),

      initGit: () =>
        p.confirm({
          message: "Initialize a git repository?",
          initialValue: true,
        }),

      installDeps: ({ results }) =>
        results.projectType === "backend"
          ? Promise.resolve(false)
          : p.confirm({
              message: "Install frontend dependencies now?",
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

  const includeBackend = config.projectType !== "frontend";
  const includeFrontend = config.projectType !== "backend";

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

  // Step 1: Copy base template (selective based on project type)
  spinner.start(chalk.cyan("📁 Copying project files..."));

  if (!fs.existsSync(templateDir)) {
    spinner.stop(chalk.red("Template directory not found"));
    p.log.error(`Template not found at ${templateDir}`);
    process.exit(1);
  }

  // Create target directory
  fs.ensureDirSync(targetDir);

  // Copy based on project type
  if (includeBackend) {
    fs.copySync(path.join(templateDir, "backend"), path.join(targetDir, "backend"));
  }
  if (includeFrontend) {
    fs.copySync(path.join(templateDir, "frontend"), path.join(targetDir, "frontend"));
  }

  // Copy root files (.gitignore will be handled by template)
  spinner.stop(chalk.green("📁 Project files copied"));

  // Step 2: Apply Handlebars templates
  spinner.start(chalk.cyan("⚙️  Applying configuration..."));

  // Helper to apply template
  const applyTemplate = (templateName: string, outputPath: string) => {
    const templatePath = path.join(hbsTemplatesDir, templateName);
    const fullOutputPath = path.join(targetDir, outputPath);

    // Check if the parent directory exists (for project type filtering)
    const parentDir = path.dirname(fullOutputPath);
    if (!fs.existsSync(parentDir)) {
      return; // Skip if parent doesn't exist (e.g., frontend templates when backend-only)
    }

    if (fs.existsSync(templatePath)) {
      const content = renderTemplate(templatePath, ctx);
      fs.writeFileSync(fullOutputPath, content);
    }
  };

  // Apply all templates (getTemplateFiles now filters by project type)
  const templateFiles = getTemplateFiles(config.includeDocker, config.projectType);
  for (const [templateName, outputPath] of templateFiles) {
    applyTemplate(templateName, outputPath);
  }

  // Remove unused provider files (only for backend)
  if (includeBackend) {
    const filesToRemove = getFilesToRemove(config.paymentProvider, config.emailProvider);

    const paymentProvidersDir = path.join(targetDir, "backend", "app", "billing", "providers");
    for (const filename of filesToRemove.paymentFiles) {
      const filePath = path.join(paymentProvidersDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }

    const emailProvidersDir = path.join(targetDir, "backend", "app", "emails", "providers");
    for (const filename of filesToRemove.emailFiles) {
      const filePath = path.join(emailProvidersDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }

    const billingTestsDir = path.join(targetDir, "backend", "tests", "unit", "billing");
    for (const filename of filesToRemove.paymentTestFiles) {
      const filePath = path.join(billingTestsDir, filename);
      if (fs.existsSync(filePath)) fs.removeSync(filePath);
    }
  }

  // Update tailwind.config.ts with selected color (only for frontend)
  if (includeFrontend) {
    const tailwindPath = path.join(targetDir, "frontend", "tailwind.config.ts");
    if (fs.existsSync(tailwindPath)) {
      let content = fs.readFileSync(tailwindPath, "utf-8");
      content = updateTailwindConfig(content, ctx.primaryColor);
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

  // Step 5: Install frontend dependencies only (when frontend is included)
  if (config.installDeps && includeFrontend) {
    console.log();
    p.log.step(chalk.dim("Installing frontend dependencies..."));
    console.log();

    spinner.start(chalk.cyan("📦 Installing frontend dependencies..."));
    try {
      execSync("npm install", { cwd: path.join(targetDir, "frontend"), stdio: "ignore" });
      spinner.stop(chalk.green("📦 Frontend dependencies installed"));
    } catch {
      spinner.stop(chalk.red("📦 Frontend install failed"));
      p.log.warn("Run 'npm install' manually in frontend/");
    }
  }

  return targetDir;
}

function printNextSteps(targetDir: string, config: ProjectConfig) {
  const relativePath = path.relative(process.cwd(), targetDir);
  const includeBackend = config.projectType !== "frontend";
  const includeFrontend = config.projectType !== "backend";

  console.log();
  console.log(jollofGradient("  ✨ Your Jollof app is ready! ✨"));
  console.log();

  // Jollof orange theme colors
  const o = chalk.hex("#ff6b35"); // orange border
  const c = chalk.hex("#f7c59f"); // command color
  const t = chalk.hex("#ffb088"); // text color
  const h = chalk.hex("#ff8c42"); // highlight

  // Box width = 60 inner chars
  const W = 60;
  const bar = "─".repeat(W);
  const spc = " ".repeat(W);
  const pad = (s: string, len: number) => s + " ".repeat(Math.max(0, W - len));

  console.log(o(`  ┌${bar}┐`));
  console.log(o("  │") + pad(chalk.bold.white(" 🚀 Next Steps"), 15) + o("│"));
  console.log(o(`  ├${bar}┤`));
  console.log(o("  │") + spc + o("│"));

  let stepNum = 1;

  // Step 1: Navigate
  console.log(o("  │") + pad(t(` ${stepNum}. Navigate to your project:`), 30) + o("│"));
  console.log(o("  │") + pad(c(`    cd ${relativePath}`), 7 + relativePath.length) + o("│"));
  console.log(o("  │") + spc + o("│"));
  stepNum++;

  // Step 2: Environment variables
  console.log(o("  │") + pad(t(` ${stepNum}. Set up environment variables:`), 34) + o("│"));
  if (includeFrontend) {
    console.log(o("  │") + pad(`    ${c("cp")} frontend/.env.example frontend/.env.local`, 49) + o("│"));
  }
  if (includeBackend) {
    console.log(o("  │") + pad(`    ${c("cp")} backend/.env.example backend/.env`, 41) + o("│"));
  }
  console.log(o("  │") + spc + o("│"));
  stepNum++;

  // Step 3: Backend setup (only if backend included)
  if (includeBackend) {
    console.log(o("  │") + pad(t(` ${stepNum}. Set up backend:`), 20) + o("│"));
    console.log(o("  │") + pad(`    ${c("cd")} backend`, 15) + o("│"));
    console.log(o("  │") + pad(`    ${c("python3 -m venv venv")}`, 25) + o("│"));
    console.log(o("  │") + pad(`    ${c("source venv/bin/activate")}`, 29) + o("│"));
    console.log(o("  │") + pad(`    ${c("pip install -r requirements.txt")}`, 36) + o("│"));
    console.log(o("  │") + spc + o("│"));
    stepNum++;
  }

  // Docker step (only for fullstack or backend with docker)
  if (config.includeDocker && includeBackend) {
    console.log(o("  │") + pad(t(` ${stepNum}. Or use Docker:`), 19) + o("│"));
    console.log(o("  │") + pad(`    ${c("docker compose up -d")}`, 25) + o("│"));
    console.log(o("  │") + spc + o("│"));
    stepNum++;
  }

  // Run locally step
  console.log(o("  │") + pad(t(` ${stepNum}. Run locally:`), 17) + o("│"));
  if (includeFrontend && includeBackend) {
    console.log(o("  │") + pad(`    ${h("Terminal 1:")} cd frontend && ${c("make dev")}`, 40) + o("│"));
    console.log(o("  │") + pad(`    ${h("Terminal 2:")} cd backend && ${c("make dev")}`, 39) + o("│"));
  } else if (includeFrontend) {
    console.log(o("  │") + pad(`    cd frontend && ${c("make dev")}`, 27) + o("│"));
  } else if (includeBackend) {
    console.log(o("  │") + pad(`    cd backend && ${c("make dev")}`, 26) + o("│"));
  }
  console.log(o("  │") + spc + o("│"));
  console.log(o(`  └${bar}┘`));

  console.log();

  // Configuration summary with jollof styling
  console.log(chalk.bold.hex("#ff6b35")("  📋 Configuration"));
  console.log(chalk.hex("#ff8c42")("  ─".repeat(20)));
  console.log(chalk.hex("#ffb088")("  App:      ") + chalk.white(config.appName));
  console.log(chalk.hex("#ffb088")("  Type:     ") + chalk.white(PROJECT_TYPES[config.projectType].name));
  if (includeFrontend) {
    console.log(
      chalk.hex("#ffb088")("  Color:    ") +
        COLOR_THEMES_WITH_PREVIEW[config.colorTheme].preview +
        " " +
        chalk.white(COLOR_THEMES_WITH_PREVIEW[config.colorTheme].name)
    );
  }
  if (includeBackend) {
    console.log(chalk.hex("#ffb088")("  Payment:  ") + chalk.white(PAYMENT_PROVIDERS[config.paymentProvider].name));
    console.log(chalk.hex("#ffb088")("  Email:    ") + chalk.white(EMAIL_PROVIDERS[config.emailProvider].name));
  }
  if (includeFrontend) {
    console.log(chalk.hex("#ffb088")("  Frontend: ") + chalk.hex("#f7c59f")(`http://localhost:${config.frontendPort}`));
  }
  if (includeBackend) {
    console.log(chalk.hex("#ffb088")("  Backend:  ") + chalk.hex("#f7c59f")(`http://localhost:${config.backendPort}`));
  }
  if (includeFrontend) {
    console.log(chalk.hex("#ffb088")("  Examples: ") + chalk.white(config.includeExamples ? "Yes" : "No"));
  }
  console.log();

  if (includeBackend && config.paymentProvider !== "nomba") {
    p.log.warn(
      `${PAYMENT_PROVIDERS[config.paymentProvider].name} is coming soon. Using Nomba as default.`
    );
  }

  console.log(chalk.hex("#ffb088")("  📚 Docs: ") + chalk.hex("#f7c59f")("https://github.com/sir-temi/fastapi-next-jollof"));
  console.log();
}

async function main() {
  const program = new Command()
    .name("create-jollof-app")
    .description("Create a full-stack FastAPI + Next.js application")
    .version("1.0.0")
    .argument("[project-name]", "Name of the project")
    .option("--type <type>", "Project type (fullstack, backend, frontend)")
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
    const projectType = (options.type as keyof typeof PROJECT_TYPES) || "fullstack";
    const includeBackend = projectType !== "frontend";
    const includeFrontend = projectType !== "backend";

    const quickConfig: ProjectConfig = {
      projectName: args[0],
      appName: projectNameToDisplayName(args[0]),
      projectType,
      colorTheme: (options.theme as keyof typeof COLOR_THEMES) || "indigo",
      paymentProvider: (options.payment as keyof typeof PAYMENT_PROVIDERS) || "nomba",
      emailProvider: (options.email as keyof typeof EMAIL_PROVIDERS) || "resend",
      frontendPort: parseInt(options.frontendPort, 10) || 3000,
      backendPort: parseInt(options.backendPort, 10) || 8000,
      includeDocker: includeBackend, // Only include Docker if backend is included
      includeExamples: includeFrontend, // Only include examples if frontend is included
      initGit: options.git !== false,
      installDeps: options.install !== false && includeFrontend,
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
