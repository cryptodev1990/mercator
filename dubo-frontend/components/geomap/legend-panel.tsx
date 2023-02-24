import { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import Image from "next/image";

import Icon from "../../Icon";
import { PALETTES } from "../../lib/hooks/scales/use-palette";
import { useTheme } from "../../lib/hooks/census/use-theme";

import { abbrevTick, formatPercentage } from "./legend";

const LegendPanel = ({
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
  const { theme } = useTheme();
  const [paletteIdx, setPaletteIdx] = useState(0);
  const [relabeling, setRelabeling] = useState(false);

  const [slide, setSlide] = useState<boolean>(false);

  const handleIconHideClick = () => {
    setIconShow("visible");
    setLegendShow("-translate-x-56");
  };

  useEffect(() => {
    const newPalette = Object.keys(PALETTES)[paletteIdx];

		if (!setPaletteName) return;
		setPaletteName(newPalette);
  }, [colors, paletteIdx, setPaletteName]);

  if (text.length === 0) {
    return null;
  }

	const onCangeDensity = (e:any) => {
		const value = e.target.value;

		if (header.indexOf(value) !== -1) {
			setSelectedColumn(value);
		}
	}

  return (
    <div className={`relative flex-1 w-[17rem] transition-transform duration-100 ${slide ? `-translate-x-72` : ``}`}>
      <label 
        className={clsx(
          "absolute top-0 -right-1 translate-x-full cursor-pointer p-2 panel-combo",
          theme.bgColor,
          theme.fontColor
        )}
        onClick={() => setSlide(!slide)}
        htmlFor="for-setting"
      >
        {slide ? (<Icon icon="CircleRight" width="1.1rem" height="1.1rem" />) : (<Icon icon="CircleLeft" width="1.1rem" height="1.1rem" />)}
      </label>
      <div
        className={clsx(
          "shadow-md py-5 px-5 flex flex-col justify-start group h-full",
          theme.bgColor,
          theme.fontColor
        )}
      >
        <h2 className="text-2xl text-center mb-3">Legend Setting</h2>
        <div id="Input Field" className="flex flex-col mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Icon icon={"Pen"} />
            <h3 className="text-lg">Label Name</h3>
          </div>
          <div className="flex justify-between items-center gap-3 pl-4">
            <input
              className={clsx(
                "w-full p-3 border-1 border-stone-300",
                theme.bgColor,
                theme.fontColor
              )}
              placeholder="Select the label"
              title="RatioName"
              list="density"
              onChange={onCangeDensity}
            />
            <datalist id="density" className="absolute w-full">
              {header.map(
                (item, key) => (
                  <option key={key} className="">
                    {item}
                  </option>
                )
              )}
            </datalist>
          </div>
        </div>
        <div id="Palette Select" className="flex flex-col mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Icon icon={"Palette"} />
            <h3 className="text-lg">Palette Type</h3>
          </div>
          <div className="pl-4">
            <div className="relative" data-te-dropdown-ref>
              <a
                className="flex items-center justify-between border-1 border-stone-300 whitespace-nowrap p-3 ont-medium leading-normal transition duration-150 ease-in-out"
                href="#"
                type="button"
                id="dropdownMenuButton2"
                data-te-dropdown-toggle-ref
                aria-expanded="false"
                data-te-ripple-init
                data-te-ripple-color="light"
              >
                <div className="flex flex-row">
                  {colors.map((color, i) => (
                    <div key={i} className="text-center">
                      <div
                        className="h-7 w-7 cursor-pointer"
                        style={{
                          background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`,
                        }}
                      ></div>
                      <div
                        className="text-sm w-full overflow-hidden cursor-pointer select-none"
                      >
                        {isRatio ? +formatPercentage(+text[i]) : abbrevTick(+text[i])}
                      </div>
                    </div>
                  ))}
                </div>
                <span className="mr-2 w-2 mb-6">
                  <Icon icon={"Chevren"} />
                </span>
              </a>
              <ul
                className="absolute z-[1000] float-left m-0 hidden min-w-max list-none overflow-hidden w-full border-none bg-white bg-clip-padding text-left text-base shadow-lg dark:bg-neutral-700 [&[data-te-dropdown-show]]:block"
                aria-labelledby="dropdownMenuButton2"
                data-te-dropdown-menu-ref
              >
                <li>
                  {Object.values(PALETTES).map((clrs, k) => (
                    <a
                      key={k}
                      className="block w-full whitespace-nowrap bg-transparent py-2 px-4 text-sm font-normal text-neutral-700 hover:bg-neutral-100 active:text-neutral-800 active:no-underline disabled:pointer-events-none disabled:bg-transparent disabled:text-neutral-400 dark:text-neutral-200 dark:hover:bg-neutral-600"
                      href="#"
                      data-te-dropdown-item-ref
                      onClick={() =>
                        setPaletteIdx(k)
                      }
                    >
                      <div className="flex flex-row">
                        {clrs.map((color, i) => (
                          <div key={i} className="text-center">
                            <div
                              className="h-7 w-7 cursor-pointer"
                              style={{
                                background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`,
                              }}
                            ></div>
                          </div>
                        ))}
                      </div>
                    </a>
                  ))}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div id="Scale Type" className="flex flex-col mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Icon icon={"Checks"} />
            <h3 className="text-lg">Scale Type</h3>
          </div>
          <div className="flex flex-col pl-4">
            <label className="flex gap-3 px-2">
              <input type="radio" name="scale_type" value="quantize" onChange={(e) => onScaleTextClicked(e.target.value)} defaultChecked={scaleType === "quantize"} />
              <span>Quantity</span>
            </label>
            <label className="flex gap-3 px-2">
              <input type="radio" name="scale_type" value="quantile" onChange={(e) => onScaleTextClicked(e.target.value)} defaultChecked={scaleType === "quantile"} />
              <span>Quantile</span>
            </label>
          </div>
        </div>
        {/* <button clas></button> */}
      </div>
    </div>
  );
};

export default LegendPanel;
