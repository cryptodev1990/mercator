import { useCallback, useEffect, useState } from "react";
// @ts-ignore
import DeckGL, { GeoJsonLayer, FlyToInterpolator } from "deck.gl";
import StaticMap from "react-map-gl";
import { snapToBounds } from "../../../src/lib/geo-utils";
import { useSelector } from "react-redux";
import { selectSearchState } from "src/search/search-slice";

type Viewport = {
  latitude: number;
  longitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
  width?: number;
  height?: number;
};

const GeoMap = () => {
  const { searchResults } = useSelector(selectSearchState);
  // deck.gl map with a GeoJsonLayer

  const [viewport, setViewport] = useState<Viewport>({
    latitude: 37.7577,
    longitude: -122.4376,
    zoom: 8,
    bearing: 0,
    pitch: 0,
  });

  useEffect(() => {
    if (searchResults.length > 0) {
      fitViewport();
    }
  }, [searchResults]);

  const fitViewport = useCallback(() => {
    // TODO handle the feature collection here
    const newBounds = snapToBounds(
      // @ts-ignore
      searchResults[searchResults.length - 1].results
    );
    if (newBounds) {
      setViewport({
        ...newBounds,
        // @ts-ignore
        // transitionDuration: 1000,
      });
    }
  }, [searchResults]);

  return (
    <div className="w-full h-full">
      <div className="w-full h-full">
        <DeckGL
          initialViewState={viewport}
          controller={true}
          onViewStateChange={({ viewState }: any) => setViewport(viewState)}
          getTooltip={({ object }: any) =>
            object && object?.properties?.osm?.tags?.name
          }
          layers={searchResults.map((x, i) => [
            new GeoJsonLayer({
              id: `geojson-layer-${i}`,
              data: x.results,
              stroked: false,
              getRadius: 100,
              filled: true,
              extruded: false,
              wireframe: true,
              lineWidthMinPixels: 1,
              getFillColor: [
                Math.abs(255 - 20 * i) % 255,
                Math.abs(255 - 20 * i) % 255,
                (50 * i) % 255,
              ],
              pickable: true,
            }),
          ])}
        >
          <StaticMap
            reuseMaps
            mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
            attributionControl={false}
            mapStyle="mapbox://styles/mapbox/dark-v9"
          />
        </DeckGL>
      </div>
    </div>
  );
};

export default GeoMap;
