/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        abyss: {
          0: "rgb(var(--abyss-0-rgb) / <alpha-value>)",
          1: "rgb(var(--abyss-1-rgb) / <alpha-value>)",
          2: "rgb(var(--abyss-2-rgb) / <alpha-value>)",
          3: "rgb(var(--abyss-3-rgb) / <alpha-value>)",
          4: "rgb(var(--abyss-4-rgb) / <alpha-value>)",
          5: "rgb(var(--abyss-5-rgb) / <alpha-value>)",
        },
        thermo: "rgb(var(--thermo-rgb) / <alpha-value>)",
        "thermo-bright": "rgb(var(--thermo-bright-rgb) / <alpha-value>)",
        "thermo-dim": "rgb(var(--thermo-dim-rgb) / <alpha-value>)",
        surface: "rgb(var(--sea-surface-rgb) / <alpha-value>)",
        "surface-warm": "rgb(var(--surface-warm-rgb) / <alpha-value>)",
        "surface-warm-deep": "rgb(var(--surface-warm-deep-rgb) / <alpha-value>)",
        marine: "rgb(var(--marine-rgb) / <alpha-value>)",
        ink: "rgb(var(--ink-rgb) / <alpha-value>)",
        "ink-dim": "rgb(var(--ink-dim-rgb) / <alpha-value>)",
        "ink-faint": "rgb(var(--ink-faint-rgb) / <alpha-value>)",
        reply: "rgb(var(--reply-rgb) / <alpha-value>)",
        verified: "rgb(var(--verified-rgb) / <alpha-value>)",
        refusal: "rgb(var(--refusal-rgb) / <alpha-value>)",
        hold: "rgb(var(--hold-rgb) / <alpha-value>)",
        tick: "rgb(var(--ruler-tick-rgb) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        digits: ["IBM Plex Mono", "monospace"],
      },
      boxShadow: {
        "glass-glow": "0 12px 40px -14px var(--glass-shadow)",
      },
      backgroundImage: {
        brand: "linear-gradient(135deg, #8b7cf6 0%, #5f4fe0 100%)",
      },
    },
  },
  plugins: [],
};
