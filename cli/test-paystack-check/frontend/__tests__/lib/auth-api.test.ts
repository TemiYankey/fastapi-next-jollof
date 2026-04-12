import { beforeEach, describe, expect, it, vi } from "vitest";

// Create mock inside vi.mock factory
vi.mock("@/utils/api/client", () => ({
  api: {
    get: vi.fn(),
    getWithToken: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(
      message: string,
      public status: number,
      public response?: unknown
    ) {
      super(message);
      this.name = "ApiError";
    }
  },
}));

// Import after mocks
import { authApi } from "@/utils/api/auth";
import { api } from "@/utils/api/client";

// Type the mocked api
const mockApi = api as {
  get: ReturnType<typeof vi.fn>;
  getWithToken: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  put: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

describe("authApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("me", () => {
    it("calls GET /auth/me", async () => {
      const mockUser = {
        id: "user-123",
        email: "test@example.com",
        full_name: "Test User",
      };
      mockApi.get.mockResolvedValue(mockUser);

      const result = await authApi.me();

      expect(mockApi.get).toHaveBeenCalledWith("/auth/me");
      expect(result).toEqual(mockUser);
    });

    it("propagates errors", async () => {
      mockApi.get.mockRejectedValue(new Error("Unauthorized"));

      await expect(authApi.me()).rejects.toThrow("Unauthorized");
    });
  });

  describe("meWithToken", () => {
    it("calls GET /auth/me with token", async () => {
      const mockUser = {
        id: "user-123",
        email: "test@example.com",
      };
      const token = "test-token-abc";
      mockApi.getWithToken.mockResolvedValue(mockUser);

      const result = await authApi.meWithToken(token);

      expect(mockApi.getWithToken).toHaveBeenCalledWith("/auth/me", token);
      expect(result).toEqual(mockUser);
    });
  });

  describe("updateBasicProfile", () => {
    it("calls PUT /auth/me/basic-profile", async () => {
      const profileData = {
        firstName: "John",
        lastName: "Doe",
        email: "john@example.com",
      };
      const mockResponse = {
        id: "user-123",
        email: "john@example.com",
        full_name: "John Doe",
      };
      mockApi.put.mockResolvedValue(mockResponse);

      const result = await authApi.updateBasicProfile(profileData);

      expect(mockApi.put).toHaveBeenCalledWith(
        "/auth/me/basic-profile",
        profileData
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe("getPreferences", () => {
    it("calls GET /auth/me/preferences", async () => {
      const mockPreferences = {
        emailNotifications: true,
        marketingEmails: false,
      };
      mockApi.get.mockResolvedValue(mockPreferences);

      const result = await authApi.getPreferences();

      expect(mockApi.get).toHaveBeenCalledWith("/auth/me/preferences");
      expect(result).toEqual(mockPreferences);
    });
  });

  describe("updatePreferences", () => {
    it("calls PUT /auth/me/preferences", async () => {
      const preferencesData = {
        emailNotifications: false,
        marketingEmails: true,
      };
      const mockResponse = { success: true };
      mockApi.put.mockResolvedValue(mockResponse);

      const result = await authApi.updatePreferences(preferencesData);

      expect(mockApi.put).toHaveBeenCalledWith(
        "/auth/me/preferences",
        preferencesData
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe("deleteAccount", () => {
    it("calls DELETE /auth/me/delete-account", async () => {
      const mockResponse = { success: true };
      mockApi.delete.mockResolvedValue(mockResponse);

      const result = await authApi.deleteAccount();

      expect(mockApi.delete).toHaveBeenCalledWith("/auth/me/delete-account");
      expect(result).toEqual(mockResponse);
    });
  });

  describe("getCompleteProfile", () => {
    it("calls GET /auth/me/profile", async () => {
      const mockProfile = {
        id: "user-123",
        email: "test@example.com",
        full_name: "Test User",
        bio: "Test bio",
        phone: "+1234567890",
        location: "Lagos",
        theme: "dark",
      };
      mockApi.get.mockResolvedValue(mockProfile);

      const result = await authApi.getCompleteProfile();

      expect(mockApi.get).toHaveBeenCalledWith("/auth/me/profile");
      expect(result).toEqual(mockProfile);
    });
  });

  describe("updateCompleteProfile", () => {
    it("calls PUT /auth/me/profile", async () => {
      const profileUpdate = {
        full_name: "Updated Name",
        bio: "New bio",
        theme: "light",
      };
      const mockResponse = {
        id: "user-123",
        full_name: "Updated Name",
        bio: "New bio",
        theme: "light",
      };
      mockApi.put.mockResolvedValue(mockResponse);

      const result = await authApi.updateCompleteProfile(profileUpdate);

      expect(mockApi.put).toHaveBeenCalledWith("/auth/me/profile", profileUpdate);
      expect(result).toEqual(mockResponse);
    });

    it("handles validation errors", async () => {
      const invalidData = { theme: "invalid-theme" };
      mockApi.put.mockRejectedValue(
        new Error("Validation Error: Invalid theme")
      );

      await expect(authApi.updateCompleteProfile(invalidData)).rejects.toThrow(
        "Validation Error"
      );
    });
  });
});
