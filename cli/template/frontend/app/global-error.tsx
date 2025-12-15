"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 dark:bg-gray-900">
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="text-center">
            {/* Critical Error Icon */}
            <div className="mx-auto w-24 h-24 flex items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
              <svg
                className="w-12 h-12 text-red-600 dark:text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            {/* Message */}
            <h2 className="mt-6 text-3xl font-semibold text-gray-900 dark:text-white">
              Critical Error
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400 max-w-md mx-auto">
              A critical error occurred. Please refresh the page or try again
              later.
            </p>

            {/* Error digest */}
            {error.digest && (
              <p className="mt-4 text-sm text-gray-500">
                Error ID:{" "}
                <code className="font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                  {error.digest}
                </code>
              </p>
            )}

            {/* Actions */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={reset}
                className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Try again
              </button>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
