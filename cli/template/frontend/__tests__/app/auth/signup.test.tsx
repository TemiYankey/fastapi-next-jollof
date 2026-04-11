import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock dependencies
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    signup: vi.fn(),
  })),
}));

vi.mock("@/lib/config", () => ({
  config: {
    appName: "Test App",
  },
}));

// Import after mocks
import SignUpPage from "@/app/auth/signup/page";
import { useAuth } from "@/contexts/AuthContext";

describe("SignUpPage", () => {
  const mockSignup = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockSignup.mockResolvedValue(undefined);

    vi.mocked(useAuth).mockReturnValue({
      signup: mockSignup,
      login: vi.fn(),
      isAuthenticated: false,
      isLoading: false,
      supabaseUser: null,
      loginWithGoogle: vi.fn(),
      logout: vi.fn(),
      resetPassword: vi.fn(),
    });
  });

  describe("rendering", () => {
    it("renders sign up form", () => {
      render(<SignUpPage />);

      expect(
        screen.getByRole("heading", { name: /create your account/i })
      ).toBeInTheDocument();
    });

    it("renders first name input", () => {
      render(<SignUpPage />);

      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    });

    it("renders last name input", () => {
      render(<SignUpPage />);

      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    });

    it("renders email input", () => {
      render(<SignUpPage />);

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    });

    it("renders password input", () => {
      render(<SignUpPage />);

      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    });

    it("renders submit button", () => {
      render(<SignUpPage />);

      expect(
        screen.getByRole("button", { name: /create account/i })
      ).toBeInTheDocument();
    });

    it("renders sign in link", () => {
      render(<SignUpPage />);

      expect(
        screen.getByRole("link", { name: /sign in/i })
      ).toBeInTheDocument();
    });

    it("renders Google sign in button", () => {
      render(<SignUpPage />);

      expect(
        screen.getByRole("button", { name: /continue with google/i })
      ).toBeInTheDocument();
    });
  });

  describe("password strength indicator", () => {
    it("shows password requirements when typing", () => {
      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "test" },
      });

      // Password strength component shows requirements
      expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
    });
  });

  describe("form submission", () => {
    it("calls signup with form data when all requirements met", async () => {
      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      // Password that meets all requirements
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(mockSignup).toHaveBeenCalledWith({
          firstName: "John",
          lastName: "Doe",
          email: "john@example.com",
          password: "Password123",
        });
      });
    });

    it("disables button during submission", async () => {
      mockSignup.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByRole("button", { name: /create account/i })).toBeDisabled();
      });
    });
  });

  describe("validation", () => {
    it("shows error when password requirements not met", async () => {
      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "short" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/please meet all password requirements/i)
        ).toBeInTheDocument();
      });

      // Should not call signup
      expect(mockSignup).not.toHaveBeenCalled();
    });
  });

  describe("error handling", () => {
    it("shows error message on signup failure", async () => {
      mockSignup.mockRejectedValue(new Error("Email already registered"));

      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "existing@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/email already registered/i)
        ).toBeInTheDocument();
      });
    });

    it("shows generic error for unknown errors", async () => {
      mockSignup.mockRejectedValue("Unknown error");

      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/failed to create account/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe("success state", () => {
    it("shows success message after signup", async () => {
      mockSignup.mockResolvedValue(undefined);

      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/check your email/i)).toBeInTheDocument();
      });
    });

    it("shows email address in success message", async () => {
      mockSignup.mockResolvedValue(undefined);

      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText("john@example.com")).toBeInTheDocument();
      });
    });

    it("shows link to sign in after success", async () => {
      mockSignup.mockResolvedValue(undefined);

      render(<SignUpPage />);

      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "John" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "Doe" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "john@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: "Password123" },
      });

      fireEvent.click(screen.getByRole("button", { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/back to sign in/i)).toBeInTheDocument();
      });
    });
  });
});
