import { describe, it, expect } from "vitest";
import { validateProjectName, validatePort, validateAppName } from "../lib/validation.js";

describe("validateProjectName", () => {
  it("returns error for empty string", () => {
    expect(validateProjectName("")).toBe("Project name is required");
  });

  it("returns error for whitespace only", () => {
    expect(validateProjectName("   ")).toBe("Project name is required");
  });

  it("returns error for uppercase letters", () => {
    expect(validateProjectName("MyApp")).toBe(
      "Project name can only contain lowercase letters, numbers, and hyphens"
    );
  });

  it("returns error for spaces", () => {
    expect(validateProjectName("my app")).toBe(
      "Project name can only contain lowercase letters, numbers, and hyphens"
    );
  });

  it("returns error for special characters", () => {
    expect(validateProjectName("my_app")).toBe(
      "Project name can only contain lowercase letters, numbers, and hyphens"
    );
    expect(validateProjectName("my.app")).toBe(
      "Project name can only contain lowercase letters, numbers, and hyphens"
    );
    expect(validateProjectName("my@app")).toBe(
      "Project name can only contain lowercase letters, numbers, and hyphens"
    );
  });

  it("returns error for leading hyphen", () => {
    expect(validateProjectName("-my-app")).toBe(
      "Project name cannot start or end with a hyphen"
    );
  });

  it("returns error for trailing hyphen", () => {
    expect(validateProjectName("my-app-")).toBe(
      "Project name cannot start or end with a hyphen"
    );
  });

  it("returns undefined for valid project name", () => {
    expect(validateProjectName("my-app")).toBeUndefined();
  });

  it("returns undefined for simple name", () => {
    expect(validateProjectName("myapp")).toBeUndefined();
  });

  it("returns undefined for name with numbers", () => {
    expect(validateProjectName("my-app-123")).toBeUndefined();
  });

  it("returns undefined for numeric name", () => {
    expect(validateProjectName("123")).toBeUndefined();
  });

  it("handles single character names", () => {
    expect(validateProjectName("a")).toBeUndefined();
    expect(validateProjectName("-")).toBe(
      "Project name cannot start or end with a hyphen"
    );
  });
});

describe("validatePort", () => {
  it("returns error for non-numeric value", () => {
    expect(validatePort("abc")).toBe("Port must be between 1024 and 65535");
  });

  it("returns error for port below 1024", () => {
    expect(validatePort("80")).toBe("Port must be between 1024 and 65535");
    expect(validatePort("443")).toBe("Port must be between 1024 and 65535");
    expect(validatePort("1023")).toBe("Port must be between 1024 and 65535");
  });

  it("returns error for port above 65535", () => {
    expect(validatePort("65536")).toBe("Port must be between 1024 and 65535");
    expect(validatePort("70000")).toBe("Port must be between 1024 and 65535");
  });

  it("returns error for negative port", () => {
    expect(validatePort("-1")).toBe("Port must be between 1024 and 65535");
  });

  it("returns error for empty string", () => {
    expect(validatePort("")).toBe("Port must be between 1024 and 65535");
  });

  it("returns undefined for valid port 1024", () => {
    expect(validatePort("1024")).toBeUndefined();
  });

  it("returns undefined for valid port 65535", () => {
    expect(validatePort("65535")).toBeUndefined();
  });

  it("returns undefined for common ports", () => {
    expect(validatePort("3000")).toBeUndefined();
    expect(validatePort("8000")).toBeUndefined();
    expect(validatePort("8080")).toBeUndefined();
    expect(validatePort("5000")).toBeUndefined();
  });

  it("returns error for decimal values", () => {
    expect(validatePort("3000.5")).toBe("Port must be between 1024 and 65535");
  });

  it("returns error for mixed string", () => {
    expect(validatePort("3000abc")).toBe("Port must be between 1024 and 65535");
  });
});

describe("validateAppName", () => {
  it("returns error for empty string", () => {
    expect(validateAppName("")).toBe("App name is required");
  });

  it("returns error for whitespace only", () => {
    expect(validateAppName("   ")).toBe("App name is required");
  });

  it("returns undefined for valid app name", () => {
    expect(validateAppName("My App")).toBeUndefined();
  });

  it("returns undefined for simple name", () => {
    expect(validateAppName("App")).toBeUndefined();
  });

  it("returns undefined for name with special characters", () => {
    expect(validateAppName("My App!")).toBeUndefined();
  });

  it("returns undefined for numeric name", () => {
    expect(validateAppName("123")).toBeUndefined();
  });

  it("returns undefined for single character", () => {
    expect(validateAppName("A")).toBeUndefined();
  });
});
