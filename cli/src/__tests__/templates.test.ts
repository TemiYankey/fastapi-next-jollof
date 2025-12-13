import { describe, it, expect } from "vitest";
import {
  createTemplateContext,
  renderTemplateString,
  projectNameToDisplayName,
  generateLogoSvg,
  generateFaviconSvg,
  updateTailwindConfig,
  getTemplateFiles,
  getFilesToRemove,
} from "../lib/templates.js";
import type { ProjectConfig } from "../lib/types.js";

const baseConfig: ProjectConfig = {
  projectName: "my-test-app",
  appName: "My Test App",
  colorTheme: "indigo",
  paymentProvider: "nomba",
  emailProvider: "resend",
  frontendPort: 3000,
  backendPort: 8000,
  includeDocker: true,
  includeExamples: true,
  initGit: true,
  installDeps: true,
};

describe("createTemplateContext", () => {
  it("creates context with correct app name", () => {
    const ctx = createTemplateContext(baseConfig);
    expect(ctx.appName).toBe("My Test App");
  });

  it("converts project name to db name (hyphens to underscores)", () => {
    const ctx = createTemplateContext(baseConfig);
    expect(ctx.dbName).toBe("my_test_app");
  });

  it("handles project name without hyphens", () => {
    const config = { ...baseConfig, projectName: "myapp" };
    const ctx = createTemplateContext(config);
    expect(ctx.dbName).toBe("myapp");
  });

  it("sets correct primary color name", () => {
    const ctx = createTemplateContext(baseConfig);
    expect(ctx.primaryColor).toBe("indigo");
  });

  it("sets correct primary color hex", () => {
    const ctx = createTemplateContext(baseConfig);
    expect(ctx.primaryColorHex).toBe("#6366f1");
  });

  it("sets different hex for different colors", () => {
    const roseConfig = { ...baseConfig, colorTheme: "rose" as const };
    const ctx = createTemplateContext(roseConfig);
    expect(ctx.primaryColor).toBe("rose");
    expect(ctx.primaryColorHex).toBe("#f43f5e");
  });

  it("sets correct ports", () => {
    const ctx = createTemplateContext(baseConfig);
    expect(ctx.frontendPort).toBe(3000);
    expect(ctx.backendPort).toBe(8000);
  });

  it("sets custom ports", () => {
    const config = { ...baseConfig, frontendPort: 4000, backendPort: 9000 };
    const ctx = createTemplateContext(config);
    expect(ctx.frontendPort).toBe(4000);
    expect(ctx.backendPort).toBe(9000);
  });

  describe("payment provider flags", () => {
    it("sets isNomba true for nomba", () => {
      const ctx = createTemplateContext(baseConfig);
      expect(ctx.isNomba).toBe(true);
      expect(ctx.isStripe).toBe(false);
      expect(ctx.isPaystack).toBe(false);
    });

    it("sets isStripe true for stripe", () => {
      const config = { ...baseConfig, paymentProvider: "stripe" as const };
      const ctx = createTemplateContext(config);
      expect(ctx.isNomba).toBe(false);
      expect(ctx.isStripe).toBe(true);
      expect(ctx.isPaystack).toBe(false);
    });

    it("sets isPaystack true for paystack", () => {
      const config = { ...baseConfig, paymentProvider: "paystack" as const };
      const ctx = createTemplateContext(config);
      expect(ctx.isNomba).toBe(false);
      expect(ctx.isStripe).toBe(false);
      expect(ctx.isPaystack).toBe(true);
    });
  });

  describe("email provider flags", () => {
    it("sets isResend true for resend", () => {
      const ctx = createTemplateContext(baseConfig);
      expect(ctx.isResend).toBe(true);
      expect(ctx.isBrevo).toBe(false);
      expect(ctx.noEmail).toBe(false);
    });

    it("sets isBrevo true for brevo", () => {
      const config = { ...baseConfig, emailProvider: "brevo" as const };
      const ctx = createTemplateContext(config);
      expect(ctx.isResend).toBe(false);
      expect(ctx.isBrevo).toBe(true);
      expect(ctx.noEmail).toBe(false);
    });

    it("sets noEmail true for none", () => {
      const config = { ...baseConfig, emailProvider: "none" as const };
      const ctx = createTemplateContext(config);
      expect(ctx.isResend).toBe(false);
      expect(ctx.isBrevo).toBe(false);
      expect(ctx.noEmail).toBe(true);
    });
  });

  describe("all color themes", () => {
    const themes = ["indigo", "violet", "blue", "emerald", "rose", "amber", "cyan", "orange"] as const;
    const expectedHex: Record<string, string> = {
      indigo: "#6366f1",
      violet: "#8b5cf6",
      blue: "#3b82f6",
      emerald: "#10b981",
      rose: "#f43f5e",
      amber: "#f59e0b",
      cyan: "#06b6d4",
      orange: "#f97316",
    };

    themes.forEach((theme) => {
      it(`handles ${theme} theme correctly`, () => {
        const config = { ...baseConfig, colorTheme: theme };
        const ctx = createTemplateContext(config);
        expect(ctx.primaryColor).toBe(theme);
        expect(ctx.primaryColorHex).toBe(expectedHex[theme]);
      });
    });
  });
});

