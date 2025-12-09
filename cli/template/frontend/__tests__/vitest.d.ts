/// <reference types="vitest/globals" />

import "@testing-library/jest-dom";

declare global {
  namespace Vi {
    interface JestAssertion<T = unknown> {
      toBeInTheDocument(): void;
      toHaveTextContent(text: string): void;
      toBeVisible(): void;
      toBeDisabled(): void;
      toHaveAttribute(attr: string, value?: string): void;
      toHaveClass(className: string): void;
      toHaveStyle(style: Record<string, unknown>): void;
    }
  }
}
