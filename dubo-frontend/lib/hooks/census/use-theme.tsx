import { createContext, useContext, useState } from "react";
import { MdOutlineSatellite } from "react-icons/md";
import { BsFillMoonFill } from "react-icons/bs";
import { BiSun } from "react-icons/bi";

// add no labels
export const LIGHT = {
  theme: "light",
  baseMap:
    "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json",
  icon: <BiSun />,
  fontColor: "text-slate-900",
  secondaryFontColor: "text-slate-100",
  bgColor: "bg-slate-100",
  secondaryBgColor: "bg-slate-500",
  borderColor: "border-slate-500",
};

const EARTH = {
  theme: "earth",
  baseMap: "mapbox://styles/mapbox/satellite-v9",
  icon: <MdOutlineSatellite />,
  fontColor: "text-slate-100",
  secondaryFontColor: "text-slate-100",
  bgColor: "bg-slate-700",
  secondaryBgColor: "bg-slate-900",
  borderColor: "border-slate-900",
};

const MOON = {
  theme: "moon",
  baseMap:
    "https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json",
  icon: <BsFillMoonFill />,
  fontColor: "text-neutral-100",
  bgColor: "bg-neutral-600",
  secondaryFontColor: "text-slate-100",
  secondaryBgColor: "bg-neutral-700",
  borderColor: "border-neutral-700",
};

type Theme = typeof LIGHT | typeof EARTH | typeof MOON;

const THEMES = [LIGHT, EARTH, MOON];

const ThemeContext = createContext({
  theme: LIGHT,
  nextTheme: EARTH,
  toggleTheme: () => {},
});

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<Theme>(LIGHT);
  const [themeIdx, setThemeIdx] = useState(0);

  // let us preview the next theme
  const [nextTheme, setNextTheme] = useState<Theme>(EARTH);
  const [nextThemeIdx, setNextThemeIdx] = useState(1);

  const toggleTheme = () => {
    console.log("toggleTheme", themeIdx);
    const newIdx = (themeIdx + 1) % THEMES.length;
    const newTheme = THEMES[newIdx];
    setThemeIdx((idx) => newIdx);
    setTheme(newTheme);

    {
      /* This really exists just to make the animation in the toggle button work */
    }
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
