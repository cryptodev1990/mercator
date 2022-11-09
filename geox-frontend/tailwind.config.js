const plugin = require("tailwindcss/plugin");

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  daisyui: {
    themes: ["corporate"],
  },
  theme: {
    fontFamily: {
      sans: ["Roboto", "sans-serif"],
    },
    extend: {
      screens: {
        "tall-h": { raw: "(min-height: 500px)" },
        "md-h": { raw: "(min-height: 400px)" },
        "short-h": { raw: "(min-height: 300px)" },
      },
      colors: {
        "baby-blue": "#E7F2F8",
        primary: "#E7F2F8",
        aquamarine: "#74BDCB",
        secondary: "#74BDCB",
        salmon: "#FFA384",
        tertiary: "#FFA384",
        freesia: "#EFE7BC",
        quartiary: "#EFE7BC",
      },
      animation: {
        text: "text 5s ease infinite",
        bg: "background 5s ease infinite",
      },
      keyframes: {
        text: {
          "0%, 100%": {
            "background-size": "200% 200%",
            "background-position": "left center",
          },
          "50%": {
            "background-size": "200% 200%",
            "background-position": "right center",
          },
        },
      },
    },
  },
  plugins: [
    require("daisyui"),
    require("tailwind-scrollbar"),
    plugin(function ({ addUtilities }) {
      const newUtilities = {
        ".text-animation": {
          animation: "text 5s ease infinite",
        },
        ".no-scrollbar::-webkit-scrollbar": {
          display: "none",
        },
        ".no-scrollbar": {
          "-ms-overflow-style": "none",
          "scrollbar-width": "none",
        },
      };
      addUtilities(newUtilities);
    }),
  ],
};
