import { useEffect, useState } from "react";
import { PALETTES } from "../../lib/hooks/scales/use-palette";
import { useTheme } from "../../lib/hooks/census/use-theme";
import clsx from "clsx";

const pctFormat = (num: number) => {
  return `${num * 100}%`;
};

const Legend = ({
  colors,
  text,
  title,
  isRatio,
  setPaletteName,
}: {
  colors: number[][];
  text: string[];
  title: string;
  isRatio?: boolean;
  setPaletteName?: (name: any) => void;
}) => {
  const [paletteIdx, setPaletteIdx] = useState(0);
  const { theme } = useTheme();

  useEffect(() => {
    const newPalette = Object.keys(PALETTES)[paletteIdx];
    setPaletteName && setPaletteName(newPalette);
  }, [colors, paletteIdx, setPaletteName]);

  if (!title) {
    return null;
  }

  return (
    <div className="absolute bottom-0 left-0 z-50 m-2">
      <div className={clsx("shadow-md p-3", theme.bgColor, theme.fontColor)}>
        <div className="text-sm font-bold">{title}</div>
        <div className="">
          {colors.map((color, i) => {
            return (
              <div key={i} className="flex flex-row justify-start gap-3">
                <div
                  className="h-5 w-5 cursor-pointer"
                  onClick={() => {
                    setPaletteIdx(
                      (paletteIdx + 1) % Object.values(PALETTES).length
                    );
                  }}
                  style={{
                    background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`,
                  }}
                ></div>
                {Number.isFinite(+text[i]) && (
                  <div className="text-sm w-full overflow-hidden">
                    {isRatio ? pctFormat(+text[i]) : +text[i]}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Legend;
