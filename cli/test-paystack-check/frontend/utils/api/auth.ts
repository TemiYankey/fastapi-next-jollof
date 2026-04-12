import { CompleteUserProfile, ProfileUpdate, User } from "@/types";
import { api } from "./client";

export const authApi = {
  me: () => api.get<User>("/me"),
  meWithToken: (token: string) => api.getWithToken<User>("/me", token),

  // Profile endpoints
  getProfile: () => api.get<CompleteUserProfile>("/me/profile"),
  updateProfile: (data: ProfileUpdate) =>
    api.put<CompleteUserProfile>("/me/profile", data),

  // Dashboard
  getDashboard: () => api.get("/me/dashboard"),

  // Account management
  deleteAccount: () => api.delete<{ success: boolean }>("/me/account"),
};
