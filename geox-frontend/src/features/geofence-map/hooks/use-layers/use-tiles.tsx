import { GeoJsonLayer } from "@deck.gl/layers";
import { MVTLayer } from "@deck.gl/geo-layers";
import { useIdToken } from "../use-id-token";
import { useShapes } from "../use-shapes";
import { useSelectedShapes } from "../use-selected-shapes";
import { findIndex } from "../../../../common/utils";
import { useEffect, useState } from "react";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";

export function useTiles() {
  const { idToken } = useIdToken();

  const { shapeMetadata, scrollToSelectedShape, tileCacheKey } = useShapes();

  const slideToCard = (uuid: string) => {
    const i = findIndex(uuid, shapeMetadata);
    scrollToSelectedShape(i);
  };

  const { isSelected, selectedUuids, selectOneShapeUuid } = useSelectedShapes();
  const [isHovering, setIsHovering] = useState<string | null>(null);
  const { cursorMode } = useCursorMode();

  useEffect(() => {
    setIsHovering(null);
  }, [cursorMode]);

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
      if (
        // @ts-ignore
        object?.properties?.__uuid &&
        EditorMode.ModifyMode === cursorMode
      ) {
        // @ts-ignore
        setIsHovering(object?.properties?.__uuid);
      }
      // @ts-ignore
      if (object?.properties?.__uuid && cursorMode === EditorMode.ViewMode) {
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
      if (cursorMode === EditorMode.SplitMode) {
        return;
      }
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
    getLineColor: [255, 255, 255, 255],
    updateTriggers: {
      getFillColor: [selectedUuids, isHovering],
      getTileData: [tileCacheKey],
    },
    getFillColor: (d: any) => {
      if (isSelected(d.properties.__uuid)) {
        // salmon in rgba
        return [250, 128, 114, 150];
      }
      if (isHovering === d.properties.__uuid) {
        // light blue in rgba
        return [173, 216, 230, 150];
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
    transitions: {
      getFillColor: {
        duration: 300,
        // @ts-ignore
        enter: () => [140, 170, 180, 200], //
      },
    },
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
