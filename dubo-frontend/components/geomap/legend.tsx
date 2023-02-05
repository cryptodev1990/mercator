import { useEffect, useState } from "react";
import { PALETTES } from "../../lib/hooks/scales/use-palette";

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

  useEffect(() => {
    const newPalette = Object.keys(PALETTES)[paletteIdx];
    console.log("newPalette", newPalette);
    setPaletteName && setPaletteName(newPalette);
  }, [colors, paletteIdx, setPaletteName]);

  return (
    <div className="absolute bottom-0 left-0 z-50 m-2">
      <div className="bg-slate-500 shadow-md text-white p-3">
        <div className="text-sm text-bold">{title}</div>
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
