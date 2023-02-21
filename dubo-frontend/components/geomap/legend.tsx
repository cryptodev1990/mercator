import { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import {
  AiOutlineCloseCircle,
  AiFillCheckCircle,
  AiOutlineDoubleLeft,
} from "react-icons/ai";
import { BiPencil } from "react-icons/bi";

import { PALETTES } from "../../lib/hooks/scales/use-palette";
import { useTheme } from "../../lib/hooks/census/use-theme";

export const formatPercentage = (num: number) => {
  return (num * 100).toFixed(1);
};

function abbrevTick(num: number) {
  // If the number in the 1's position is greater than 0, cut the decimal
  // return K for the number of thousands
  if (num >= 1000) {
    return `${(num / 1000).toFixed(0)}K`;
  }
  // return M for the number of millions
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(0)}M`;
  }
  if (num % 10 > 0) {
    return `${num.toFixed(0)}`;
  }
  return `${num.toFixed(0)}`;
}

export const ColumnSelector = ({
  columns,
  selectedColumn,
  setSelectedColumn,
}: {
  columns: string[];
  selectedColumn: string;
  setSelectedColumn: (column: string) => void;
}) => {
  const [interacted, setInteracted] = useState(false);
  const selectRef = useRef<HTMLSelectElement | null>(null);

  useEffect(() => {
    setInteracted(false);
  }, [columns[0]]);

  return (
    <div className="max-w-[14rem] flex flex-row cursor-pointer">
      <select
        title="density"
        name="colorSelect"
        // change default caret
        ref={selectRef}
        className="bg-transparent border-none w-full border-red-400 text-ellipsis cursor-pointer"
        value={selectedColumn}
        onFocus={() => setInteracted(true)}
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
      {/* circle containing the number of columns */}
      <button
        title="focusButton"
        type="button"
        onClick={() => {
          if (selectRef.current) {
            selectRef.current.focus();
          }
        }}
      >
        <svg
          className={clsx(
            "w-5 h-5 translate-x-2 translate-y-[0.66rem]",
            !interacted && columns.length !== 1 ? "visible" : "invisible"
          )}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="12" cy="12" r="12" fill={"#679eff"} />
          <text
            x="50%"
            y="50%"
            dominantBaseline="middle"
            textAnchor="middle"
            fill={"#fff"}
          >
            {columns.length}
          </text>
        </svg>
      </button>
    </div>
  );
};

const Legend = ({
  setIconShow,
  setLegendShow,
  colors,
  text,
  isRatio,
  setPaletteName,
  scaleType,
  onScaleTextClicked,
  header,
  selectedColumn,
  setSelectedColumn,
  label,
  setLabel,
}: {
  setIconShow: (iconShow: string) => void;
  setLegendShow: (legendShow: string) => void;
  colors: number[][];
  text: string[];
  isRatio?: boolean;
  scaleType: string;
  setPaletteName?: (name: any) => void;
  onScaleTextClicked: any;
  header: string[];
  selectedColumn: string;
  setSelectedColumn: (column: string) => void;
  label: string | null;
  setLabel: (label: string | null) => void;
}) => {
  const [paletteIdx, setPaletteIdx] = useState(0);
  const { theme } = useTheme();
  const [relabeling, setRelabeling] = useState(false);

  const handleIconHideClick = () => {
    setIconShow("visible");
    setLegendShow("hidden");
  };

  useEffect(() => {
    const newPalette = Object.keys(PALETTES)[paletteIdx];
    setPaletteName && setPaletteName(newPalette);
  }, [colors, paletteIdx, setPaletteName]);

  if (text.length === 0) {
    return null;
  }

  return (
    <div
      className={clsx(
        "shadow-md py-5 px-3 flex flex-col justify-start items-center gap-3 rounded group max-w-[13rem] relative",
        theme.bgColor,
        theme.fontColor
      )}
    >
      <div
        className={clsx(
          "absolute right-0 top-0 m-2 cursor-pointer h-5 w-5",
          theme.bgColor,
          theme.fontColor
        )}
        onClick={handleIconHideClick}
      >
        <AiOutlineDoubleLeft />
      </div>
      <div className="flex flex-row-reverse justify-between w-full">
        {relabeling ? (
          <div className="flex flex-row gap-3 w-full">
            <input
              autoFocus
              onBlur={(e) => setRelabeling(false)}
              type="text"
              onSubmit={(e) => setRelabeling(false)}
              onChange={(e) => setLabel(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setRelabeling(false);
                }
              }}
              className={clsx(
                "px-2 text-center",
                theme.secondaryBgColor,
                theme.secondaryFontColor
              )}
              placeholder="A title for this legend"
            />
            <button
              title="AiFilCheckCircle"
              type="button"
              onClick={() => {
                setRelabeling(false);
              }}
            >
              <AiFillCheckCircle size={20} />
            </button>
          </div>
        ) : (
          <>
            {label ? (
              <span className="text-md text-ellipsis overflow-x-clip text-center">
                {label}
              </span>
            ) : (
              <ColumnSelector
                columns={header}
                selectedColumn={selectedColumn}
                setSelectedColumn={setSelectedColumn}
              />
            )}
            <button
              className="group-hover:visible group-hover:animate-fadeIn100 invisible w-5 h-5"
              onClick={() => {
                if (label) {
                  setLabel(null);
                } else {
                  setRelabeling(true);
                }
              }}
            >
              {label ? <AiOutlineCloseCircle /> : <BiPencil />}
            </button>
          </>
        )}
      </div>
      {/* Colors */}
      <div>
        {/* paintbrush icon that changes the palette */}
        <div className="flex flex-row">
          {colors.map((color, i) => (
            <div key={i} className="text-left">
              <div
                className="h-7 w-7 cursor-pointer"
                onClick={() =>
                  setPaletteIdx(
                    (paletteIdx + 1) % Object.values(PALETTES).length
                  )
                }
                style={{
                  background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`,
                }}
              ></div>
              <div
                onClick={onScaleTextClicked}
                className="text-sm w-full overflow-hidden cursor-pointer select-none"
              >
                {isRatio ? +formatPercentage(+text[i]) : abbrevTick(+text[i])}
              </div>
            </div>
          ))}
        </div>
        <div
          onClick={onScaleTextClicked}
          className="w-full mx-auto text-center text-xs cursor-pointer select-none"
        >
          {isRatio && "% "}
          {scaleType === "quantile" && "By Quantiles"}
        </div>
      </div>
    </div>
  );
};

export default Legend;
