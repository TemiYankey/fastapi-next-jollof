import { CompleteUserProfile, ProfileUpdate, User } from "@/types";
import { api } from "./client";

export interface UpdateProfileRequest {
  firstName: string;
  lastName: string;
  email: string;
}

export interface UpdatePreferencesRequest {
  emailNotifications: boolean;
  marketingEmails: boolean;
}

export interface UserPreferences {
  emailNotifications: boolean;
  marketingEmails: boolean;
}

export const authApi = {
  me: () => api.get<User>("/auth/me"),
  meWithToken: (token: string) => api.getWithToken<User>("/auth/me", token),

  updateBasicProfile: (data: UpdateProfileRequest) =>
    api.put<User>("/auth/me/basic-profile", data),

  getPreferences: () => api.get<UserPreferences>("/auth/me/preferences"),
  updatePreferences: (data: UpdatePreferencesRequest) =>
    api.put<{ success: boolean }>("/auth/me/preferences", data),

  deleteAccount: () =>
    api.delete<{ success: boolean }>("/auth/me/delete-account"),

  // Complete profile endpoints
  getCompleteProfile: () => api.get<CompleteUserProfile>("/auth/me/profile"),
  updateCompleteProfile: (data: ProfileUpdate) =>
    api.put<CompleteUserProfile>("/auth/me/profile", data),
};
