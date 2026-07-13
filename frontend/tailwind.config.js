/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // All values resolve to design tokens — see src/shared/design-system/tokens.css
        canvas: "var(--bg-canvas)",
        surface: "var(--bg-surface)",
        "surface-raised": "var(--bg-surface-raised)",
        hairline: "var(--border)",
        ink: "var(--text-primary)",
        muted: "var(--text-secondary)",
        accent: "var(--accent)",
        "risk-high": "var(--risk-high)",
        "risk-medium": "var(--risk-medium)",
        "risk-low": "var(--risk-low)",
        "confidence-direct": "var(--confidence-direct)",
        "confidence-inferred": "var(--confidence-inferred)",
        "node-program": "var(--node-program)",
        "node-table": "var(--node-table)",
        "node-function-module": "var(--node-function-module)",
        "node-badi": "var(--node-badi)",
        "node-job": "var(--node-job)",
        "node-transport": "var(--node-transport)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
