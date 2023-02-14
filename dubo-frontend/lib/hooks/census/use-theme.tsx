import { createContext, useContext, useState } from "react";
import { MdOutlineSatellite } from "react-icons/md";
import { BsFillMoonFill } from "react-icons/bs";
import { BiSun } from "react-icons/bi";

// add no labels
export const LIGHT = {
  theme: "light",
  baseMap: "mapbox://styles/mapbox/light-v10",
  icon: <BiSun />,
  fontColor: "text-slate-900",
  secondaryFontColor: "text-slate-100",
  bgColor: "bg-slate-100",
  secondaryBgColor: "bg-slate-500",
  borderColor: "border-slate-500",
};

const LIGHT_NO_LABELS = {
  ...LIGHT,
  theme: "light_no_labels",
  baseMap:
    "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json",
};

const EARTH = {
  theme: "earth",
  baseMap: "mapbox://styles/mapbox/satellite-streets-v11",
  icon: <MdOutlineSatellite />,
  fontColor: "text-slate-100",
  secondaryFontColor: "text-slate-100",
  bgColor: "bg-slate-700",
  secondaryBgColor: "bg-slate-900",
  borderColor: "border-slate-900",
};

const EARTH_NO_LABELS = {
  ...EARTH,
  theme: "earth_no_labels",
  baseMap: "mapbox://styles/mapbox/satellite-v9",
};

const MOON = {
  theme: "moon",
  baseMap: "mapbox://styles/mapbox/dark-v10",
  icon: <BsFillMoonFill />,
  fontColor: "text-neutral-100",
  bgColor: "bg-neutral-600",
  secondaryFontColor: "text-slate-100",
  secondaryBgColor: "bg-neutral-700",
  borderColor: "border-neutral-700",
};

const MOON_NO_LABELS = {
  ...MOON,
  theme: "moon_no_labels",
  baseMap:
    "https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json",
};

type Theme =
  | typeof LIGHT
  | typeof EARTH
  | typeof MOON
  | typeof LIGHT_NO_LABELS
  | typeof EARTH_NO_LABELS
  | typeof MOON_NO_LABELS;

const THEMES = [
  LIGHT,
  EARTH,
  MOON,
  LIGHT_NO_LABELS,
  EARTH_NO_LABELS,
  MOON_NO_LABELS,
];

const ThemeContext = createContext({
  theme: EARTH,
  nextTheme: MOON,
  toggleTheme: () => {},
});

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<Theme>(EARTH);
  const [themeIdx, setThemeIdx] = useState(0);

  // let us preview the next theme
  const [nextTheme, setNextTheme] = useState<Theme>(MOON);
  const [nextThemeIdx, setNextThemeIdx] = useState(1);

  const toggleTheme = () => {
    const newIdx = (themeIdx + 1) % THEMES.length;
    const newTheme = THEMES[newIdx];
    setThemeIdx((idx) => newIdx);
    setTheme(newTheme);

    /* This really exists just to make the animation in the toggle button work */
    const newNextIdx = (nextThemeIdx + 1) % THEMES.length;
    const newNextTheme = THEMES[newNextIdx];
    setNextThemeIdx((idx) => newNextIdx);
    setNextTheme(newNextTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, nextTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const { theme, toggleTheme, nextTheme } = useContext(ThemeContext);
  return {
    theme,
    toggleTheme,
    nextTheme,
  };
};