describe("renderTemplateString", () => {
  const ctx = createTemplateContext(baseConfig);

  it("renders simple variable substitution", () => {
    const template = "Hello {{appName}}!";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("Hello My Test App!");
  });

  it("renders multiple variables", () => {
    const template = "{{appName}} running on ports {{frontendPort}} and {{backendPort}}";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("My Test App running on ports 3000 and 8000");
  });

  it("renders conditional blocks (true)", () => {
    const template = "{{#if isNomba}}Nomba enabled{{/if}}";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("Nomba enabled");
  });

  it("renders conditional blocks (false)", () => {
    const template = "{{#if isStripe}}Stripe enabled{{/if}}";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("");
  });

  it("renders else blocks", () => {
    const template = "{{#if isStripe}}Stripe{{else}}Not Stripe{{/if}}";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("Not Stripe");
  });

  it("renders unless blocks", () => {
    const template = "{{#unless isStripe}}Using Nomba{{/unless}}";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("Using Nomba");
  });

  it("renders hex color", () => {
    const template = 'color: "{{primaryColorHex}}"';
    const result = renderTemplateString(template, ctx);
    expect(result).toBe('color: "#6366f1"');
  });

  it("handles empty template", () => {
    const result = renderTemplateString("", ctx);
    expect(result).toBe("");
  });

  it("handles template with no variables", () => {
    const template = "Static content";
    const result = renderTemplateString(template, ctx);
    expect(result).toBe("Static content");
  });
});

describe("projectNameToDisplayName", () => {
  it("converts hyphenated name to title case", () => {
    expect(projectNameToDisplayName("my-awesome-app")).toBe("My Awesome App");
  });

  it("handles single word", () => {
    expect(projectNameToDisplayName("myapp")).toBe("Myapp");
  });

  it("handles multiple hyphens", () => {
    expect(projectNameToDisplayName("my-super-awesome-app")).toBe("My Super Awesome App");
  });

  it("handles numbers", () => {
    expect(projectNameToDisplayName("my-app-123")).toBe("My App 123");
  });

  it("handles empty string", () => {
    expect(projectNameToDisplayName("")).toBe("");
  });

  it("handles single character segments", () => {
    expect(projectNameToDisplayName("a-b-c")).toBe("A B C");
  });
});

