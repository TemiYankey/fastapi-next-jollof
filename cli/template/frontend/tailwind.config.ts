import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";

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
        // Brand colors - CLI will replace 'colors.indigo' with selected theme
        primary: colors.indigo,
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
