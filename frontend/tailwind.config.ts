import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./contexts/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dynamic colors using CSS variables
        background: "var(--background)",
        foreground: {
          DEFAULT: "var(--foreground)",
          primary: "var(--foreground-primary)",
          secondary: "var(--foreground-secondary)",
          tertiary: "var(--foreground-tertiary)",
          muted: "var(--foreground-muted)",
        },
        border: "var(--border)",
        muted: "var(--muted)",
        alternate: "var(--alternate)",
        // Brand colors - customize these
        primary: {
          DEFAULT: "var(--primary)",
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
