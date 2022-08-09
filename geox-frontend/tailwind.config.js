const plugin = require("tailwindcss/plugin");

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
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
