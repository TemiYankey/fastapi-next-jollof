/**
 * Robust logout utility that handles all edge cases.
 * Used consistently across AuthContext and API interceptor.
 */

import { config } from "@/lib/config";
import logger from "./logger";

export const robustLogout = async () => {
  try {
    const [{ supabase }, { useUserStore }] = await Promise.all([
      import("@/lib/supabase"),
      import("@/stores/userStore"),
    ]);

    const { clearUser } = useUserStore.getState();

    // Step 1: Clear user state immediately (optimistic logout)
    clearUser();

    // Step 2: Try Supabase logout with timeout
    const logoutPromise = supabase.auth.signOut();
    const timeoutPromise = new Promise<void>((_, reject) =>
      setTimeout(() => reject(new Error("Logout timeout")), 5000)
    );

    await Promise.race([logoutPromise, timeoutPromise]);
  } catch (error) {
    logger.warn("Logout error (user still logged out locally):", error);

    // Step 3: Force clear any remaining Supabase session data
    if (typeof window !== "undefined") {
      try {
        const keysToRemove: string[] = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && key.startsWith("sb-") && key.includes("auth")) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach((key) => localStorage.removeItem(key));

        try {
          const supabaseUrl = config.supabaseUrl;
          if (supabaseUrl) {
            const projectId = supabaseUrl.split("//")[1].split(".")[0];
            const supabaseKey = `sb-${projectId}-auth-token`;
            localStorage.removeItem(supabaseKey);
          }
        } catch (urlError) {
          logger.warn("Could not determine Supabase project ID:", urlError);
        }
      } catch (storageError) {
        logger.warn("Failed to clear localStorage:", storageError);
      }
    }

    // Step 4: Ensure user state is cleared again (redundant but safe)
    try {
      const { useUserStore } = await import("@/stores/userStore");
      const { clearUser } = useUserStore.getState();
      clearUser();
    } catch (storeError) {
      logger.warn("Failed to clear user store:", storeError);
    }
  }
};
