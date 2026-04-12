/**
 * Centralized Supabase client configuration
 * Single source of truth for Supabase initialization
 */

import { createBrowserClient } from "@supabase/ssr";
import { config } from "./config";

// Create the Supabase client
export const supabase = createBrowserClient(config.supabaseUrl, config.supabaseKey);

// Export types for convenience
export type { User } from "@supabase/supabase-js";
