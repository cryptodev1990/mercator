import { useCallback, useEffect, useState } from "react";
// @ts-ignore
import DeckGL, { GeoJsonLayer, FlyToInterpolator } from "deck.gl";
import StaticMap from "react-map-gl";
import { snapToBounds } from "../../../src/lib/geo-utils";
import { useDispatch, useSelector } from "react-redux";
import { selectSearchState } from "src/search/search-slice";
import clsx from "clsx";
import { selectGeoMapState, setViewport } from "src/shapes/shape-slice";

const DARK = "mapbox://styles/mapbox/dark-v9";
const SATELLITE = "mapbox://styles/mapbox/satellite-v9";

const GeoMap = () => {
  const { searchResults } = useSelector(selectSearchState);
  const { viewport } = useSelector(selectGeoMapState);
  const [localViewPort, setLocalViewPort] = useState(viewport);
  // deck.gl map with a GeoJsonLayer
  const dispatch = useDispatch();

  const [baseMap, setBaseMap] = useState(DARK);

  useEffect(() => {
    setLocalViewPort({ ...viewport });
  }, [viewport]);

  // After 500 ms of inactivity, set the global viewport to be the local viewport
  useEffect(() => {
    const timeout = setTimeout(() => {
      dispatch(setViewport({ ...localViewPort }));
    }, 500);
    return () => clearTimeout(timeout);
  }, [localViewPort, dispatch]);

  useEffect(() => {
    if (searchResults.length > 0) {
      const bounds = snapToBounds(
        // @ts-ignore
        searchResults[searchResults.length - 1].results
      );
      if (bounds) {
        setLocalViewPort({
          ...localViewPort,
          longitude: bounds?.longitude,
          latitude: bounds?.latitude,
          zoom: 12,
          // @ts-ignore
          transitionDuration: 1000,
          transitionInterpolator: new FlyToInterpolator(),
        });
      }
    }
  }, [searchResults, localViewPort]);

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
          }
          layers={searchResults.map((x, i) => [
            new GeoJsonLayer({
              id: `geojson-layer-${i}`,
              data: x.results,
              getRadius: 100,
              filled: true,
              extruded: false,
              stroked: true,
              wireframe: true,
              lineWidthMinPixels: 1,
              radiusMinPixels: 1,
              radiusMaxPixels: 1,
              getFillColor: [255, 0, 0],
              getLineColor: [255, 0, 0],
              pickable: true,
            }),
          ])}
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
