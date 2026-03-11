/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        tcm: {
          bg: "var(--tcm-bg)",
          card: "var(--tcm-card)",
          ink: "var(--tcm-ink)",
          subtle: "var(--tcm-subtle)",
          line: "var(--tcm-line)",
          brand: "var(--tcm-brand)",
          brandDeep: "var(--tcm-brand-deep)",
          warn: "var(--tcm-warn)",
          paper: "var(--tcm-paper)",
          wood: "var(--tcm-wood)",
          cinnabar: "var(--tcm-cinnabar)",
          inkStone: "var(--tcm-ink-stone)",
          gold: "var(--tcm-gold)",
          purple: "var(--tcm-purple)",
          blue: "var(--tcm-blue)",
          green: "var(--tcm-green)",
        },
      },
    },
  },
  plugins: [],
}
