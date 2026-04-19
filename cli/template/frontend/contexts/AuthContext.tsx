"use client";

import { supabase } from "@/lib/supabase";
import { useUserStore } from "@/stores/userStore";
import { authApi } from "@/utils/api/auth";
import { robustLogout } from "@/utils/robustLogout";
import { AuthError, User as SupabaseUser } from "@supabase/supabase-js";
import { useQueryClient } from "@tanstack/react-query";
import { usePathname, useRouter } from "next/navigation";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";

interface AuthContextType {
  supabaseUser: SupabaseUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<{ error: AuthError | null }>;
  signup: (data: SignupData) => Promise<{ userExists: boolean }>;
  verifyOtp: (email: string, token: string) => Promise<void>;
  resendSignupCode: (email: string) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
}

interface SignupData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [supabaseUser, setSupabaseUser] = useState<SupabaseUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const queryClient = useQueryClient();
  const { user, setUser, clearUser } = useUserStore();

  // Helper function to check if session is a recovery session
  const isRecoverySession = (session: unknown) => {
    const sess = session as { access_token?: string } | null;
    return (
      sess?.access_token &&
      (() => {
        try {
          const payload = JSON.parse(
            atob(sess.access_token!.split(".")[1])
          );
          return payload.amr?.some(
            (method: { method: string }) => method.method === "recovery"
          );
        } catch {
          return false;
        }
      })()
    );
  };

  useEffect(() => {
    const getInitialSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      setSupabaseUser(session?.user ?? null);

      const isRecovery = isRecoverySession(session);

      if (isRecovery && session?.user) {
        if (pathname === "/auth/reset-password") {
          setIsLoading(false);
          return;
        } else {
          await robustLogout();
          setIsLoading(false);
          return;
        }
      }

      if (session?.user && session?.access_token) {
        try {
          const user = await authApi.meWithToken(session.access_token);
          setUser(user);
        } catch {
          clearUser();
          await robustLogout();
        }
      } else {
        clearUser();
      }

      setIsLoading(false);
      setInitialLoadComplete(true);
    };

    getInitialSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setSupabaseUser(session?.user ?? null);

      if (event === "SIGNED_OUT") {
        queryClient.clear();
        clearUser();
      } else if (event === "PASSWORD_RECOVERY") {
        router.push("/auth/reset-password");
      } else if (event === "SIGNED_IN") {
        if (session?.user && session?.access_token) {
          const isRecovery = isRecoverySession(session);

          if (!isRecovery) {
            try {
              const user = await authApi.meWithToken(session.access_token);
              setUser(user);
            } catch {
              clearUser();
              await robustLogout();
            }
          }
        }
      } else if (event === "TOKEN_REFRESHED") {
        // Token refreshed - no need to refetch user
      } else if (event === "USER_UPDATED") {
        // User updated in Supabase - could refetch if needed
      } else if (event === "INITIAL_SESSION") {
        // Initial session load - handled by getInitialSession
        return;
      }

      if (initialLoadComplete) {
        setIsLoading(false);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryClient, router, initialLoadComplete]);

  useEffect(() => {
    const checkRecoveryNavigation = async () => {
      if (pathname === "/auth/reset-password") return;

      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session?.user) return;

      const isRecovery = isRecoverySession(session);
      if (isRecovery) {
        await robustLogout();
      }
    };

    checkRecoveryNavigation();
  }, [pathname]);

  const login = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      throw new Error(error.message);
    }

    // User fetch is handled by onAuthStateChange SIGNED_IN event
    // This prevents duplicate API calls and works for all sign-in methods
  };

  const signup = async (data: SignupData) => {
    const { data: signupData, error } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: {
        data: {
          full_name: `${data.firstName} ${data.lastName}`,
          first_name: data.firstName,
          last_name: data.lastName,
          signup_source: "web",
          signup_timestamp: new Date().toISOString(),
        },
      },
    });

    if (error) {
      throw new Error(error.message);
    }

    // Check if user already exists (identities will be empty)
    const userExists =
      signupData.user &&
      signupData.user.identities &&
      signupData.user.identities.length === 0;

    return { userExists: !!userExists };
  };

  const verifyOtp = async (email: string, token: string) => {
    // Try signup type first, then email type as fallback
    let result = await supabase.auth.verifyOtp({
      email,
      token: token.trim(),
      type: "signup",
    });

    if (result.error) {
      result = await supabase.auth.verifyOtp({
        email,
        token: token.trim(),
        type: "email",
      });
    }

    if (result.error) {
      throw new Error(result.error.message);
    }
  };

  const resendSignupCode = async (email: string) => {
    const { error } = await supabase.auth.resend({
      type: "signup",
      email,
    });

    if (error) {
      throw new Error(error.message);
    }
  };

  const logout = async () => {
    await robustLogout();
  };

  const loginWithGoogle = async () => {
    // Preserve ?next param through OAuth flow
    const urlParams = new URLSearchParams(window.location.search);
    const next = urlParams.get("next");
    const callbackUrl = next
      ? `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`
      : `${window.location.origin}/auth/callback`;

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: callbackUrl,
        queryParams: {
          access_type: "offline",
          prompt: "consent",
        },
      },
    });

    return { error };
  };

  const resetPassword = async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });
    return { error };
  };

  const contextValue: AuthContextType = {
    supabaseUser,
    isLoading: isLoading,
    isAuthenticated: !!user,
    login,
    loginWithGoogle,
    signup,
    verifyOtp,
    resendSignupCode,
    logout,
    resetPassword,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
