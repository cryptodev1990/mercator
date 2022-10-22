// @ts-ignore
import { _GlobeView } from "@deck.gl/core";
import { DeckGL } from "@deck.gl/react";
import { GeoJsonLayer, SolidPolygonLayer } from "@deck.gl/layers";
import { useEffect, useState } from "react";
import countries from "./globe.json";
// const countries =
//   "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson";

export const Globe = (): JSX.Element => {
  const [initialViewState, setInitialViewState] = useState({
    longitude: 2.27,
    latitude: 48.86,
    zoom: 0,
    minZoom: 0,
    maxZoom: 0,
  });

  const [rotate, setRotate] = useState(true);

  useEffect(() => {
    if (!rotate) {
      return;
    }
    const intervalId = setInterval(() => {
      setInitialViewState({
        ...initialViewState,
        longitude: initialViewState.longitude - 0.5,
      });
    }, 50);

    return () => {
      clearInterval(intervalId);
    };
  }, [initialViewState, rotate]);

  return (
    <div onMouseLeave={() => setRotate(true)}>
      <DeckGL
        initialViewState={initialViewState}
        controller={{
          keyboard: true,
          scrollZoom: false,
        }}
        getCursor={() => "crosshair"}
        onDragStart={() => {
          setRotate(false);
        }}
        onDragEnd={(args) => {
          // @ts-ignore
          const { viewport } = args; // TODO: why this typescript error
          setInitialViewState({
            ...initialViewState,
            latitude: viewport.latitude,
            longitude: viewport.longitude,
          });
        }}
        parameters={{ cull: true }}
        layers={[
          new GeoJsonLayer({
            data: countries,
            getPolygonOffset: ({ layerIndex }) => [0, -layerIndex * 100],
            opacity: 0.0,
            stroked: false,
            filled: true,
          }),
          new SolidPolygonLayer({
            id: "background",
            data: [
              [
                [-180, 90],
                [0, 90],
                [180, 90],
                [180, -90],
                [0, -90],
                [-180, -90],
              ],
            ],
            getPolygonOffset: ({ layerIndex }) => [0, -layerIndex],
            getPolygon: (d: any) => d,
            // stroked: false,
            filled: true,
            getFillColor: [255, 255, 255],
          }),
        ]}
        views={[new _GlobeView()]}
      ></DeckGL>
    </div>
  );
};
