import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock useAuth
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    loginWithGoogle: vi.fn().mockResolvedValue({ error: null }),
  })),
}));

// Import after mocks
import { GoogleSignInButton } from "@/components/ui/GoogleSignInButton";
import { useAuth } from "@/contexts/AuthContext";

describe("GoogleSignInButton", () => {
  const mockLoginWithGoogle = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockLoginWithGoogle.mockResolvedValue({ error: null });
    vi.mocked(useAuth).mockReturnValue({
      loginWithGoogle: mockLoginWithGoogle,
      isLoading: false,
      isAuthenticated: false,
      supabaseUser: null,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
      resetPassword: vi.fn(),
    });
  });

  describe("rendering", () => {
    it("renders button with Google text", () => {
      render(<GoogleSignInButton />);

      expect(screen.getByRole("button")).toHaveTextContent(
        "Continue with Google"
      );
    });

    it("renders Google icon", () => {
      const { container } = render(<GoogleSignInButton />);

      const svg = container.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("has type button", () => {
      render(<GoogleSignInButton />);

      expect(screen.getByRole("button")).toHaveAttribute("type", "button");
    });
  });

  describe("sizes", () => {
    it("renders with default md size", () => {
      render(<GoogleSignInButton />);

      const button = screen.getByRole("button");
      expect(button.className).toContain("py-3");
      expect(button.className).toContain("text-sm");
    });

    it("renders with sm size", () => {
      render(<GoogleSignInButton size="sm" />);

      const button = screen.getByRole("button");
      expect(button.className).toContain("py-2");
    });

    it("renders with lg size", () => {
      render(<GoogleSignInButton size="lg" />);

      const button = screen.getByRole("button");
      expect(button.className).toContain("py-4");
      expect(button.className).toContain("text-base");
    });
  });

  describe("click handling", () => {
    it("calls loginWithGoogle on click", async () => {
      render(<GoogleSignInButton />);

      fireEvent.click(screen.getByRole("button"));

      await waitFor(() => {
        expect(mockLoginWithGoogle).toHaveBeenCalledTimes(1);
      });
    });

    it("shows loading state while signing in", async () => {
      // Make loginWithGoogle take time
      mockLoginWithGoogle.mockImplementation(
        () =>
          new Promise((resolve) => setTimeout(() => resolve({ error: null }), 100))
      );

      render(<GoogleSignInButton />);

      const button = screen.getByRole("button");
      fireEvent.click(button);

      // Should show spinner
      await waitFor(() => {
        expect(button.innerHTML).toContain("animate-spin");
      });

      // Text should be hidden during loading
      expect(
        screen.queryByText("Continue with Google")
      ).not.toBeInTheDocument();
    });

    it("is disabled while loading", async () => {
      mockLoginWithGoogle.mockImplementation(
        () =>
          new Promise((resolve) => setTimeout(() => resolve({ error: null }), 100))
      );

      render(<GoogleSignInButton />);

      const button = screen.getByRole("button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(button).toBeDisabled();
      });
    });

    it("re-enables after sign-in completes", async () => {
      mockLoginWithGoogle.mockResolvedValue({ error: null });

      render(<GoogleSignInButton />);

      const button = screen.getByRole("button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });

      expect(
        screen.getByText("Continue with Google")
      ).toBeInTheDocument();
    });
  });

  describe("error handling", () => {
    it("handles Google sign-in error", async () => {
      const consoleError = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      mockLoginWithGoogle.mockResolvedValue({
        error: { message: "OAuth error" },
      });

      render(<GoogleSignInButton />);

      fireEvent.click(screen.getByRole("button"));

      await waitFor(() => {
        expect(consoleError).toHaveBeenCalledWith(
          "Google sign in error:",
          expect.anything()
        );
      });

      consoleError.mockRestore();
    });

    it("handles thrown error", async () => {
      const consoleError = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      mockLoginWithGoogle.mockRejectedValue(new Error("Network error"));

      render(<GoogleSignInButton />);

      fireEvent.click(screen.getByRole("button"));

      await waitFor(() => {
        expect(consoleError).toHaveBeenCalledWith(
          "Google sign in error:",
          expect.any(Error)
        );
      });

      consoleError.mockRestore();
    });

    it("resets loading state after error", async () => {
      mockLoginWithGoogle.mockRejectedValue(new Error("Error"));

      render(<GoogleSignInButton />);

      const button = screen.getByRole("button");
      fireEvent.click(button);

      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });
    });
  });

  describe("accessibility", () => {
    it("is keyboard accessible", () => {
      render(<GoogleSignInButton />);

      const button = screen.getByRole("button");
      button.focus();

      expect(document.activeElement).toBe(button);
    });
  });
});
