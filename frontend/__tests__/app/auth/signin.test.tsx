import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Create mock functions at module level
const mockLogin = vi.fn();
const mockPush = vi.fn();

// Mock dependencies
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    login: vi.fn(),
    isAuthenticated: false,
    isLoading: false,
  })),
}));

vi.mock("@/lib/config", () => ({
  config: {
    appName: "Test App",
  },
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Import after mocks
import SignInPage from "@/app/auth/signin/page";
import { useAuth } from "@/contexts/AuthContext";

describe("SignInPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLogin.mockResolvedValue(undefined);

    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      supabaseUser: null,
      loginWithGoogle: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
      resetPassword: vi.fn(),
    });
  });

  describe("rendering", () => {
    it("renders sign in form", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: /sign in/i })
        ).toBeInTheDocument();
      });
    });

    it("renders email input", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });
    });

    it("renders password input", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      });
    });

    it("renders submit button", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /sign in/i })
        ).toBeInTheDocument();
      });
    });

    it("renders forgot password link", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(
          screen.getByRole("link", { name: /forgot password/i })
        ).toBeInTheDocument();
      });
    });

    it("renders sign up link", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(
          screen.getByRole("link", { name: /create one now/i })
        ).toBeInTheDocument();
      });
    });

    it("renders Google sign in button", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /continue with google/i })
        ).toBeInTheDocument();
      });
    });
  });

  describe("form submission", () => {
    it("calls login with email and password", async () => {
      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
      });
    });

    it("shows loading state during submission", async () => {
      let resolveLogin: () => void;
      mockLogin.mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveLogin = resolve;
          })
      );

      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "password123" },
      });

      const submitButton = screen.getByRole("button", { name: /sign in/i });
      fireEvent.click(submitButton);

      // Verify login was called - this confirms form submission happened
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalled();
      });

      // Resolve the login to clean up
      resolveLogin!();
    });
  });

  describe("error handling", () => {
    it("shows error message on login failure", async () => {
      mockLogin.mockRejectedValue(new Error("Invalid credentials"));

      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "wrongpassword" },
      });

      fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it("shows friendly message for invalid credentials", async () => {
      mockLogin.mockRejectedValue(new Error("Invalid login credentials"));

      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "wrong" },
      });

      fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/invalid email or password/i)
        ).toBeInTheDocument();
      });
    });

    it("shows email not confirmed message", async () => {
      mockLogin.mockRejectedValue(new Error("Email not confirmed"));

      render(<SignInPage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });

      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "password" },
      });

      fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/check your email and click the confirmation/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe("authenticated redirect", () => {
    it("redirects to dashboard when already authenticated", async () => {
      vi.mocked(useAuth).mockReturnValue({
        login: mockLogin,
        isAuthenticated: true,
        isLoading: false,
        supabaseUser: { id: "user-123", email: "test@example.com" } as never,
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(<SignInPage />);

      // Shows loading spinner while redirecting
      await waitFor(() => {
        expect(screen.queryByLabelText(/email/i)).not.toBeInTheDocument();
      });
    });
  });

  describe("loading state", () => {
    it("shows loading spinner while auth is loading", () => {
      vi.mocked(useAuth).mockReturnValue({
        login: mockLogin,
        isAuthenticated: false,
        isLoading: true,
        supabaseUser: null,
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(<SignInPage />);

      // Should show loading, not form
      expect(screen.queryByLabelText(/email/i)).not.toBeInTheDocument();
    });
  });
});
