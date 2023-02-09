/** @type {import('tailwindcss').Config} */
const { fontFamily } = require("tailwindcss/defaultTheme");

module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
    "./node_modules/tw-elements/dist/js/**/*.js",
  ],
  theme: {
    // Add a blue color
    extend: {
      padding: {
        "1/3": "33%",
        "1/2": "50%",
        "1/4": "25%",
        "5/12": "41.666667%",
        "11/24": "45.833333%",
        full: "100%",
      },
      fontFamily: {
        primary: ["var(--roboto-font)", ...fontFamily.sans],
        sans: ["var(--roboto-font)", ...fontFamily.sans],
        sans2: [fontFamily.sans[1]],
      },
      // that is animation class
      animation: {
        fadeIn100: "fadeIn 100ms ease-in",
        fadeIn500: "fadeIn 500ms ease-in",
        fadeOut100: "fadeOut 100ms ease-in",
        fadeOut500: "fadeOut 500ms ease-in",
        slideOut200: "slideOut 200ms ease-out",
        slideOut500: "slideOut 500ms ease-in",
        slideIn500: "slideIn 500ms ease-in",
        moveThroughRainbow2s: "moveThroughRainbow 2s ease-in-out infinite",
        pushUpOnce: "pushUpOnce 3000ms ease-in-out 1",
      },
      // that is actual animation
      keyframes: (theme) => ({
        fadeIn: {
          "0%": { opacity: "0%" },
          "100%": { opacity: "100%" },
        },
        fadeOut: {
          "0%": { opacity: "100%" },
          "100%": { opacity: "0%" },
        },
        pushUpOnce: {
          "0%": { transform: "translateY(0)" },
          "30%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(-100%)" },
        },
        moveThroughRainbow: {
          "0%": { color: theme("colors.cxRed") },
          "10%": { color: theme("colors.cxOrange") },
          "20%": { color: theme("colors.cxYellow") },
          "30%": { color: theme("colors.cxGreen") },
          "40%": { color: theme("colors.cxBlue") },
          "50%": { color: theme("colors.cxIndigo") },
          "60%": { color: theme("colors.cxViolet") },
          "70%": { color: theme("colors.cxRed") },
          "80%": { color: theme("colors.cxOrange") },
          "90%": { color: theme("colors.cxYellow") },
          "100%": { color: theme("colors.cxGreen") },
        },
        slideOut: {
          "0%": { transform: "translateY(0)" },
          "100%": {
            transform: "translateY(-100%)",
            display: "none",
            opacity: "0%",
          },
        },
        slideIn: {
          "100%": {
            transform: "translateY(0)",
            opacity: "100%",
          },
          "0%": {
            transform: "translateY(-100%)",
          },
        },
      }),
      colors: {
        spBlue: "#0070f3",
        spBlueDark: "#005bd9",
        spBlueLight: "#679eff",
        cxRed: "#ff0000",
        cxOrange: "#ff7f00",
        cxYellow: "#ffff00",
        cxGreen: "#00ff00",
        cxBlue: "#0000ff",
        cxIndigo: "#4b0082",
        cxViolet: "#ee82ee",
      },
    },
  },
  plugins: [require("tw-elements/dist/plugin")],
};
