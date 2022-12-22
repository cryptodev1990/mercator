import { useDispatch, useSelector } from "react-redux";
import { SearchResponse } from "src/store/search-api";
import {
  deleteOneSearchResult,
  selectSearchState,
} from "../../src/search/search-slice";
import simplur from "simplur";
import {
  LayerStyle,
  selectGeoMapState,
  setViewport,
  updateStyle,
} from "src/shapes/shape-slice";
import { bbox, centroid } from "@turf/turf";
import { bboxToZoom } from "src/lib/geo-utils";
import clsx from "clsx";
import { useEffect, useRef, useState } from "react";
import { convertHexToRGB, convertRGBToHex } from "src/lib/colors";

const DeleteButton = ({ searchResult }: { searchResult: SearchResponse }) => {
  const dispatch = useDispatch();
  function onClick() {
    dispatch(deleteOneSearchResult(searchResult?.query));
  }
  return (
    <button
      className="bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
      onClick={onClick}
    >
      Delete
    </button>
  );
};

const HamburgerMenu = ({
  searchResult,
  layerStyle,
}: {
  searchResult: SearchResponse;
  layerStyle: LayerStyle;
}) => {
  return (
    <button className="flex-0 ml-auto">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 6h16M4 12h16M4 18h16"
        />
      </svg>
    </button>
  );
};

const ZoomButton = ({ searchResult }: { searchResult: SearchResponse }) => {
  const dispatch = useDispatch();
  function onClick() {
    alert("zoom to " + searchResult?.query);
  }
  return (
    <button
      className="bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
      onClick={onClick}
    >
      Z
    </button>
  );
};

const RadiusPicker = ({
  radius,
  setRadius,
}: {
  radius: number;
  setRadius: (radius: number) => void;
}) => {
  return <SliderPicker knotSize={radius} setKnotSize={setRadius} />;
};

const SliderPicker = ({
  knotSize,
  setKnotSize,
  min,
  max,
  step,
}: {
  knotSize: number;
  setKnotSize: (knotSize: number) => void;
  min?: number;
  max?: number;
  step?: string;
}) => {
  const [selected, setSelected] = useState(false);
  const [interacted, setInteracted] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (selected && inputRef.current) {
      inputRef.current?.focus();
      inputRef.current?.select();
    } else {
      setInteracted(false);
    }
  }, [selected]);

  return (
    <div className="flex flex-row gap-2">
      {!selected && (
        <button
          onMouseDown={() => setSelected(true)}
          className={clsx(
            "bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
          )}
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="12"
              cy="12"
              r={~~Math.floor(Math.sqrt(knotSize)) || 2}
            />
          </svg>
        </button>
      )}
      <div>
        <input
          ref={inputRef}
          autoFocus={selected}
          className={clsx(
            "bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded -rotate-90 translate-x-[-50px] transform",
            selected ? "block" : "hidden"
          )}
          onChange={(e) => {
            setKnotSize(parseFloat(e.target.value));
            setInteracted(true);
          }}
          onMouseUp={() => {
            // If the slider actually moved, then close it
            if (interacted) {
              setSelected(false);
            }
          }}
          value={knotSize}
          max={max || 100}
          min={min || 0}
          step={step || "1"}
          type="range"
        ></input>
      </div>
    </div>
  );
};

const ColorPicker = ({
  color,
  setColor,
}: {
  color: number[];
  setColor: (color: string) => void;
}) => {
  const hexColor = convertRGBToHex(color);
  console.log("hexColor", hexColor);
  console.log("color", color);
  return (
    <div className="relative">
      <input
        type="color"
        className="z-10 w-6 h-6 absolute top-0 left-0 opacity-0"
        id="head"
        name="head"
        value={"#000000"}
        onChange={(e) => {
          console.log(e.target.value);
          setColor(e.target.value);
        }}
      />
      <svg
        className="w-6 h-6"
        fill={hexColor.toUpperCase()}
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 15l7-7 7 7M5 21l7-7 7 7"
        />
      </svg>
    </div>
  );
};

const LayerCard = ({
  searchResult,
  layerStyle,
}: {
  searchResult: SearchResponse;
  layerStyle: LayerStyle;
}) => {
  const dispatch = useDispatch();
  if (!searchResult) {
    console.warn("LayerCard got null search");
    return null;
  }
  const {
    query,
    parse_result: { geom },
  } = searchResult;
  const numResults = geom?.features?.length ?? 0;
  return (
    <div
      onClick={() => {
        console.log("clicked");
      }}
      className="flex flex-col w-64 h-[100px] bg-slate-100 text-slate-800 rounded-lg shadow-lg p-2 cursor-pointer"
    >
      <h4 className="font-bold text-ellipsis">{query}</h4>
      <div className="flex flex-row">
        <HamburgerMenu layerStyle={layerStyle} searchResult={searchResult} />
        <p>{simplur`${numResults} shape[|s]`}</p>
        <ZoomButton searchResult={searchResult} />
        <ColorPicker
          color={layerStyle.paint}
          setColor={(newColor: string) => {
            dispatch(
              updateStyle({
                paint: convertHexToRGB(newColor),
                id: layerStyle.id,
              })
            );
          }}
        />
        <RadiusPicker
          radius={layerStyle.lineThicknessPx}
          setRadius={(newKnotSize: number) => {
            dispatch(
              updateStyle({ lineThicknessPx: newKnotSize, id: layerStyle.id })
            );
          }}
        />
        <SliderPicker
          knotSize={layerStyle.opacity}
          min={0}
          step={"0.1"}
          max={1}
          setKnotSize={(newOpacity: number) => {
            dispatch(updateStyle({ opacity: newOpacity, id: layerStyle.id }));
          }}
        />
        <DeleteButton searchResult={searchResult} />
      </div>
    </div>
  );
};

const ColorSquare = ({ color }: { color: number[] }) => {
  const hexColor = convertRGBToHex(color);
  return (
    <div className="relative">
      <svg
        className="w-6 h-6"
        fill={hexColor.toUpperCase()}
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 10 L90 10 L90 90 L10 90 Z"
        />
      </svg>
    </div>
  );
};

const LayerCardSm = ({
  searchResult,
  layerStyle,
}: {
  searchResult: SearchResponse;
  layerStyle: LayerStyle;
}) => {
  const query = searchResult?.query;
  const geom = searchResult?.parse_result.geom;
  const entities = searchResult?.parse_result.entities;

  if (!query || !geom || !entities) {
    return null;
  }
  return (
    <div
      onClick={() => {
        console.log("clicked");
      }}
      className="flex flex-row w-64 bg-slate-100 text-slate-800 shadow-lg p-2 cursor-pointer"
    >
      <h4 className="font-bold text-ellipsis">{query}</h4>
      <div className="flex-none ml-auto">
        <ColorSquare color={layerStyle.paint} />
      </div>
    </div>
  );
};

const LayerCardBar = () => {
  const { searchResults } = useSelector(selectSearchState);
  const { layerStyles } = useSelector(selectGeoMapState);

  if (!searchResults) {
    return null;
  }

  return (
    <div className="flex flex-col items-center justify-start w-full h-[90vh] gap-1 overflow-y-scroll">
      <LayerCard searchResult={searchResults[0]} layerStyle={layerStyles[0]} />
      {searchResults.map((searchResult, i) => {
        return (
          <LayerCardSm
            key={searchResult.id}
            searchResult={searchResult}
            layerStyle={layerStyles[i]}
          />
        );
      })}
    </div>
  );
};

export default LayerCardBar;
