import { GeoJsonLayer } from "@deck.gl/layers";
import { useIdToken } from "../use-id-token";
import { useShapes } from "../use-shapes";
import { useSelectedShapes } from "../use-selected-shapes";
import { useCallback, useEffect, useState } from "react";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
// import { CxMVTLayer, TileCache } from "../../../../common/cx-mvt-layer";
import { MVTLayer } from "@deck.gl/geo-layers";

export function useTiles() {
  const { idToken } = useIdToken();

  const tileArgs = useTileArgs();

  if (idToken === null) {
    return null;
  }
  return ["geofence-mvt"].map(
    (id) =>
      new MVTLayer({
        id,
        // @ts-ignore
        ...tileArgs,
      })
  );
}

const useTileArgs = () => {
  const { idToken } = useIdToken();
  const { tileCacheKey, visibleNamepaces, numShapes } = useShapes();
  const [isHovering, setIsHovering] = useState<string | null>(null);

  const { isSelected, selectedUuids, selectOneShapeUuid } = useSelectedShapes();

  const { cursorMode } = useCursorMode();

  const getTileUrl = useCallback(() => {
    if (visibleNamepaces.length === 0) {
      return (
        process.env.REACT_APP_BACKEND_URL +
        "/backsplash/generate_shape_tile/{z}/{x}/{y}"
      );
    }
    const namespacesAsParams = visibleNamepaces.map(
      (x) => `namespace_ids=${x.id}`
    );
    return (
      process.env.REACT_APP_BACKEND_URL +
      `/backsplash/generate_shape_tile/{z}/{x}/{y}?${namespacesAsParams.join(
        "&"
      )}`
    );
  }, [visibleNamepaces, numShapes]);

  useEffect(() => {
    setIsHovering(null);
  }, [cursorMode]);

  if (visibleNamepaces.length === 0 && numShapes != null && numShapes > 0) {
    return [];
  }

  return {
    // @ts-ignore
    lineWidthMinPixels: 1,
    data: getTileUrl(),
    loadOptions: {
      fetch: {
        method: "GET",
        caches: "max-age=0",
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      },
    },
    onHover: ({ object, x, y }: any) => {
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
        }
      }
    },
    onClick: ({ object, x, y }: any) => {
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
        }
      }
    },
    pickable: true,
    // maxRequests: 4, // TODO need to upgrade to HTTP/2
    maxRequests: -1, // unlimited connections, using HTTP/2
    getLineColor: [255, 255, 255, 255],
    updateTriggers: {
      getFillColor: [selectedUuids, isHovering],
      getTileData: [tileCacheKey, visibleNamepaces],
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
    maxCacheByteSize: 0,
    renderSubLayers: (props: any) => {
      return new GeoJsonLayer({
        ...props,
      });
    },
  };
};
