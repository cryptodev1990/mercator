import { useCallback, useEffect, useRef, useState } from "react";
// @ts-ignore
import DeckGL, { GeoJsonLayer, FlyToInterpolator } from "deck.gl";
import StaticMap from "react-map-gl";
import { snapToBounds } from "../../../src/lib/geo-utils";
import { useDispatch, useSelector } from "react-redux";
import { selectSearchState } from "src/search/search-slice";
import clsx from "clsx";
import { selectGeoMapState, setViewport } from "src/shapes/shape-slice";
import { webGLInit } from "./blend";
import { Feature } from "src/store/search-api";

const DARK = "mapbox://styles/mapbox/dark-v9";
const SATELLITE = "mapbox://styles/mapbox/satellite-v9";

const GeoMap = () => {
  const { searchResults } = useSelector(selectSearchState);
  const { layerStyles, viewport } = useSelector(selectGeoMapState);
  const [localViewPort, setLocalViewPort] = useState(viewport);
  // deck.gl map with a GeoJsonLayer
  const dispatch = useDispatch();

  const [baseMap, setBaseMap] = useState(DARK);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setLocalViewPort({ ...viewport });
    console.log("testing");
  }, [viewport]);

  useEffect(() => {
    if (searchResults.length > 0) {
      const { geom: newGeom } =
        searchResults[searchResults.length - 1].parse_result;
      const bounds = snapToBounds({
        features: (newGeom.features ?? []) as Feature[],
        type: newGeom.type ?? "FeatureCollection",
        bbox: [],
      });
      if (bounds) {
        setLocalViewPort({
          ...localViewPort,
          longitude: bounds?.longitude,
          latitude: bounds?.latitude,
          zoom: 12,
        });
      }
    }
    console.log("testing");
  }, [searchResults.length]);

  // After 500 ms of inactivity, set the global viewport to be the local viewport
  useEffect(() => {
    if (
      localViewPort.latitude !== viewport.latitude &&
      localViewPort.longitude !== viewport.longitude &&
      localViewPort.zoom !== viewport.zoom
    ) {
      timeoutRef.current = setTimeout(() => {
        dispatch(setViewport({ ...localViewPort }));
      }, 500);
    }
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [localViewPort, dispatch]);

  if (!viewport || !viewport.zoom) {
    return null;
  }

  return (
    <div className="w-full h-full">
      <div className="w-full h-full relative">
        <div
          className={clsx(
            "absolute top-0 right-0 z-50 m-2",
            "bg-slate-100 rounded-md shadow-md text-black",
            "flex flex-row justify-center items-center space-x-2 p-2",
            "cursor-pointer",
            "hover:bg-slate-200"
          )}
        >
          <button
            onClick={() => setBaseMap(baseMap !== DARK ? DARK : SATELLITE)}
          >
            {baseMap === DARK ? "Dark" : "Satellite"}
          </button>
        </div>
        <DeckGL
          initialViewState={localViewPort}
          onWebGLInitialized={webGLInit}
          onViewStateChange={({ viewState }: any) => {
            const { latitude, longitude, zoom } = viewState;
            setLocalViewPort({ latitude, longitude, zoom });
          }}
          controller={{
            touchRotate: false,
            dragRotate: false,
          }}
          getTooltip={({ object }: any) =>
            object && object?.properties?.osm?.tags?.name
              ? JSON.stringify(object?.properties)
              : null
          }
          layers={searchResults.map((x, i) => {
            const layerStyle = layerStyles[i];
            return [
              new GeoJsonLayer({
                id: `geojson-layer-${i}-${layerStyle.id}`,
                data: x.parse_result.geom,
                pickingRadius: 5,
                getRadius: layerStyle.lineThicknessPx,
                getLineWidth: layerStyle.lineThicknessPx,
                opacity: layerStyle.opacity,
                filled: true,
                extruded: false,
                stroked: true,
                wireframe: true,
                pointRadiusMinPixels: 3,
                lineWidthMinPixels: 5,
                radiusMaxPixels: 3,
                getFillColor: layerStyle.paint,
                getLineColor: layerStyle.paint,
                pickable: true,
              }),
            ];
          })}
        >
          <StaticMap
            reuseMaps
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            attributionControl={false}
            mapStyle={baseMap}
          />
        </DeckGL>
      </div>
    </div>
  );
};

export default GeoMap;
