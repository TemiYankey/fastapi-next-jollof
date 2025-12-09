import { config } from "@/lib/config";
import { supabase } from "@/lib/supabase";
import { APIError } from "@/types";
import logger from "@/utils/logger";
import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: APIError
  ) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiClient {
  private axiosInstance: AxiosInstance;
  private isLoggingOut = false;

  constructor(baseURL: string) {
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 90000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.setupRequestInterceptor();
    this.setupResponseInterceptor();
  }

  private setupRequestInterceptor() {
    this.axiosInstance.interceptors.request.use(
      async (config: InternalAxiosRequestConfig) => {
        if (typeof window !== "undefined") {
          if (!config.headers.Authorization) {
            try {
              const {
                data: { session },
              } = await supabase.auth.getSession();

              if (session?.access_token) {
                config.headers.Authorization = `Bearer ${session.access_token}`;
              }
            } catch (err) {
              logger.warn("Supabase session error:", err);
            }
          }
        }

        if (config.data instanceof FormData) {
          delete config.headers["Content-Type"];
        }

        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  private setupResponseInterceptor() {
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (
          error.response?.status === 401 ||
          error.response?.status === 403
        ) {
          await this.handleAuthError();
        }

        const errorData = error.response?.data as APIError;
        throw new ApiError(
          errorData?.detail || error.message || `HTTP ${error.response?.status}`,
          error.response?.status || 500,
          errorData
        );
      }
    );
  }

  private async handleAuthError(): Promise<void> {
    if (this.isLoggingOut) return;
    this.isLoggingOut = true;

    if (typeof window !== "undefined") {
      try {
        const { robustLogout } = await import("@/utils/robustLogout");
        await robustLogout();

        const { toast } = await import("sonner");
        toast.error("Session expired", {
          description: "You have been signed out. Please sign in again.",
        });
      } catch (error) {
        logger.error("Error during automatic logout:", error);
      } finally {
        this.isLoggingOut = false;
      }
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await this.axiosInstance.get<T>(endpoint);
    return response.data;
  }

  async getWithToken<T>(endpoint: string, token: string): Promise<T> {
    const response = await this.axiosInstance.get<T>(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.axiosInstance.post<T>(endpoint, data);
    return response.data;
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.axiosInstance.put<T>(endpoint, data);
    return response.data;
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.axiosInstance.patch<T>(endpoint, data);
    return response.data;
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.axiosInstance.delete<T>(endpoint);
    return response.data;
  }
}

export const api = new ApiClient(config.apiUrl);
