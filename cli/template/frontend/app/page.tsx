import { config } from "@/lib/config";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 bg-gradient-to-b from-background to-muted">
      <div className="text-center max-w-2xl">
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium mb-6">
          Ready to ship
        </div>
        <h1 className="text-5xl font-bold text-foreground-primary mb-4 tracking-tight">
          Welcome to{" "}
          <span className="text-primary-600 dark:text-primary-400">{config.appName}</span>
        </h1>
        <p className="text-lg text-foreground-tertiary mb-8 leading-relaxed">
          A production-ready FastAPI + Next.js boilerplate with Supabase
          authentication, payments, and email built-in.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/auth/signin"
            className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors shadow-lg shadow-primary-500/25"
          >
            Sign In
          </Link>
          <Link
            href="/auth/signup"
            className="px-6 py-3 border border-primary-500 text-primary-600 dark:text-primary-400 rounded-xl font-medium hover:bg-primary-50 dark:hover:bg-primary-950 transition-colors"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  );
}
