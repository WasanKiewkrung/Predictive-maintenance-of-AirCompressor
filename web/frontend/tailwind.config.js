/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#135bec",
        "primary-dark": "#0c3b9e",
        "primary-light": "#e0e7ff",
        secondary: "#324467",
        "background-light": "#f8fafc",
        "surface-light": "#ffffff",
        "text-main": "#1e293b",
        "text-muted": "#64748b",
        "border-light": "#e2e8f0",
        success: "#10b981",
        "success-bg": "#ecfdf5",
        warning: "#f59e0b",
        "warning-bg": "#fffbeb",
        danger: "#ef4444",
      },
      fontFamily: {
        display: ["Inter", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        soft: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
        glow: "0 0 15px rgba(19, 91, 236, 0.15)",
      }
    },
  },
  plugins: [],
}