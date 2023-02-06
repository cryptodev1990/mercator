// @ts-ignore
import { MVTLayer } from "@deck.gl/geo-layers";
// @ts-ignore
import { PolygonLayer, GeoJsonLayer } from "@deck.gl/layers";
import StaticMap from "react-map-gl";
// @ts-ignore
import DeckGL from "deck.gl";
import { useEffect, useRef, useState } from "react";
import { useZctaShapes } from "../../lib/hooks/use-zcta-shapes";

const TILE_URL =
  "https://api.mercator.tech/backsplash/zcta/generate_shape_tile/{z}/{x}/{y}";
const ZOOM_TRANSITION = 7.1;

export const DeckMap = ({
  zctaLookup,
  selectedColumn,
  selectedZcta,
  setSelectedZcta,
  deckContainerRef,
  colors,
  scale,
  baseMap,
  onZoom,
}: {
  zctaLookup: any;
  selectedColumn: string;
  selectedZcta: string;
  setSelectedZcta: (zcta: string) => void;
  deckContainerRef: React.RefObject<HTMLDivElement>;
  colors: number[][];
  scale: (d: number) => string;
  baseMap: string;
  onZoom: (zoom: number) => void;
}) => {
  const deckRef = useRef<DeckGL | null>(null);
  const { zctaShapes } = useZctaShapes();

  const [localViewPort, setLocalViewPort] = useState({
    longitude: -98.5795,
    latitude: 39.8283,
    zoom: 3,
    bearing: 0,
    pitch: 0,
  });

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

  useEffect(() => {
    if (localViewPort) {
      onZoom(localViewPort.zoom);
    }
  }, [localViewPort]);

  return (
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
        if (!object && !selectedZcta) {
          return;
        }
        if (!object) {
          setSelectedZcta("");
          return;
        }
        console.log(object);
        const zcta =
          object?.zcta ||
          object?.properties.zcta ||
          object?.properties.ZCTA5CE10;
        setSelectedZcta(zcta);
      }}
      onClick={({ object }: any) => {
        if (!object) {
          setSelectedZcta("");
        }
        const zcta =
          object?.zcta ||
          object?.properties?.zcta ||
          object?.properties?.ZCTA5CE10;
        if (zcta === selectedZcta) {
          setSelectedZcta("");
          return;
        }
        setSelectedZcta(zcta);
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
            getFillColor: [selectedColumn, zctaLookup, colors],
          },
          getPolygon: (d: any) => {
            return d.geom;
          },
          getFillColor: (d: any) => {
            if (!zctaLookup) return colors[0];
            try {
              const val = zctaLookup[d.zcta][selectedColumn];
              const color = scale(val);
              return color;
            } catch (e) {
              return [0, 0, 0, 0];
            }
          },
          stroked: true,
          transitions: {
            getFillColor: 500,
          },
          filled: true,
          pickable: true,
          extruded: false,
          wireframe: false,
          opacity: 1,
          autoHighlight: true,
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
            getFillColor: [selectedColumn, zctaLookup, colors],
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
              const val = zctaLookup[zcta][selectedColumn];
              const color = scale(val);
              return color;
            } catch (e) {
              return [0, 0, 0, 0];
            }
          },
          uniqueIdProperty: "zcta",
          pickable: true,
          autoHighlight: true,
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
  );
};