describe("generateLogoSvg", () => {
  it("generates valid SVG with initials", () => {
    const svg = generateLogoSvg("My App", "indigo");
    expect(svg).toContain("<svg");
    expect(svg).toContain("</svg>");
    expect(svg).toContain(">MA<"); // Initials
  });

  it("uses correct hex color", () => {
    const svg = generateLogoSvg("My App", "indigo");
    expect(svg).toContain("#6366f1");
  });

  it("uses different hex for different colors", () => {
    const svg = generateLogoSvg("My App", "rose");
    expect(svg).toContain("#f43f5e");
  });

  it("limits initials to 2 characters", () => {
    const svg = generateLogoSvg("My Super Awesome App", "indigo");
    expect(svg).toContain(">MS<"); // Only first 2
  });

  it("handles single word app name", () => {
    const svg = generateLogoSvg("App", "indigo");
    expect(svg).toContain(">A<");
  });

  it("falls back to indigo for unknown color", () => {
    const svg = generateLogoSvg("My App", "unknown");
    expect(svg).toContain("#6366f1"); // indigo fallback
  });

  it("contains gradient definition", () => {
    const svg = generateLogoSvg("My App", "indigo");
    expect(svg).toContain("linearGradient");
    expect(svg).toContain("bgGradient");
  });

  it("has correct dimensions", () => {
    const svg = generateLogoSvg("My App", "indigo");
    expect(svg).toContain('width="512"');
    expect(svg).toContain('height="512"');
  });
});

describe("generateFaviconSvg", () => {
  it("generates valid SVG with single initial", () => {
    const svg = generateFaviconSvg("My App", "indigo");
    expect(svg).toContain("<svg");
    expect(svg).toContain("</svg>");
    expect(svg).toContain(">M<"); // Single initial
  });

  it("uses correct hex color", () => {
    const svg = generateFaviconSvg("My App", "indigo");
    expect(svg).toContain("#6366f1");
  });

  it("uses different hex for different colors", () => {
    const svg = generateFaviconSvg("My App", "emerald");
    expect(svg).toContain("#10b981");
  });

  it("has correct dimensions", () => {
    const svg = generateFaviconSvg("My App", "indigo");
    expect(svg).toContain('width="32"');
    expect(svg).toContain('height="32"');
  });

  it("falls back to indigo for unknown color", () => {
    const svg = generateFaviconSvg("My App", "unknown");
    expect(svg).toContain("#6366f1");
  });

  it("uppercases the initial", () => {
    const svg = generateFaviconSvg("myapp", "indigo");
    expect(svg).toContain(">M<");
  });
});

describe("updateTailwindConfig", () => {
  it("replaces primary color", () => {
    const content = "primary: colors.indigo";
    const result = updateTailwindConfig(content, "rose");
    expect(result).toBe("primary: colors.rose");
  });

  it("handles different spacing", () => {
    const content = "primary:  colors.blue";
    const result = updateTailwindConfig(content, "emerald");
    expect(result).toBe("primary: colors.emerald");
  });

  it("replaces multiple occurrences", () => {
    const content = "primary: colors.indigo\nprimary: colors.violet";
    const result = updateTailwindConfig(content, "cyan");
    expect(result).toBe("primary: colors.cyan\nprimary: colors.cyan");
  });

  it("preserves other content", () => {
    const content = `module.exports = {
  colors: {
    primary: colors.indigo,
    secondary: colors.gray
  }
}`;
    const result = updateTailwindConfig(content, "amber");
    expect(result).toContain("primary: colors.amber");
    expect(result).toContain("secondary: colors.gray");
  });

  it("handles content without primary color", () => {
    const content = "module.exports = {}";
    const result = updateTailwindConfig(content, "rose");
    expect(result).toBe("module.exports = {}");
  });
});

