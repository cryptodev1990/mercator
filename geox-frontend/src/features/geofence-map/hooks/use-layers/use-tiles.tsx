import { GeoJsonLayer } from "@deck.gl/layers";
import { useIdToken } from "../use-id-token";
import { useShapes } from "../use-shapes";
import { useSelectedShapes } from "../use-selected-shapes";
import { findIndex } from "../../../../common/utils";
import { useEffect, useMemo, useState } from "react";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { CxMVTLayer, TileCache } from "../../../../common/cx-mvt-layer";

export function useTiles() {
  const { idToken } = useIdToken();

  const tileCache = useMemo(() => {
    return new TileCache();
  }, []);

  const tileArgs = useTileArgs();

  const { updatedShapeIds } = useShapes();

  useEffect(() => {
    const numCleared = tileCache.clearForFeatures(updatedShapeIds);
    if (numCleared > 0) {
      console.log(`Cleared ${numCleared} features from cache`);
    } else {
      // clear all
      // This currently applies in the "add shape" case
      tileCache.clear();
    }
  }, [updatedShapeIds, tileCache]);

  if (idToken === null) {
    return null;
  }
  return ["geofence-mvt"].map(
    (id) =>
      new CxMVTLayer({
        id,
        // @ts-ignore
        cache: tileCache,
        ...tileArgs,
      })
  );
}

const useTileArgs = () => {
  const { idToken } = useIdToken();
  const { shapeMetadata, scrollToSelectedShape, tileCacheKey } = useShapes();
  const [isHovering, setIsHovering] = useState<string | null>(null);

  const { isSelected, selectedUuids, selectOneShapeUuid } = useSelectedShapes();

  const slideToCard = (uuid: string) => {
    const i = findIndex(uuid, shapeMetadata);
    scrollToSelectedShape(i);
  };
  const { cursorMode } = useCursorMode();

  useEffect(() => {
    setIsHovering(null);
  }, [cursorMode]);

  return {
    // @ts-ignore
    lineWidthMinPixels: 1,
    data:
      process.env.REACT_APP_BACKEND_URL +
      "/backsplash/generate_shape_tile/{z}/{x}/{y}" +
      `/0`,
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
          slideToCard(uuid);
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
          slideToCard(uuid);
        }
      }
    },
    pickable: true,
    // maxRequests: 4, // TODO need to upgrade to HTTP/2
    maxRequests: -1, // unlimited connections, using HTTP/2
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
    maxCacheByteSize: 0,
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
  };
};
