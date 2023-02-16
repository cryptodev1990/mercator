import clsx from "clsx";

import { useTheme } from "../../lib/hooks/census/use-theme";

export const MapToggle = () => {
  const { theme, toggleTheme, nextTheme } = useTheme();

  return (
    <button
      onClick={() => toggleTheme()}
      className={clsx(
        "relative shadow-md h-12 w-12",
        "space-x-2 hover:shadow-lg",
        "flex flex-col justify-start items-center",
        "cursor-pointer overflow-hidden group",
        "sm:block hidden"
      )}
    >
      <div className="">
        <div
          className={clsx(
            "shadow-md h-12 w-12",
            "flex flex-row justify-center items-center",
            "cursor-pointer",
            "group-hover:animate-pushUpOnce",
            theme.bgColor,
            theme.fontColor
          )}
        >
          {theme.icon}
        </div>
        {/* This really exists just to make the animation work */}
        <div
          className={clsx(
            "shadow-md h-12 w-12 hover:shadow-lg hover",
            "flex flex-row justify-center items-center space-x-2 p-2",
            "cursor-pointer",
            "group-hover:animate-pushUpOnce",
            nextTheme.bgColor,
            nextTheme.fontColor
          )}
          onClick={() => toggleTheme()}
        >
          {nextTheme.icon}
        </div>
      </div>
    </button>
  );
};
