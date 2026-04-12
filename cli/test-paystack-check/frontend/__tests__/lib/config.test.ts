import { beforeEach, describe, expect, it, vi } from "vitest";

describe("config", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe("appName", () => {
    it("uses environment variable when set", async () => {
      process.env.NEXT_PUBLIC_APP_NAME = "My Custom App";

      const { config } = await import("@/lib/config");

      expect(config.appName).toBe("My Custom App");
    });

    it("defaults to Jollof App", async () => {
      delete process.env.NEXT_PUBLIC_APP_NAME;

      const { config } = await import("@/lib/config");

      expect(config.appName).toBe("Jollof App");
    });
  });

  describe("supabaseUrl", () => {
    it("uses environment variable when set", async () => {
      process.env.NEXT_PUBLIC_SUPABASE_URL = "https://myproject.supabase.co";

      const { config } = await import("@/lib/config");

      expect(config.supabaseUrl).toBe("https://myproject.supabase.co");
    });

    it("defaults to placeholder for build compatibility", async () => {
      delete process.env.NEXT_PUBLIC_SUPABASE_URL;

      const { config } = await import("@/lib/config");

      expect(config.supabaseUrl).toBe("https://placeholder.supabase.co");
    });
  });

  describe("supabaseKey", () => {
    it("uses environment variable when set", async () => {
      process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY = "test-key-123";

      const { config } = await import("@/lib/config");

      expect(config.supabaseKey).toBe("test-key-123");
    });

    it("defaults to placeholder for build compatibility", async () => {
      delete process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

      const { config } = await import("@/lib/config");

      expect(config.supabaseKey).toBe("placeholder-key");
    });
  });

  describe("apiUrl", () => {
    it("uses environment variable when set", async () => {
      process.env.NEXT_PUBLIC_API_URL = "https://api.myapp.com";

      const { config } = await import("@/lib/config");

      expect(config.apiUrl).toBe("https://api.myapp.com");
    });

    it("defaults to localhost", async () => {
      delete process.env.NEXT_PUBLIC_API_URL;

      const { config } = await import("@/lib/config");

      expect(config.apiUrl).toBe("http://localhost:8000/api");
    });
  });

  describe("config structure", () => {
    it("exports all required fields", async () => {
      const { config } = await import("@/lib/config");

      expect(config).toHaveProperty("appName");
      expect(config).toHaveProperty("supabaseUrl");
      expect(config).toHaveProperty("supabaseKey");
      expect(config).toHaveProperty("apiUrl");
    });
  });
});
