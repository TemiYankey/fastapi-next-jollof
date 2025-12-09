"use client";

import { config } from "@/lib/config";

interface LoadingScreenProps {
  message?: string;
}

export function LoadingScreen({ message }: LoadingScreenProps) {
  return (
    <div className="fixed inset-0 bg-background z-50 flex flex-col items-center justify-center">
      <div className="w-8 h-8 border-2 border-border border-t-primary-600 rounded-full animate-spin mb-4"></div>
      <p className="text-foreground-tertiary text-sm">
        {message || `Loading ${config.appName}...`}
      </p>
    </div>
  );
}
