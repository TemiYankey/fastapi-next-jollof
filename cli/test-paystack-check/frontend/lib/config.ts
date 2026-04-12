/**
 * Central configuration for the frontend application.
 * All environment variables are accessed through this module.
 */

export const config = {
  // App
  appName: process.env.NEXT_PUBLIC_APP_NAME || "Jollof App",

  // Supabase (placeholder values allow build without env vars)
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co",
  supabaseKey: process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || "placeholder-key",

  // Backend API
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
};
