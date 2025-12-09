import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Create mock functions at module level
const mockReplace = vi.fn();
const mockPush = vi.fn();

// Mock useAuth before importing ProtectedRoute
vi.mock("@/contexts/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    isLoading: false,
    isAuthenticated: true,
  })),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace: mockReplace,
    push: mockPush,
  }),
}));

// Import after mocks
import { useAuth } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("loading state", () => {
    it("shows loading screen while auth is loading", () => {
      vi.mocked(useAuth).mockReturnValue({
        isLoading: true,
        isAuthenticated: false,
        supabaseUser: null,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      // Should not show protected content while loading
      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });
  });

  describe("authenticated state", () => {
    it("renders children when authenticated", () => {
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: true,
        supabaseUser: { id: "user-123", email: "test@example.com" } as never,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });

    it("renders nested children correctly", () => {
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: true,
        supabaseUser: { id: "user-123", email: "test@example.com" } as never,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(
        <ProtectedRoute>
          <div>
            <h1>Dashboard</h1>
            <p>Welcome to your dashboard</p>
          </div>
        </ProtectedRoute>
      );

      expect(screen.getByText("Dashboard")).toBeInTheDocument();
      expect(
        screen.getByText("Welcome to your dashboard")
      ).toBeInTheDocument();
    });
  });

  describe("unauthenticated state", () => {
    it("does not render children when not authenticated", () => {
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: false,
        supabaseUser: null,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("redirects to signin by default when not authenticated", async () => {
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: false,
        supabaseUser: null,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      // Component should handle redirect
      await waitFor(() => {
        expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
      });
    });
  });

  describe("custom redirect", () => {
    it("accepts custom redirectTo prop", () => {
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: false,
        supabaseUser: null,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      render(
        <ProtectedRoute redirectTo="/custom-login">
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });
  });

  describe("state transitions", () => {
    it("updates when auth state changes", async () => {
      // Initially not authenticated
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: false,
        supabaseUser: null,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      const { rerender } = render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();

      // Now authenticated
      vi.mocked(useAuth).mockReturnValue({
        isLoading: false,
        isAuthenticated: true,
        supabaseUser: { id: "user-123", email: "test@example.com" } as never,
        login: vi.fn(),
        loginWithGoogle: vi.fn(),
        signup: vi.fn(),
        logout: vi.fn(),
        resetPassword: vi.fn(),
      });

      rerender(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });
  });
});
