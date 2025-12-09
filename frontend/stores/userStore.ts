/**
 * User store for managing user state.
 */

import { CompleteUserProfile, ProfileUpdate, User } from "@/types";
import { authApi } from "@/utils/api/auth";
import { create } from "zustand";

interface UserState {
  user: User | null;
  completeProfile: CompleteUserProfile | null;
  isProfileLoading: boolean;
  profileError: string | null;
  isUpdating: boolean;
  updateError: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setCompleteProfile: (profile: CompleteUserProfile | null) => void;
  setProfileLoading: (loading: boolean) => void;
  setProfileError: (error: string | null) => void;
  fetchCompleteProfile: () => Promise<void>;
  updateCompleteProfile: (data: ProfileUpdate) => Promise<void>;
  clearProfile: () => void;
  clearUser: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  completeProfile: null,
  isProfileLoading: false,
  profileError: null,
  isUpdating: false,
  updateError: null,

  setUser: (user) => set({ user }),
  setCompleteProfile: (profile) => set({ completeProfile: profile }),
  setProfileLoading: (loading) => set({ isProfileLoading: loading }),
  setProfileError: (error) => set({ profileError: error }),

  fetchCompleteProfile: async () => {
    set({ isProfileLoading: true, profileError: null });

    try {
      const response = await authApi.getCompleteProfile();
      set({
        completeProfile: response,
        isProfileLoading: false,
      });
    } catch (error: unknown) {
      console.error("Error fetching complete profile:", error);
      const errorMessage =
        error && typeof error === "object" && "response" in error
          ? (
              error as {
                response?: { data?: { detail?: string } };
              }
            ).response?.data?.detail || "Failed to fetch profile"
          : "Failed to fetch profile";
      set({
        profileError: errorMessage,
        isProfileLoading: false,
      });
    }
  },

  updateCompleteProfile: async (data: ProfileUpdate) => {
    set({ isUpdating: true, updateError: null });

    try {
      const response = await authApi.updateCompleteProfile(data);
      set({
        completeProfile: response,
        isUpdating: false,
      });
    } catch (error: unknown) {
      console.error("Error updating profile:", error);
      const errorMessage =
        error && typeof error === "object" && "response" in error
          ? (
              error as {
                response?: { data?: { detail?: string } };
              }
            ).response?.data?.detail || "Failed to update profile"
          : "Failed to update profile";
      set({
        updateError: errorMessage,
        isUpdating: false,
      });
      throw new Error(errorMessage);
    }
  },

  clearUser: () => set({ user: null }, false),

  clearProfile: () =>
    set({
      completeProfile: null,
      isProfileLoading: false,
      profileError: null,
    }),
}));
