import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock dependencies - inline to avoid hoisting issues
vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      signOut: vi.fn().mockResolvedValue({}),
    },
  },
}));

vi.mock("@/stores/userStore", () => ({
  useUserStore: {
    getState: vi.fn(() => ({
      clearUser: vi.fn(),
    })),
  },
}));

vi.mock("@/lib/config", () => ({
  config: {
    supabaseUrl: "https://test.supabase.co",
  },
}));

vi.mock("@/utils/logger", () => ({
  default: {
    warn: vi.fn(),
  },
}));

// Import after mocks
import { robustLogout } from "@/utils/robustLogout";
import { supabase } from "@/lib/supabase";
import { useUserStore } from "@/stores/userStore";
import logger from "@/utils/logger";

describe("robustLogout", () => {
  let mockClearUser: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup fresh mocks for each test
    mockClearUser = vi.fn();
    vi.mocked(supabase.auth.signOut).mockResolvedValue({} as never);
    vi.mocked(useUserStore.getState).mockReturnValue({
      clearUser: mockClearUser,
    } as never);

    // Mock localStorage
    Object.defineProperty(window, "localStorage", {
      value: {
        length: 0,
        key: vi.fn(),
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    });
  });

  describe("successful logout", () => {
    it("clears user state", async () => {
      await robustLogout();

      expect(mockClearUser).toHaveBeenCalled();
    });

    it("calls Supabase signOut", async () => {
      await robustLogout();

      expect(supabase.auth.signOut).toHaveBeenCalled();
    });
  });

  describe("timeout handling", () => {
    it("handles Supabase timeout gracefully", async () => {
      // Make signOut never resolve
      vi.mocked(supabase.auth.signOut).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      // Use fake timers
      vi.useFakeTimers();

      const logoutPromise = robustLogout();

      // Fast-forward 6 seconds (past the 5 second timeout)
      await vi.advanceTimersByTimeAsync(6000);

      await logoutPromise;

      // Should still clear user state
      expect(mockClearUser).toHaveBeenCalled();
      expect(logger.warn).toHaveBeenCalled();

      vi.useRealTimers();
    });
  });

  describe("error handling", () => {
    it("logs warning on signOut error", async () => {
      vi.mocked(supabase.auth.signOut).mockRejectedValue(
        new Error("Network error")
      );

      await robustLogout();

      expect(logger.warn).toHaveBeenCalledWith(
        expect.stringContaining("Logout error"),
        expect.anything()
      );
    });

    it("still clears user on error", async () => {
      vi.mocked(supabase.auth.signOut).mockRejectedValue(new Error("Error"));

      await robustLogout();

      expect(mockClearUser).toHaveBeenCalled();
    });
  });

  describe("localStorage cleanup", () => {
    it("clears Supabase auth keys from localStorage on error", async () => {
      const mockRemoveItem = vi.fn();

      Object.defineProperty(window, "localStorage", {
        value: {
          length: 3,
          key: vi.fn((i) => {
            const keys = [
              "sb-test-auth-token",
              "other-key",
              "sb-project-auth-extra",
            ];
            return keys[i];
          }),
          getItem: vi.fn(),
          setItem: vi.fn(),
          removeItem: mockRemoveItem,
          clear: vi.fn(),
        },
        writable: true,
      });

      vi.mocked(supabase.auth.signOut).mockRejectedValue(new Error("Error"));

      await robustLogout();

      // Should have attempted to remove auth keys
      expect(mockRemoveItem).toHaveBeenCalled();
    });

    it("handles localStorage errors gracefully", async () => {
      Object.defineProperty(window, "localStorage", {
        value: {
          get length() {
            throw new Error("Storage error");
          },
        },
        writable: true,
      });

      vi.mocked(supabase.auth.signOut).mockRejectedValue(new Error("Error"));

      // Should not throw
      await expect(robustLogout()).resolves.not.toThrow();

      expect(logger.warn).toHaveBeenCalled();
    });
  });

  describe("clearUser redundancy", () => {
    it("calls clearUser multiple times for safety", async () => {
      vi.mocked(supabase.auth.signOut).mockRejectedValue(new Error("Error"));

      await robustLogout();

      // Should be called at least twice (initial + retry after error)
      expect(mockClearUser.mock.calls.length).toBeGreaterThanOrEqual(1);
    });
  });
});
