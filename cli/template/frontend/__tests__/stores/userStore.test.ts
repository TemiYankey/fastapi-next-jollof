import { act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the auth API inside vi.mock factory
vi.mock("@/utils/api/auth", () => ({
  authApi: {
    getCompleteProfile: vi.fn(),
    updateCompleteProfile: vi.fn(),
  },
}));

// Import after mocks
import { useUserStore } from "@/stores/userStore";
import { authApi } from "@/utils/api/auth";

// Type the mocked authApi
const mockAuthApi = authApi as {
  getCompleteProfile: ReturnType<typeof vi.fn>;
  updateCompleteProfile: ReturnType<typeof vi.fn>;
};

describe("useUserStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    const { clearUser, clearProfile } = useUserStore.getState();
    clearUser();
    clearProfile();
    vi.clearAllMocks();
  });

  describe("initial state", () => {
    it("has correct initial values", () => {
      const state = useUserStore.getState();

      expect(state.user).toBeNull();
      expect(state.completeProfile).toBeNull();
      expect(state.isProfileLoading).toBe(false);
      expect(state.profileError).toBeNull();
      expect(state.isUpdating).toBe(false);
      expect(state.updateError).toBeNull();
    });
  });

  describe("setUser", () => {
    it("sets user state", () => {
      const mockUser = {
        id: "user-123",
        email: "test@example.com",
        full_name: "Test User",
      };

      act(() => {
        useUserStore.getState().setUser(mockUser as never);
      });

      expect(useUserStore.getState().user).toEqual(mockUser);
    });

    it("clears user when set to null", () => {
      // First set a user
      act(() => {
        useUserStore.getState().setUser({ id: "123" } as never);
      });

      // Then clear it
      act(() => {
        useUserStore.getState().setUser(null);
      });

      expect(useUserStore.getState().user).toBeNull();
    });
  });

  describe("setCompleteProfile", () => {
    it("sets complete profile state", () => {
      const mockProfile = {
        id: "user-123",
        email: "test@example.com",
        full_name: "Test User",
        bio: "Test bio",
        theme: "dark",
      };

      act(() => {
        useUserStore.getState().setCompleteProfile(mockProfile as never);
      });

      expect(useUserStore.getState().completeProfile).toEqual(mockProfile);
    });
  });

  describe("setProfileLoading", () => {
    it("sets loading state to true", () => {
      act(() => {
        useUserStore.getState().setProfileLoading(true);
      });

      expect(useUserStore.getState().isProfileLoading).toBe(true);
    });

    it("sets loading state to false", () => {
      act(() => {
        useUserStore.getState().setProfileLoading(true);
        useUserStore.getState().setProfileLoading(false);
      });

      expect(useUserStore.getState().isProfileLoading).toBe(false);
    });
  });

  describe("setProfileError", () => {
    it("sets error message", () => {
      act(() => {
        useUserStore.getState().setProfileError("Failed to load");
      });

      expect(useUserStore.getState().profileError).toBe("Failed to load");
    });

    it("clears error when set to null", () => {
      act(() => {
        useUserStore.getState().setProfileError("Error");
        useUserStore.getState().setProfileError(null);
      });

      expect(useUserStore.getState().profileError).toBeNull();
    });
  });

  describe("fetchCompleteProfile", () => {
    it("fetches and sets profile on success", async () => {
      const mockProfile = {
        id: "user-123",
        email: "test@example.com",
        full_name: "Test User",
        bio: "Test bio",
      };
      mockAuthApi.getCompleteProfile.mockResolvedValue(mockProfile);

      await act(async () => {
        await useUserStore.getState().fetchCompleteProfile();
      });

      const state = useUserStore.getState();
      expect(state.completeProfile).toEqual(mockProfile);
      expect(state.isProfileLoading).toBe(false);
      expect(state.profileError).toBeNull();
    });

    it("handles fetch error", async () => {
      const error = {
        response: {
          data: {
            detail: "Profile not found",
          },
        },
      };
      mockAuthApi.getCompleteProfile.mockRejectedValue(error);

      await act(async () => {
        await useUserStore.getState().fetchCompleteProfile();
      });

      const state = useUserStore.getState();
      expect(state.profileError).toBe("Profile not found");
      expect(state.isProfileLoading).toBe(false);
      expect(state.completeProfile).toBeNull();
    });

    it("uses default error message when detail not available", async () => {
      mockAuthApi.getCompleteProfile.mockRejectedValue(new Error("Network error"));

      await act(async () => {
        await useUserStore.getState().fetchCompleteProfile();
      });

      expect(useUserStore.getState().profileError).toBe("Failed to fetch profile");
    });
  });

  describe("updateCompleteProfile", () => {
    it("updates profile on success", async () => {
      const updateData = { full_name: "New Name", bio: "New bio" };
      const updatedProfile = {
        id: "user-123",
        full_name: "New Name",
        bio: "New bio",
      };
      mockAuthApi.updateCompleteProfile.mockResolvedValue(updatedProfile);

      await act(async () => {
        await useUserStore.getState().updateCompleteProfile(updateData as never);
      });

      const state = useUserStore.getState();
      expect(state.completeProfile).toEqual(updatedProfile);
      expect(state.isUpdating).toBe(false);
      expect(state.updateError).toBeNull();
    });

    it("handles update error and throws", async () => {
      const error = {
        response: {
          data: {
            detail: "Update failed",
          },
        },
      };
      mockAuthApi.updateCompleteProfile.mockRejectedValue(error);

      await expect(
        act(async () => {
          await useUserStore.getState().updateCompleteProfile({} as never);
        })
      ).rejects.toThrow("Update failed");

      const state = useUserStore.getState();
      expect(state.updateError).toBe("Update failed");
      expect(state.isUpdating).toBe(false);
    });
  });

  describe("clearUser", () => {
    it("clears user state", () => {
      // First set a user
      act(() => {
        useUserStore.getState().setUser({ id: "123" } as never);
      });

      // Then clear
      act(() => {
        useUserStore.getState().clearUser();
      });

      expect(useUserStore.getState().user).toBeNull();
    });
  });

  describe("clearProfile", () => {
    it("clears profile related state", () => {
      // Set some state
      act(() => {
        useUserStore.getState().setCompleteProfile({ id: "123" } as never);
        useUserStore.getState().setProfileLoading(true);
        useUserStore.getState().setProfileError("Some error");
      });

      // Clear
      act(() => {
        useUserStore.getState().clearProfile();
      });

      const state = useUserStore.getState();
      expect(state.completeProfile).toBeNull();
      expect(state.isProfileLoading).toBe(false);
      expect(state.profileError).toBeNull();
    });
  });
});
