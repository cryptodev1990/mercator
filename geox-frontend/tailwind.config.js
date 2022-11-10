const plugin = require("tailwindcss/plugin");

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  daisyui: {
    themes: [
      {
        geox: {
          primary: "#2D2D2D",
          secondary: "#D926A9",
          accent: "#1FB2A6",
          neutral: "#191D24",
          "base-100": "#2A303C",
          info: "#3ABFF8",
          success: "#36D399",
          warning: "#FBBD23",
          error: "#F87272",
        },
      },
    ],
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
