import { describe, it, expect } from "vitest";
import {
  COLOR_THEMES,
  PAYMENT_PROVIDERS,
  EMAIL_PROVIDERS,
  COLOR_HEX,
} from "../lib/constants.js";

describe("COLOR_THEMES", () => {
  it("has all expected color themes", () => {
    const themes = Object.keys(COLOR_THEMES);
    expect(themes).toContain("indigo");
    expect(themes).toContain("violet");
    expect(themes).toContain("blue");
    expect(themes).toContain("emerald");
    expect(themes).toContain("rose");
    expect(themes).toContain("amber");
    expect(themes).toContain("cyan");
    expect(themes).toContain("orange");
    expect(themes.length).toBe(8);
  });

  it("each theme has required properties", () => {
    Object.values(COLOR_THEMES).forEach((theme) => {
      expect(theme).toHaveProperty("name");
      expect(theme).toHaveProperty("description");
      expect(theme).toHaveProperty("primary");
      expect(theme).toHaveProperty("hex");
    });
  });

  it("each theme has valid hex color", () => {
    const hexPattern = /^#[0-9a-f]{6}$/i;
    Object.values(COLOR_THEMES).forEach((theme) => {
      expect(theme.hex).toMatch(hexPattern);
    });
  });

  it("primary matches the key", () => {
    Object.entries(COLOR_THEMES).forEach(([key, theme]) => {
      expect(theme.primary).toBe(key);
    });
  });

  it("indigo has correct values", () => {
    expect(COLOR_THEMES.indigo).toEqual({
      name: "Indigo",
      description: "Professional & trustworthy",
      primary: "indigo",
      hex: "#6366f1",
    });
  });

  it("orange has Jollof in name", () => {
    expect(COLOR_THEMES.orange.name).toBe("Orange (Jollof)");
  });
});

describe("PAYMENT_PROVIDERS", () => {
  it("has all expected providers", () => {
    const providers = Object.keys(PAYMENT_PROVIDERS);
    expect(providers).toContain("nomba");
    expect(providers).toContain("paystack");
    expect(providers).toContain("stripe");
    expect(providers.length).toBe(3);
  });

  it("each provider has required properties", () => {
    Object.values(PAYMENT_PROVIDERS).forEach((provider) => {
      expect(provider).toHaveProperty("name");
      expect(provider).toHaveProperty("description");
      expect(provider).toHaveProperty("regions");
      expect(provider).toHaveProperty("comingSoon");
      expect(Array.isArray(provider.regions)).toBe(true);
    });
  });

  it("nomba is not coming soon", () => {
    expect(PAYMENT_PROVIDERS.nomba.comingSoon).toBe(false);
  });

  it("stripe and paystack are coming soon", () => {
    expect(PAYMENT_PROVIDERS.stripe.comingSoon).toBe(true);
    expect(PAYMENT_PROVIDERS.paystack.comingSoon).toBe(true);
  });

  it("nomba has Nigeria region", () => {
    expect(PAYMENT_PROVIDERS.nomba.regions).toContain("Nigeria");
  });

  it("stripe has global coverage", () => {
    expect(PAYMENT_PROVIDERS.stripe.regions.some((r) => r.includes("Global"))).toBe(true);
  });

  it("paystack covers multiple African countries", () => {
    expect(PAYMENT_PROVIDERS.paystack.regions).toContain("Nigeria");
    expect(PAYMENT_PROVIDERS.paystack.regions).toContain("Ghana");
    expect(PAYMENT_PROVIDERS.paystack.regions).toContain("South Africa");
    expect(PAYMENT_PROVIDERS.paystack.regions).toContain("Kenya");
  });
});

describe("EMAIL_PROVIDERS", () => {
  it("has all expected providers", () => {
    const providers = Object.keys(EMAIL_PROVIDERS);
    expect(providers).toContain("resend");
    expect(providers).toContain("brevo");
    expect(providers).toContain("none");
    expect(providers.length).toBe(3);
  });

  it("each provider has required properties", () => {
    Object.values(EMAIL_PROVIDERS).forEach((provider) => {
      expect(provider).toHaveProperty("name");
      expect(provider).toHaveProperty("description");
    });
  });

  it("resend has correct name", () => {
    expect(EMAIL_PROVIDERS.resend.name).toBe("Resend");
  });

  it("brevo mentions Sendinblue", () => {
    expect(EMAIL_PROVIDERS.brevo.description).toContain("Sendinblue");
  });

  it("none option exists for skipping", () => {
    expect(EMAIL_PROVIDERS.none.name).toContain("None");
    expect(EMAIL_PROVIDERS.none.description).toContain("later");
  });
});

describe("COLOR_HEX", () => {
  it("has all expected colors", () => {
    const colors = Object.keys(COLOR_HEX);
    expect(colors).toContain("indigo");
    expect(colors).toContain("violet");
    expect(colors).toContain("blue");
    expect(colors).toContain("emerald");
    expect(colors).toContain("rose");
    expect(colors).toContain("amber");
    expect(colors).toContain("cyan");
    expect(colors).toContain("orange");
    expect(colors.length).toBe(8);
  });

  it("all values are valid hex colors", () => {
    const hexPattern = /^#[0-9a-f]{6}$/i;
    Object.values(COLOR_HEX).forEach((hex) => {
      expect(hex).toMatch(hexPattern);
    });
  });

  it("matches COLOR_THEMES hex values", () => {
    Object.entries(COLOR_THEMES).forEach(([key, theme]) => {
      expect(COLOR_HEX[key]).toBe(theme.hex);
    });
  });

  it("has correct specific values", () => {
    expect(COLOR_HEX.indigo).toBe("#6366f1");
    expect(COLOR_HEX.rose).toBe("#f43f5e");
    expect(COLOR_HEX.emerald).toBe("#10b981");
    expect(COLOR_HEX.orange).toBe("#f97316");
  });
});
