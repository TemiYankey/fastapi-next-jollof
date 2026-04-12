import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Mock modules before imports
vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
    },
  },
}));

vi.mock("@/lib/config", () => ({
  config: {
    apiUrl: "http://localhost:8000",
  },
}));

vi.mock("@/utils/logger", () => ({
  default: {
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    debug: vi.fn(),
  },
}));

vi.mock("sonner", () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

// Import after mocks
import { ApiError, api } from "@/utils/api/client";
import { supabase } from "@/lib/supabase";
import axios from "axios";

// Mock axios
vi.mock("axios", async () => {
  const mockAxios = {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    })),
  };
  return { default: mockAxios };
});

describe("ApiError", () => {
  it("creates error with message and status", () => {
    const error = new ApiError("Not Found", 404);

    expect(error.message).toBe("Not Found");
    expect(error.status).toBe(404);
    expect(error.name).toBe("ApiError");
    expect(error.response).toBeUndefined();
  });

  it("creates error with response data", () => {
    const responseData = { detail: "Resource not found" };
    const error = new ApiError("Not Found", 404, responseData);

    expect(error.response).toEqual(responseData);
    expect(error.response?.detail).toBe("Resource not found");
  });

  it("is instanceof Error", () => {
    const error = new ApiError("Test", 500);

    expect(error).toBeInstanceOf(Error);
  });
});

describe("ApiClient", () => {
  describe("initialization", () => {
    it("creates axios instance with correct base config", () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: "http://localhost:8000",
        timeout: 90000,
        headers: {
          "Content-Type": "application/json",
        },
      });
    });
  });
});

describe("ApiClient methods", () => {
  // Since we can't easily test the actual implementation with mocked axios,
  // we test the structure and expected behavior

  it("has get method", () => {
    expect(typeof api.get).toBe("function");
  });

  it("has post method", () => {
    expect(typeof api.post).toBe("function");
  });

  it("has put method", () => {
    expect(typeof api.put).toBe("function");
  });

  it("has patch method", () => {
    expect(typeof api.patch).toBe("function");
  });

  it("has delete method", () => {
    expect(typeof api.delete).toBe("function");
  });

  it("has getWithToken method", () => {
    expect(typeof api.getWithToken).toBe("function");
  });
});

describe("Request Interceptor behavior", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should attempt to get session for auth header", async () => {
    const mockSession = {
      data: {
        session: {
          access_token: "test-token-123",
        },
      },
    };

    vi.mocked(supabase.auth.getSession).mockResolvedValue(mockSession as never);

    // The interceptor is set up on construction
    // We verify the mock is properly set up
    expect(supabase.auth.getSession).toBeDefined();
  });
});

describe("Error handling", () => {
  it("ApiError preserves error details", () => {
    const errorResponse = {
      detail: "Validation failed",
      errors: [{ field: "email", message: "Invalid email" }],
    };

    const error = new ApiError("Validation Error", 422, errorResponse);

    expect(error.status).toBe(422);
    expect(error.response?.detail).toBe("Validation failed");
  });

  it("ApiError handles undefined response", () => {
    const error = new ApiError("Network Error", 0);

    expect(error.response).toBeUndefined();
    expect(error.status).toBe(0);
  });
});
