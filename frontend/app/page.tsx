import { config } from "@/lib/config";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center max-w-2xl">
        <h1 className="text-4xl font-bold text-foreground-primary mb-4">
          Welcome to {config.appName}
        </h1>
        <p className="text-lg text-foreground-tertiary mb-8">
          A production-ready FastAPI + Next.js boilerplate with Supabase authentication.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/auth/signin"
            className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Sign In
          </Link>
          <Link
            href="/auth/signup"
            className="px-6 py-3 border border-border text-foreground-primary rounded-lg font-medium hover:bg-muted transition-colors"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  );
}
