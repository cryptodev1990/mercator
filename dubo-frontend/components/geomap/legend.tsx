import { useEffect, useState } from "react";
import { PALETTES } from "../../lib/hooks/scales/use-palette";
import { useTheme } from "../../lib/hooks/census/use-theme";
import clsx from "clsx";

const pctFormat = (num: number) => {
  return `${num * 100}%`;
};

export const ColumnSelector = ({
  columns,
  selectedColumn,
  setSelectedColumn,
}: {
  columns: string[];
  selectedColumn: string;
  setSelectedColumn: (column: string) => void;
}) => {
  return (
    <div>
      <select
        className="bg-transparent border-none"
        value={selectedColumn}
        onChange={(e) => {
          setSelectedColumn(e.target.value);
        }}
      >
        {columns.map((d) => (
          <option key={d} value={d}>
            {d}
          </option>
        ))}
      </select>
    </div>
  );
};

const Legend = ({
  colors,
  text,
  isRatio,
  setPaletteName,
  children,
}: {
  colors: number[][];
  text: string[];
  isRatio?: boolean;
  setPaletteName?: (name: any) => void;
  children?: React.ReactNode;
}) => {
  const [paletteIdx, setPaletteIdx] = useState(0);
  const { theme } = useTheme();

  useEffect(() => {
    const newPalette = Object.keys(PALETTES)[paletteIdx];
    setPaletteName && setPaletteName(newPalette);
  }, [colors, paletteIdx, setPaletteName]);

  if (!text) {
    return null;
  }

  return (
    <div
      className={clsx(
        "shadow-md py-5 px-3 flex flex-col justify-start items-center gap-3 rounded",
        theme.bgColor,
        theme.fontColor
      )}
    >
      {children}
      <div className="">
        {colors.map((color, i) => {
          return (
            <div key={i} className="flex flex-row justify-start gap-3">
              <div
                className="h-7 w-7 cursor-pointer"
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
  );
};

export default Legend;
