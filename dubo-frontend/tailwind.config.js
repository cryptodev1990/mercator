/** @type {import('tailwindcss').Config} */
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
      // that is animation class
      animation: {
        fadeIn100: "fadeIn 100ms ease-in",
        fadeIn500: "fadeIn 500ms ease-in",
      },
      // that is actual animation
      keyframes: (theme) => ({
        fadeIn: {
          "0%": { opacity: "0%" },
          "100%": { opacity: "100%" },
        },
      }),
      colors: {
        spBlue: "#0070f3",
        spBlueDark: "#005bd9",
        spBlueLight: "#679eff",
      },
    },
  },
  plugins: [require("tw-elements/dist/plugin")],
};
