import { useEffect, useRef, useState } from "react";
import { PALETTES } from "../../lib/hooks/scales/use-palette";
import { useTheme } from "../../lib/hooks/census/use-theme";
import clsx from "clsx";
import { BiPencil } from "react-icons/bi";
import { AiOutlineCloseCircle, AiFillCheckCircle } from "react-icons/ai";
import { BsFillPaletteFill } from "react-icons/bs";

const pctFormat = (num: number) => {
  return `${num * 100}%`;
};

const pctFmtSansPct = (num: number) => {
  return `${num * 100}`;
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

const PaletteButton = ({
  colors,
  setPaletteIdx,
  paletteIdx,
  theme,
}: {
  colors: number[][];
  setPaletteIdx: (idx: number) => void;
  paletteIdx: number;
  theme: any;
}) => {
  return (
    <div className="absolute invisible justify-center items-center gap-3 group-hover:visible">
      <button
        onClick={() =>
          setPaletteIdx((paletteIdx + 1) % Object.values(PALETTES).length)
        }
        className={clsx(
          "w-10 h-10 flex flex-row justify-center items-center rounded border-2 shadow-sm shadow-black",
          theme.bgColor
        )}
      >
        {/* Place one pan icon slightly behind the other */}

        <BsFillPaletteFill
          size={20}
          style={{
            color: `rgb(${colors[4][0]}, ${colors[4][1]}, ${colors[4][2]})`,
          }}
        />
      </button>
    </div>
  );
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
  const [interacted, setInteracted] = useState(false);
  const selectRef = useRef<HTMLSelectElement | null>(null);

  useEffect(() => {
    setInteracted(false);
  }, [columns[0]]);

  return (
    <div className="max-w-[14rem] flex flex-row">
      <select
        // change default caret
        ref={selectRef}
        style={{
          appearance: "none",
          WebkitAppearance: "none",
          MozAppearance: "none",
        }}
        className="bg-transparent border-none w-full border-red-400"
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
        onClick={() => {
          if (selectRef.current) {
            selectRef.current.focus();
          }
        }}
      >
        <svg
          className={clsx(
            "w-5 h-5",
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
  colors,
  text,
  isRatio,
  setPaletteName,
  scaleType,
  onScaleTextClicked,
  children,
}: {
  colors: number[][];
  text: string[];
  isRatio?: boolean;
  scaleType: string;
  setPaletteName?: (name: any) => void;
  onScaleTextClicked: any;
  children?: React.ReactNode;
}) => {
  const [paletteIdx, setPaletteIdx] = useState(0);
  const { theme } = useTheme();
  const [relabeling, setRelabeling] = useState(false);
  const [label, setLabel] = useState<string | null>(null);

  useEffect(() => {
    const newPalette = Object.keys(PALETTES)[paletteIdx];
    setPaletteName && setPaletteName(newPalette);
  }, [colors, paletteIdx, setPaletteName]);

  return (
    <div
      className={clsx(
        "shadow-md py-5 px-3 flex flex-col justify-start items-center gap-3 rounded group max-w-[13rem]",
        theme.bgColor,
        theme.fontColor
      )}
    >
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
                theme.fontColor
              )}
              placeholder="A title for this legend"
            />
            <button
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
              <span className="text-md text-ellipsis overflow-x-clip">
                {label}
              </span>
            ) : (
              children
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
          {colors.map((color, i) => {
            return (
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
                  {isRatio ? pctFmtSansPct(+text[i]) : abbrevTick(+text[i])}
                </div>
              </div>
            );
          })}
        </div>
        <div
          onClick={onScaleTextClicked}
          className="w-full mx-auto text-center text-xs cursor-pointer select-none"
        >
          {isRatio && "% "}
          {scaleType === "quantile" && "(By quantiles)"}
        </div>
      </div>
    </div>
  );
};

export default Legend;
