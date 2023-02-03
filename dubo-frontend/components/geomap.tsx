import { useEffect, useMemo, useRef, useState } from "react";
// @ts-ignore
import DeckGL from "deck.gl";
// @ts-ignore
import { MVTLayer } from "@deck.gl/geo-layers";
// @ts-ignore
import { PolygonLayer, GeoJsonLayer } from "@deck.gl/layers";
import StaticMap from "react-map-gl";
import clsx from "clsx";
// @ts-ignore
import { scaleQuantile } from "d3-scale";
import useCensus from "../lib/hooks/use-census";
import Legend from "./legend";
import { useZctaShapes } from "../lib/hooks/use-zcta-shapes";

const ZOOM_TRANSITION = 7.3;
const LIGHT = "mapbox://styles/mapbox/light-v9";
const SATELLITE = "mapbox://styles/mapbox/satellite-v9";
const NONE = "none";
const TILE_URL =
  "https://api.mercator.tech/backsplash/zcta/generate_shape_tile/{z}/{x}/{y}";

const COLORS = [
  [255, 255, 178],
  [254, 217, 118],
  [253, 141, 60],
  [240, 59, 32],
  [189, 0, 38],
];

const INITIAL_QUESTION = "Where do people have gas heating?";

const GeoMap = () => {
  const [localViewPort, setLocalViewPort] = useState({
    longitude: -98.5795,
    latitude: 39.8283,
    zoom: 3,
    bearing: 0,
    pitch: 0,
  });
  const [baseMap, setBaseMap] = useState(LIGHT);
  const deckRef = useRef<DeckGL | null>(null);
  const deckContainerRef = useRef<HTMLDivElement | null>(null);
  const [query, setQuery] = useState(INITIAL_QUESTION);
  const [localQuery, setLocalQuery] = useState(query);
  const [colors, setColors] = useState(COLORS);
  const [selectedZcta, setSelectedZcta] = useState("");
  const [selectedColumn, setSelectedColumn] = useState("");
  const { zctaShapes } = useZctaShapes();
  const {
    data: { header, lookup: zctaLookup },
    isLoading,
    error,
  } = useCensus({
    query,
  });

  useEffect(() => {
    if (error) console.error("error", error);
  }, [error]);

  useEffect(() => {
    if (isLoading) return;
    if (!header) return;
    if (selectedColumn) return;
    setSelectedColumn(header[0]);
  }, [header, selectedColumn]);

  const scale = useMemo(() => {
    if (!zctaLookup) return (d: any) => [0, 0, 0];
    console.log("selectedColumn", selectedColumn);
    console.log("zctaLookup", zctaLookup);
    const vals = Object.values(zctaLookup).map((d: any) => +d[selectedColumn]);
    return scaleQuantile().domain(vals).range(COLORS);
  }, [zctaLookup, selectedColumn]);

  const breaks = useMemo(() => {
    if (!zctaLookup) return [];
    const vals = Object.values(zctaLookup).map((d: any) => +d[selectedColumn]);
    const scale = scaleQuantile().domain(vals).range(COLORS).quantiles();
    const min = Math.min(...vals);
    if (min < scale[0]) scale.unshift(min);
    return scale.map((d: any) => {
      // if there's a decimal, round to 2 places
      if (!d) {
        return d;
      } else if (d % 1 !== 0) {
        return d.toFixed(2);
      } else {
        return d;
      }
    });
  }, [zctaLookup, selectedColumn]);

  const tooltipValue = useMemo(() => {
    if (!zctaLookup) return "";
    if (!selectedZcta) return "";
    const dataRow = zctaLookup[selectedZcta];
    return dataRow;
  }, [zctaLookup, selectedZcta, selectedColumn]);

  useEffect(() => {
    // on resize, update the viewport
    const handleResize = () => {
      setLocalViewPort({
        ...localViewPort,
        // @ts-ignore
        width: deckContainerRef.current?.clientWidth ?? 0,
        // @ts-ignore
        height: deckContainerRef.current?.clientHeight ?? 0,
      });
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="h-screen border-black overflow-hidden">
      <div className="w-full h-full relative" ref={deckContainerRef}>
        {/* in the top-left corner, add an input that takes a question */}
        <div
          className={clsx(
            "absolute top-[10%] z-50 mx-auto w-full",
            "bg-slate-100 rounded-md shadow-md text-slate-900 p-3",
            "hover:bg-slate-200 "
          )}
        >
          <input
            className="bg-transparent border-none w-full border-b-red-400"
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                setQuery(localQuery);
                setSelectedColumn("");
              }
            }}
          />
        </div>
        {/* Big loading spinner in the center of the screen */}
        {isLoading && (
          <div
            className={clsx(
              "absolute top-0 left-0 z-50 w-full h-full",
              "flex flex-col justify-center items-center"
            )}
          >
            <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
            <div className="text-2xl font-bold text-gray-900">
              Loading data...
            </div>
          </div>
        )}
        {/* in the top-right corner, add a button that toggles between light and satellite maps */}
        <div
          className={clsx(
            "absolute top-0 right-0 z-50 m-2",
            "bg-slate-500 rounded-md shadow-md text-white",
            "flex flex-row justify-center items-center space-x-2 p-2",
            "cursor-pointer",
            "hover:bg-slate-200"
          )}
        >
          <div className="rounded-full h-5 w-5 bg-gray-900"></div>
          <button
            onClick={() => {
              if (baseMap === LIGHT) {
                setBaseMap(SATELLITE);
              } else if (baseMap === SATELLITE) {
                setBaseMap(NONE);
              } else if (baseMap === NONE) {
                setBaseMap(LIGHT);
              }
            }}
          >
            {(baseMap === LIGHT && "Light Map") ||
              (baseMap === SATELLITE && "Satellite Map") ||
              (baseMap === NONE && "None")}
          </button>
        </div>
        {/* legend */}
        {header.length > 0 && (
          <Legend colors={COLORS} text={breaks} title={selectedColumn} />
        )}
        {error && (
          <div className="absolute top-0 left-0 z-50 m-2">
            <div className="bg-red-500 rounded-md shadow-md text-white">
              <div className="flex flex-row justify-center items-center space-x-2 p-2">
                <div className="rounded-full h-5 w-5 bg-gray-900"></div>
                <div>
                  Your query failed. Here are some suggestions:
                  <ul>
                    <li>Try a different data set</li>
                    <li>Your query may time-out if too resource intensive</li>
                    <li>Because of high query volume, our app may fail</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
        {/* column selector */}
        {header.length > 0 && (
          <div className="absolute bottom-0 right-0 z-50 m-2">
            <div className="bg-slate-500 rounded-md shadow-md text-white">
              <div className="flex flex-row justify-center items-center space-x-2 p-2">
                <div className="rounded-full h-5 w-5 bg-gray-900"></div>
                <div>
                  <select
                    className="bg-transparent border-none"
                    value={selectedColumn}
                    onChange={(e) => {
                      setSelectedColumn(e.target.value);
                    }}
                  >
                    {header.map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}
        {/* download as csv */}
        {header.length > 0 && (
          <div className="absolute bottom-0 left-[35%] z-50 m-2">
            <div className="bg-slate-500 rounded-md shadow-md text-white">
              <div className="flex flex-row justify-center items-center space-x-2 p-2">
                <div className="rounded-full h-5 w-5 bg-gray-900"></div>
                <div>
                  <button
                    onClick={() => {
                      let csvContent = "data:text/csv;charset=utf-8,";
                      const encodedUri = encodeURI(csvContent + "TODO");
                      const link = document.createElement("a");
                      link.setAttribute("href", encodedUri);
                      link.setAttribute("download", "data.csv");
                      link.click();
                    }}
                  >
                    Download as CSV
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {/* tooltip */}
        {tooltipValue && (
          <div className="absolute top-0 left-0 z-50 m-2">
            <div className="bg-slate-500 rounded-md shadow-md text-white">
              <div className="flex flex-row justify-center items-center space-x-2 p-2">
                <div className="rounded-full h-5 w-5 bg-gray-900"></div>
                <div>
                  <div className="font-bold">ZCTA: {selectedZcta}</div>
                  <div className="font-bold">
                    {selectedColumn}: {tooltipValue[selectedColumn]}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        <DeckGL
          ref={deckRef}
          initialViewState={localViewPort}
          onViewStateChange={({ viewState }: any) => {
            setLocalViewPort({
              ...localViewPort,
              latitude: viewState.latitude,
              longitude: viewState.longitude,
              zoom: viewState.zoom,
            });
          }}
          controller={{
            touchRotate: false,
            dragRotate: false,
          }}
          onHover={({ object }: any) => {
            // if (!object && !selectedZcta) {
            //   return;
            // }
            // if (!object) {
            //   setSelectedZcta("");
            //   return;
            // }
            // const { zcta } = object.properties;
            // setSelectedZcta(zcta);
          }}
          onClick={({ object }: any) => {
            console.log(object);
          }}
          layers={[
            new GeoJsonLayer({
              layerName: "usa",
              data: "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
              getFillColor: COLORS[0],
              stroked: false,
            }),
            new PolygonLayer({
              layerName: "zcta-high",
              visible: localViewPort.zoom <= ZOOM_TRANSITION,
              data: zctaShapes,
              updateTriggers: {
                getFillColor: [selectedColumn, selectedZcta, zctaLookup],
              },
              getPolygon: (d: any) => {
                return d.geom;
              },
              getFillColor: (d: any) => {
                if (!zctaLookup) return COLORS[0];
                try {
                  const { zcta } = d;
                  if (zcta === selectedZcta) return [255, 255, 255];
                  const val = zctaLookup[zcta][selectedColumn];
                  const color = scale(val);
                  return color;
                } catch (e) {
                  return [0, 0, 0, 0];
                }
              },
              stroked: true,
              filled: true,
              pickable: true,
              extruded: false,
              wireframe: false,
              opacity: 1,
            }),
            new MVTLayer({
              layerName: "zcta-low",
              data: TILE_URL,
              minZoom: 6,
              maxZoom: 24,
              visible: localViewPort.zoom > ZOOM_TRANSITION,
              maxRequests: -1,
              updateTriggers: {
                getFillColor: [selectedColumn, selectedZcta, zctaLookup],
              },
              pickingRadius: 5,
              filled: true,
              extruded: false,
              wireframe: false,
              opacity: 0.5,
              getFillColor: (d: any) => {
                if (!zctaLookup) return [0, 0, 0];
                try {
                  const { zcta } = d.properties;
                  if (zcta === selectedZcta) return [255, 255, 255];
                  const val = zctaLookup[zcta][selectedColumn];
                  const color = scale(val);
                  return color;
                } catch (e) {
                  return [0, 0, 0, 0];
                }
              },
              pickable: true,
            }),
            // simple USA map
          ]}
        >
          <StaticMap
            reuseMaps
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            attributionControl={false}
            // turn off base map
            mapStyle={baseMap !== NONE ? baseMap : undefined}
          />
        </DeckGL>
      </div>
    </div>
  );
};

export default GeoMap;
