/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0f172a",    // slate-900
        secondary: "#1e3a8a",  // blue-900
        accent: "#ca8a04",     // yellow-600
        background: "#f8fafc", // slate-50
        text: "#020617",       // slate-950
      },
      fontFamily: {
        sans: ["Fira Sans", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      }
    },
  },
  plugins: [],
}
