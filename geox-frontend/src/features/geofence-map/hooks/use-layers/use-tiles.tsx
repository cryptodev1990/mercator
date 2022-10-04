import { GeoJsonLayer } from "@deck.gl/layers";
import { MVTLayer } from "@deck.gl/geo-layers";
import { useIdToken } from "../use-id-token";
import { useShapes } from "../use-shapes";
import { useSelectedShapes } from "../use-selected-shapes";
import { findIndex } from "../../../../common/utils";
import { useContext } from "react";
import { DeckContext } from "../../contexts/deck-context";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";

export function useTiles() {
  const { tileCacheKey } = useContext(DeckContext);
  const { idToken } = useIdToken();

  const { shapeMetadata, scrollToSelectedShape, selectOneShapeUuid } =
    useShapes();

  const slideToCard = (uuid: string) => {
    const i = findIndex(uuid, shapeMetadata);
    scrollToSelectedShape(i);
  };

  const { isSelected, selectedUuids } = useSelectedShapes();
  const { cursorMode } = useCursorMode();

  if (idToken === null) {
    return null;
  }

  return new MVTLayer({
    id: "geofence-mvt",
    // @ts-ignore
    lineWidthMinPixels: 1,
    data:
      process.env.REACT_APP_BACKEND_URL +
      "/backsplash/generate_shape_tile/{z}/{x}/{y}" +
      `/${tileCacheKey}`,
    loadOptions: {
      fetch: {
        method: "GET",
        caches: "max-age=0",
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      },
    },
    onHover: ({ object, x, y }) => {
      // @ts-ignore
      if (object?.properties?.__uuid && cursorMode !== EditorMode.SplitMode) {
        // TODO how do I get TypeScript to recognize the type on object here?
        // @ts-ignore
        const { __uuid: uuid } = object.properties;
        if (!isSelected(uuid)) {
          selectOneShapeUuid(uuid);
          slideToCard(uuid);
        }
      }
    },
    onClick: ({ object, x, y }) => {
      // @ts-ignore
      if (object?.properties?.__uuid) {
        // TODO how do I get TypeScript to recognize the type on object here?
        // @ts-ignore
        const { __uuid: uuid } = object.properties;
        if (!isSelected(uuid)) {
          selectOneShapeUuid(uuid);
          slideToCard(uuid);
        }
      }
    },
    pickable: true,
    maxRequests: 4, // TODO need to upgrade to HTTP/2
    // maxRequests: -1, // unlimited connections, using HTTP/2
    getLineColor: [192, 192, 192, 255],
    updateTriggers: {
      getFillColor: [selectedUuids],
      getTileData: [tileCacheKey],
    },
    getFillColor: (d: any) => {
      if (isSelected(d.properties.__uuid)) {
        // salmon in rgba
        return [250, 128, 114, 150];
      }
      return [140, 170, 180, 200];
    },
    maxCacheSize: 0,
    // transitions: {
    // getFillColor: {
    // duration: 300,
    // @ts-ignore
    // enter: () => [0, 0, 0, 0], //
    // },
    // },
    renderSubLayers: (props: any) => {
      return new GeoJsonLayer({
        data: props.data,
        pickable: true,
        stroked: true,
        filled: true,
        getElevation: 0,
        ...props,
      });
    },
  });
}