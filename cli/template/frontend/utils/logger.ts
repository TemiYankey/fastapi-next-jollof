/**
 * Simple logging utility for the frontend.
 * In production, this could be replaced with a proper logging service.
 */

const isDev = process.env.NODE_ENV === "development";

const logger = {
  info: (...args: unknown[]) => {
    if (isDev) console.info("[INFO]", ...args);
  },
  warn: (...args: unknown[]) => {
    console.warn("[WARN]", ...args);
  },
  error: (...args: unknown[]) => {
    console.error("[ERROR]", ...args);
  },
  debug: (...args: unknown[]) => {
    if (isDev) console.debug("[DEBUG]", ...args);
  },
};

export default logger;
