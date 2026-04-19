import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock dependencies before imports
vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      onAuthStateChange: vi.fn(() => ({
        data: {
          subscription: {
            unsubscribe: vi.fn(),
          },
        },
      })),
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
      signInWithOAuth: vi.fn(),
      resetPasswordForEmail: vi.fn(),
      signOut: vi.fn(),
      verifyOtp: vi.fn(),
      resend: vi.fn(),
    },
  },
}));

vi.mock("@/utils/api/auth", () => ({
  authApi: {
    me: vi.fn(),
    meWithToken: vi.fn(),
  },
}));

vi.mock("@/utils/robustLogout", () => ({
  robustLogout: vi.fn(),
}));

vi.mock("@/stores/userStore", () => ({
  useUserStore: vi.fn(() => ({
    user: null,
    setUser: vi.fn(),
    clearUser: vi.fn(),
  })),
}));

// Import after mocks
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/lib/supabase";
import { useUserStore } from "@/stores/userStore";
import { authApi } from "@/utils/api/auth";
import { robustLogout } from "@/utils/robustLogout";

describe("AuthContext", () => {
  let queryClient: QueryClient;

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    // Default mock implementations
    vi.mocked(supabase.auth.getSession).mockResolvedValue({
      data: { session: null },
      error: null,
    });

    vi.mocked(supabase.auth.onAuthStateChange).mockReturnValue({
      data: {
        subscription: {
          unsubscribe: vi.fn(),
        },
      },
    });
  });

  describe("useAuth hook", () => {
    it("throws error when used outside AuthProvider", () => {
      const consoleError = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      expect(() => {
        renderHook(() => useAuth());
      }).toThrow("useAuth must be used within an AuthProvider");

      consoleError.mockRestore();
    });

    it("provides auth context when inside AuthProvider", async () => {
      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current).toBeDefined();
        expect(result.current.isLoading).toBeDefined();
        expect(result.current.isAuthenticated).toBeDefined();
        expect(result.current.login).toBeDefined();
        expect(result.current.signup).toBeDefined();
        expect(result.current.logout).toBeDefined();
      });
    });
  });

  describe("initial state", () => {
    it("starts with loading state", async () => {
      const { result } = renderHook(() => useAuth(), { wrapper });

      // Initially loading
      expect(result.current.isLoading).toBe(true);
      expect(result.current.isAuthenticated).toBe(false);
    });

    it("sets isAuthenticated false when no session", async () => {
      vi.mocked(supabase.auth.getSession).mockResolvedValue({
        data: { session: null },
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.supabaseUser).toBeNull();
    });
  });

  describe("login", () => {
    it("successfully logs in user", async () => {
      vi.mocked(supabase.auth.signInWithPassword).mockResolvedValue({
        data: {
          user: { id: "user-123", email: "test@example.com" } as never,
          session: { access_token: "token" } as never,
        },
        error: null,
      });

      const mockSetUser = vi.fn();
      vi.mocked(useUserStore).mockReturnValue({
        user: null,
        setUser: mockSetUser,
        clearUser: vi.fn(),
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.login("test@example.com", "password");
      });

      // Login just calls signInWithPassword
      // User fetch is handled by onAuthStateChange SIGNED_IN event
      expect(supabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password",
      });
    });

    it("throws error on login failure", async () => {
      vi.mocked(supabase.auth.signInWithPassword).mockResolvedValue({
        data: { user: null, session: null },
        error: { message: "Invalid credentials" } as never,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(
        result.current.login("test@example.com", "wrong")
      ).rejects.toThrow("Invalid credentials");
    });
  });

  describe("signup", () => {
    it("successfully signs up user and returns userExists false", async () => {
      vi.mocked(supabase.auth.signUp).mockResolvedValue({
        data: {
          user: {
            id: "new-user",
            email: "new@example.com",
            identities: [{ id: "identity-1" }],
          } as never,
          session: null,
        },
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let signupResult: { userExists: boolean } | undefined;
      await act(async () => {
        signupResult = await result.current.signup({
          firstName: "New",
          lastName: "User",
          email: "new@example.com",
          password: "password123",
        });
      });

      expect(signupResult?.userExists).toBe(false);
      expect(supabase.auth.signUp).toHaveBeenCalledWith({
        email: "new@example.com",
        password: "password123",
        options: expect.objectContaining({
          data: expect.objectContaining({
            full_name: "New User",
            first_name: "New",
            last_name: "User",
          }),
        }),
      });
    });

    it("returns userExists true when user already exists", async () => {
      vi.mocked(supabase.auth.signUp).mockResolvedValue({
        data: {
          user: {
            id: "existing-user",
            email: "existing@example.com",
            identities: [], // Empty identities means user exists
          } as never,
          session: null,
        },
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let signupResult: { userExists: boolean } | undefined;
      await act(async () => {
        signupResult = await result.current.signup({
          firstName: "Test",
          lastName: "User",
          email: "existing@example.com",
          password: "password123",
        });
      });

      expect(signupResult?.userExists).toBe(true);
    });

    it("throws error on signup failure", async () => {
      vi.mocked(supabase.auth.signUp).mockResolvedValue({
        data: { user: null, session: null },
        error: { message: "Email already registered" } as never,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(
        result.current.signup({
          firstName: "Test",
          lastName: "User",
          email: "existing@example.com",
          password: "password",
        })
      ).rejects.toThrow("Email already registered");
    });
  });

  describe("verifyOtp", () => {
    it("successfully verifies OTP code", async () => {
      vi.mocked(supabase.auth.verifyOtp).mockResolvedValue({
        data: {
          user: { id: "user-123", email: "test@example.com" } as never,
          session: { access_token: "token" } as never,
        },
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.verifyOtp("test@example.com", "123456");
      });

      expect(supabase.auth.verifyOtp).toHaveBeenCalledWith({
        email: "test@example.com",
        token: "123456",
        type: "signup",
      });
    });

    it("throws error on invalid OTP", async () => {
      vi.mocked(supabase.auth.verifyOtp).mockResolvedValue({
        data: { user: null, session: null },
        error: { message: "Invalid OTP" } as never,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(
        result.current.verifyOtp("test@example.com", "000000")
      ).rejects.toThrow("Invalid OTP");
    });
  });

  describe("resendSignupCode", () => {
    it("successfully resends signup code", async () => {
      vi.mocked(supabase.auth.resend).mockResolvedValue({
        data: {},
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.resendSignupCode("test@example.com");
      });

      expect(supabase.auth.resend).toHaveBeenCalledWith({
        type: "signup",
        email: "test@example.com",
      });
    });

    it("throws error on resend failure", async () => {
      vi.mocked(supabase.auth.resend).mockResolvedValue({
        data: {},
        error: { message: "Rate limit exceeded" } as never,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await expect(
        result.current.resendSignupCode("test@example.com")
      ).rejects.toThrow("Rate limit exceeded");
    });
  });

  describe("logout", () => {
    it("calls robustLogout", async () => {
      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(robustLogout).toHaveBeenCalled();
    });
  });

  describe("loginWithGoogle", () => {
    it("initiates Google OAuth flow", async () => {
      vi.mocked(supabase.auth.signInWithOAuth).mockResolvedValue({
        data: { provider: "google", url: "https://oauth.google.com" },
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const response = await result.current.loginWithGoogle();

      expect(supabase.auth.signInWithOAuth).toHaveBeenCalledWith({
        provider: "google",
        options: expect.objectContaining({
          queryParams: {
            access_type: "offline",
            prompt: "consent",
          },
        }),
      });

      expect(response.error).toBeNull();
    });

    it("returns error on OAuth failure", async () => {
      const mockError = { message: "OAuth failed" };
      vi.mocked(supabase.auth.signInWithOAuth).mockResolvedValue({
        data: { provider: "google", url: null },
        error: mockError as never,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const response = await result.current.loginWithGoogle();

      expect(response.error).toEqual(mockError);
    });
  });

  describe("resetPassword", () => {
    it("sends password reset email", async () => {
      vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
        data: {},
        error: null,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const response = await result.current.resetPassword("test@example.com");

      expect(supabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        "test@example.com",
        expect.objectContaining({
          redirectTo: expect.stringContaining("/auth/reset-password"),
        })
      );

      expect(response.error).toBeNull();
    });

    it("returns error on reset failure", async () => {
      const mockError = { message: "User not found" };
      vi.mocked(supabase.auth.resetPasswordForEmail).mockResolvedValue({
        data: {},
        error: mockError as never,
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      const response = await result.current.resetPassword("unknown@example.com");

      expect(response.error).toEqual(mockError);
    });
  });

  describe("auth state change handling", () => {
    it("clears user on SIGNED_OUT event", async () => {
      let authStateCallback: ((event: string, session: unknown) => void) | null =
        null;

      vi.mocked(supabase.auth.onAuthStateChange).mockImplementation(
        (callback) => {
          authStateCallback = callback;
          return {
            data: {
              subscription: {
                unsubscribe: vi.fn(),
              },
            },
          };
        }
      );

      const mockClearUser = vi.fn();
      vi.mocked(useUserStore).mockReturnValue({
        user: { id: "user-123", email: "test@example.com" },
        setUser: vi.fn(),
        clearUser: mockClearUser,
      });

      renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(authStateCallback).not.toBeNull();
      });

      // Simulate SIGNED_OUT event
      await act(async () => {
        authStateCallback!("SIGNED_OUT", null);
      });

      expect(mockClearUser).toHaveBeenCalled();
    });
  });
});