describe("getTemplateFiles", () => {
  it("returns base templates when includeDocker is false", () => {
    const files = getTemplateFiles(false);
    expect(files.length).toBe(24);
    expect(files.some(([name]) => name === "docker-compose.yml.hbs")).toBe(false);
    expect(files.some(([name]) => name === "backend-dockerfile.hbs")).toBe(false);
  });

  it("returns all templates when includeDocker is true", () => {
    const files = getTemplateFiles(true);
    expect(files.length).toBe(29); // 24 base + 5 docker
    expect(files.some(([name]) => name === "docker-compose.yml.hbs")).toBe(true);
    expect(files.some(([name]) => name === "backend-dockerfile.hbs")).toBe(true);
    expect(files.some(([name]) => name === "frontend-dockerfile.hbs")).toBe(true);
    expect(files.some(([name]) => name === "backend-dockerignore.hbs")).toBe(true);
    expect(files.some(([name]) => name === "frontend-dockerignore.hbs")).toBe(true);
  });

  it("includes all required base templates", () => {
    const files = getTemplateFiles(false);
    const templateNames = files.map(([name]) => name);

    expect(templateNames).toContain("backend.env.hbs");
    expect(templateNames).toContain("backend.env.test.hbs");
    expect(templateNames).toContain("frontend.env.hbs");
    expect(templateNames).toContain("requirements.txt.hbs");
    expect(templateNames).toContain("config.py.hbs");
    expect(templateNames).toContain("gitignore.hbs");
    expect(templateNames).toContain("conftest.py.hbs");
  });

  it("has correct output paths", () => {
    const files = getTemplateFiles(false);
    const fileMap = Object.fromEntries(files);

    expect(fileMap["backend.env.hbs"]).toBe("backend/.env.example");
    expect(fileMap["config.py.hbs"]).toBe("backend/app/core/config.py");
    expect(fileMap["gitignore.hbs"]).toBe(".gitignore");
  });
});

describe("getFilesToRemove", () => {
  describe("payment files", () => {
    it("removes stripe and paystack when using nomba", () => {
      const result = getFilesToRemove("nomba", "resend");
      expect(result.paymentFiles).toContain("stripe.py");
      expect(result.paymentFiles).toContain("paystack.py");
      expect(result.paymentFiles).not.toContain("nomba.py");
    });

    it("removes nomba and paystack when using stripe", () => {
      const result = getFilesToRemove("stripe", "resend");
      expect(result.paymentFiles).toContain("nomba.py");
      expect(result.paymentFiles).toContain("paystack.py");
      expect(result.paymentFiles).not.toContain("stripe.py");
    });

    it("removes nomba and stripe when using paystack", () => {
      const result = getFilesToRemove("paystack", "resend");
      expect(result.paymentFiles).toContain("nomba.py");
      expect(result.paymentFiles).toContain("stripe.py");
      expect(result.paymentFiles).not.toContain("paystack.py");
    });
  });

  describe("email files", () => {
    it("removes brevo when using resend", () => {
      const result = getFilesToRemove("nomba", "resend");
      expect(result.emailFiles).toContain("brevo.py");
      expect(result.emailFiles).not.toContain("resend.py");
    });

    it("removes resend when using brevo", () => {
      const result = getFilesToRemove("nomba", "brevo");
      expect(result.emailFiles).toContain("resend.py");
      expect(result.emailFiles).not.toContain("brevo.py");
    });

    it("removes all email files when using none", () => {
      const result = getFilesToRemove("nomba", "none");
      expect(result.emailFiles).toContain("resend.py");
      expect(result.emailFiles).toContain("brevo.py");
      expect(result.emailFiles.length).toBe(2);
    });
  });

  describe("payment test files", () => {
    it("removes stripe and paystack tests when using nomba", () => {
      const result = getFilesToRemove("nomba", "resend");
      expect(result.paymentTestFiles).toContain("test_stripe_provider.py");
      expect(result.paymentTestFiles).toContain("test_paystack_provider.py");
      expect(result.paymentTestFiles).not.toContain("test_nomba_provider.py");
    });

    it("removes nomba and paystack tests when using stripe", () => {
      const result = getFilesToRemove("stripe", "resend");
      expect(result.paymentTestFiles).toContain("test_nomba_provider.py");
      expect(result.paymentTestFiles).toContain("test_paystack_provider.py");
      expect(result.paymentTestFiles).not.toContain("test_stripe_provider.py");
    });

    it("removes nomba and stripe tests when using paystack", () => {
      const result = getFilesToRemove("paystack", "resend");
      expect(result.paymentTestFiles).toContain("test_nomba_provider.py");
      expect(result.paymentTestFiles).toContain("test_stripe_provider.py");
      expect(result.paymentTestFiles).not.toContain("test_paystack_provider.py");
    });
  });
});
