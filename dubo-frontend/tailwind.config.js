/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    // Add a blue color
    extend: {
      // that is animation class
      animation: {
        fadeIn: "fadeIn 0.1s ease-in",
        fadeInSlow: "fadeIn 0.5s ease-in",
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
        periwinkle: "#7289da",
      },
    },
  },
  plugins: [],
};
