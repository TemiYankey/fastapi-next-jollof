import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["src/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["src/lib/**/*.ts"],
      exclude: ["src/**/*.test.ts", "src/lib/types.ts"],
      thresholds: {
        lines: 99,
        functions: 99,
        branches: 95,
        statements: 99,
      },
    },
  },
});
