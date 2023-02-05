import { useEffect, useMemo, useRef, useState } from "react";
// @ts-ignore
import DeckGL from "deck.gl";
// @ts-ignore
import { MVTLayer } from "@deck.gl/geo-layers";
// @ts-ignore
import { PolygonLayer, GeoJsonLayer } from "@deck.gl/layers";
import StaticMap from "react-map-gl";
import clsx from "clsx";
import useCensus from "../../lib/hooks/census/use-census";
import Legend from "./legend";
import { useZctaShapes } from "../../lib/hooks/use-zcta-shapes";
import useCensusAutocomplete from "../../lib/hooks/census/use-census-autocomplete";
import { SearchBar } from "../search-bar";
import { CloseButton } from "../close-button";
import { usePalette } from "../../lib/hooks/scales/use-palette";

const ZOOM_TRANSITION = 7.1;
// add no labels
const LIGHT =
  "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json";
const SATELLITE = "mapbox://styles/mapbox/satellite-v9";
const TILE_URL =
  "https://api.mercator.tech/backsplash/zcta/generate_shape_tile/{z}/{x}/{y}";

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
  const { data: autocompleteSuggestions } = useCensusAutocomplete({
    text: localQuery,
  });

  const dataVector = useMemo(() => {
    if (!zctaLookup) return [];
    const vals = Object.values(zctaLookup).map((d: any) => +d[selectedColumn]);
    return vals;
  }, [zctaLookup, selectedColumn]);

  const { colors, breaks, scale, setPaletteName, setScaleType } = usePalette({
    vec: dataVector,
  });

  console.log("colors", colors);

  const [fixSelected, setFixSelected] = useState(false);

  useEffect(() => {
    if (error) console.error("error", error);
  }, [error]);

  useEffect(() => {
    if (isLoading) return;
    if (!header) return;
    if (selectedColumn) return;
    setSelectedColumn(header[0]);
  }, [header, selectedColumn]);

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
        <SearchBar
          value={localQuery}
          onChange={(text) => setLocalQuery(text)}
          onEnter={() => {
            setQuery(localQuery);
            setSelectedColumn("");
          }}
          autocompleteSuggestions={autocompleteSuggestions?.suggestions ?? []}
        />
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
                setBaseMap(LIGHT);
              }
            }}
          >
            {(baseMap === LIGHT && "Light Map") ||
              (baseMap === SATELLITE && "Satellite Map")}
          </button>
        </div>
        {/* legend */}
        {header.length > 0 && (
          <Legend
            colors={colors}
            text={breaks}
            title={selectedColumn}
            isRatio={selectedColumn?.includes("ratio")}
            setPaletteName={setPaletteName}
          />
        )}
        {error && (
          <div className="absolute top-0 left-0 z-50 m-2">
            <div className="bg-orange-500 rounded-md shadow-md text-white">
              <div className="flex flex-row justify-center items-center space-x-2 p-2">
                <div className="rounded-full h-5 w-5 bg-gray-900"></div>
                {/*close button*/}
                <CloseButton
                  onClick={() => {
                    setLocalQuery("");
                    setQuery("");
                    setSelectedColumn("");
                  }}
                />
                Your query failed. Here are some suggestions:
                <ul>
                  <li>Try a different data set</li>
                  <li>Your query may time-out if too resource intensive</li>
                  <li>Because of high query volume, our app may fail</li>
                </ul>
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
            if (fixSelected) {
              return;
            }

            if (!object && !selectedZcta) {
              return;
            }
            if (!object) {
              setSelectedZcta("");
              return;
            }
            const zcta =
              object?.zcta ||
              object?.properties.zcta ||
              object?.properties.ZCTA5CE10;
            setSelectedZcta(zcta);
          }}
          onClick={({ object }: any) => {
            if (!object) {
              setSelectedZcta("");
              setFixSelected(false);
            }
            const zcta =
              object?.zcta ||
              object?.properties?.zcta ||
              object?.properties?.ZCTA5CE10;
            if (zcta === selectedZcta) {
              setSelectedZcta("");
              setFixSelected(false);
              return;
            }
            setSelectedZcta(zcta);
            setFixSelected(true);
          }}
          layers={[
            new GeoJsonLayer({
              layerName: "usa",
              data: "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
              getOffset: [0, 0],
              getFillColor: colors[0],
              stroked: false,
            }),
            new PolygonLayer({
              layerName: "zcta-high",
              visible: localViewPort.zoom <= ZOOM_TRANSITION,
              getOffset: [0, 1],
              data: zctaShapes,
              updateTriggers: {
                getFillColor: [
                  selectedColumn,
                  selectedZcta,
                  zctaLookup,
                  colors,
                ],
              },
              getPolygon: (d: any) => {
                return d.geom;
              },
              getFillColor: (d: any) => {
                if (!zctaLookup) return colors[0];
                try {
                  if (d.zcta === selectedZcta) return [255, 255, 255];
                  const val = zctaLookup[d.zcta][selectedColumn];
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
              getOffset: [0, 1],
              updateTriggers: {
                getFillColor: [
                  selectedColumn,
                  selectedZcta,
                  zctaLookup,
                  colors,
                ],
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
            mapStyle={baseMap}
          />
        </DeckGL>
      </div>
    </div>
  );
};

export default GeoMap;
