// @ts-ignore
import { MVTLayer } from "@deck.gl/geo-layers";
// @ts-ignore
import { PolygonLayer, GeoJsonLayer } from "@deck.gl/layers";
import { useEffect, useRef, useState } from "react";
import Map, { NavigationControl } from "react-map-gl";
import { MapView } from "@deck.gl/core/typed";

import { useUrlState } from "../../lib/hooks/url-state/use-url-state";
import { useZctaShapes } from "../../lib/hooks/census/use-zcta-shapes";

import { DeckGLOverlay } from "./deckgl-overlay";

import "mapbox-gl/dist/mapbox-gl.css";

const TILE_URL =
  "https://api.mercator.tech/backsplash/zcta/generate_shape_tile/{z}/{x}/{y}";
const ZOOM_TRANSITION = 6;

function genCommonProps(updateTriggersVars: any) {
  return {
    updateTriggers: {
      getFillColor: updateTriggersVars,
    },
    stroked: false,
    // // NOTE if we transition away from Mapbox-managed deck, we can use this again
    // transitions: {
    //   getFillColor: 500,
    // },
    filled: true,
    pickable: true,
    extruded: false,
    wireframe: false,
    autoHighlight: true,
    // beforeId: "admin_level",
    beforeId: "waterway-label",
  };
}

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
  queryLoading,
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
  queryLoading: boolean;
}) => {
  const mapRef = useRef<any>(null);
  const { zctaShapes } = useZctaShapes();

  const { currentStateFromUrl, updateUrlState } = useUrlState();
  const [initialized, setInitialized] = useState(false);

  const [localViewPort, setLocalViewPort] = useState({
    longitude: currentStateFromUrl()?.lng ?? -98.5795,
    latitude: currentStateFromUrl()?.lat ?? 39.8283,
    zoom: currentStateFromUrl()?.zoom ?? 3,
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

  return (
    <Map
      onMove={(evt) => {
        setLocalViewPort(evt.viewState);
      }}
      onMoveEnd={(evt) => {
        const { longitude, latitude, zoom } = evt.viewState;
        // Keep our URL state synced
        updateUrlState({
          lng: longitude,
          lat: latitude,
          zoom,
        });
      }}
      {...localViewPort}
      antialias={true}
      customAttribution={
        "Data from <a href='https://www.census.gov/programs-surveys/geography.html'>US Census, </a>  <a href='https://mercator.tech'>processed by Mercator </a>"
      }
      style={
        {
          width: "100vw",
          height: "100%",
          top: 0,
          left: 0,
          position: "absolute",
        } as any
      }
      onZoom={(evt) => {
        setLocalViewPort(evt.viewState);
        onZoom(evt.viewState.zoom);
      }}
      initialViewState={localViewPort}
      ref={mapRef}
      mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      mapStyle={baseMap}
    >
      <NavigationControl position="bottom-right" />
      <DeckGLOverlay
        mapboxRef={mapRef}
        views={[
          new MapView({
            id: "mapbox-view",
          }),
        ]}
        onWebGLInitialized={() => {
          // @ts-ignore
          mapRef.current.getMap().on("load", () => {
            // @ts-ignore
            mapRef.current.getMap().resize();
          });
        }}
        interleaved={true}
        onHover={({ object }: any) => {
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
            id: "usa",
            data: "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            getOffset: [0, 0],
            visible: zctaLookup ? 1 : 0,
            getFillColor: colors[0],
            stroked: false,
            beforeId: "waterway-label", // Insert before this Mapbox layer
          }),
          new PolygonLayer({
            layerName: "zcta-high",
            id: "zcta-high",
            visible: localViewPort.zoom <= ZOOM_TRANSITION && !queryLoading,
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
            getOffset: [0, 1],
            data: zctaShapes,
            getPolygon: (d: any) => {
              return d.geom;
            },
            ...genCommonProps([selectedColumn, zctaLookup, colors, scale]),
          }),
          new MVTLayer({
            layerName: "zcta-low",
            id: "zcta-low",
            data: TILE_URL,
            visible: localViewPort.zoom > ZOOM_TRANSITION && !queryLoading,
            maxRequests: -1,
            getOffset: [0, 1],
            uniqueIdProperty: "zcta",
            getFillColor: (d: any) => {
              if (!zctaLookup) return colors[0];
              try {
                const val = zctaLookup[d.properties.zcta][selectedColumn];
                const color = scale(val);
                return color;
              } catch (e) {
                return [0, 0, 0, 0];
              }
            },
            ...genCommonProps([selectedColumn, zctaLookup, colors, scale]),
          }),
        ]}
      />
    </Map>
  );
};
