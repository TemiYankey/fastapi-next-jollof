import { toast as sonnerToast, ExternalToast } from "sonner";

type ToastOptions = Omit<ExternalToast, "id">;

/**
 * Toast utility wrapper for sonner
 * Provides a consistent API for showing notifications
 */
export const toast = {
  /**
   * Show a success toast
   */
  success: (message: string, options?: ToastOptions) => {
    return sonnerToast.success(message, options);
  },

  /**
   * Show an error toast
   */
  error: (message: string, options?: ToastOptions) => {
    return sonnerToast.error(message, options);
  },

  /**
   * Show a warning toast
   */
  warning: (message: string, options?: ToastOptions) => {
    return sonnerToast.warning(message, options);
  },

  /**
   * Show an info toast
   */
  info: (message: string, options?: ToastOptions) => {
    return sonnerToast.info(message, options);
  },

  /**
   * Show a loading toast that can be updated
   * Returns an ID that can be used to update/dismiss
   */
  loading: (message: string, options?: ToastOptions) => {
    return sonnerToast.loading(message, options);
  },

  /**
   * Show a promise toast that updates based on promise state
   */
  promise: <T>(
    promise: Promise<T>,
    {
      loading,
      success,
      error,
    }: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((err: unknown) => string);
    },
    options?: ToastOptions
  ) => {
    return sonnerToast.promise(promise, { loading, success, error }, options);
  },

  /**
   * Dismiss a specific toast by ID or all toasts
   */
  dismiss: (toastId?: string | number) => {
    return sonnerToast.dismiss(toastId);
  },

  /**
   * Show a custom toast (just renders the message)
   */
  custom: (message: string, options?: ToastOptions) => {
    return sonnerToast(message, options);
  },
};

/**
 * Show success toast for common actions
 */
export const showSuccess = {
  saved: (item = "Changes") =>
    toast.success(`${item} saved successfully`),

  created: (item: string) =>
    toast.success(`${item} created successfully`),

  deleted: (item: string) =>
    toast.success(`${item} deleted successfully`),

  updated: (item: string) =>
    toast.success(`${item} updated successfully`),

  copied: (item = "Content") =>
    toast.success(`${item} copied to clipboard`),
};

/**
 * Show error toast for common scenarios
 */
export const showError = {
  generic: (description?: string) =>
    toast.error("Something went wrong", { description }),

  network: () =>
    toast.error("Network error", {
      description: "Please check your connection and try again",
    }),

  unauthorized: () =>
    toast.error("Unauthorized", {
      description: "Please sign in to continue",
    }),

  notFound: (item: string) =>
    toast.error(`${item} not found`),

  validation: (message: string) =>
    toast.error("Validation error", { description: message }),
};

export default toast;
