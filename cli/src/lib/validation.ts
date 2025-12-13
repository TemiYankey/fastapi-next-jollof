/**
 * Input validation functions.
 */

/**
 * Validate a project name.
 * @param name - The project name to validate
 * @returns Error message if invalid, undefined if valid
 */
export function validateProjectName(name: string): string | undefined {
  if (!name || name.trim().length === 0) {
    return "Project name is required";
  }
  if (!/^[a-z0-9-]+$/.test(name)) {
    return "Project name can only contain lowercase letters, numbers, and hyphens";
  }
  if (name.startsWith("-") || name.endsWith("-")) {
    return "Project name cannot start or end with a hyphen";
  }
  return undefined;
}

/**
 * Validate a port number.
 * @param value - The port value to validate (as string)
 * @returns Error message if invalid, undefined if valid
 */
export function validatePort(value: string): string | undefined {
  // Must be a pure integer (no decimals, no trailing text)
  if (!/^\d+$/.test(value)) {
    return "Port must be between 1024 and 65535";
  }
  const port = parseInt(value, 10);
  if (isNaN(port) || port < 1024 || port > 65535) {
    return "Port must be between 1024 and 65535";
  }
  return undefined;
}

/**
 * Validate an app name.
 * @param value - The app name to validate
 * @returns Error message if invalid, undefined if valid
 */
export function validateAppName(value: string): string | undefined {
  if (!value || value.trim().length === 0) {
    return "App name is required";
  }
  return undefined;
}
