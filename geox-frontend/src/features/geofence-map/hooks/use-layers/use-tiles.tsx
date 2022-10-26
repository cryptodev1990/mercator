import { GeoJsonLayer } from "@deck.gl/layers";
import { useIdToken } from "../use-id-token";
import { useShapes } from "../use-shapes";
import { useSelectedShapes } from "../use-selected-shapes";
import { useCallback, useEffect, useState } from "react";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { CxMVTLayer, TileCache } from "../../../../common/cx-mvt-layer";
import Tile2DHeader from "@deck.gl/geo-layers/tile-layer/tile-2d-header";

import GL from "@luma.gl/constants";

const tc = new TileCache();

export function useTiles() {
  const { idToken } = useIdToken();

  const [isHovering, setIsHovering] = useState<string | null>(null);
  const [updateCount, setUpdateCount] = useState(0);
  const tileArgs = useTileArgs(isHovering, setIsHovering);
  const { tileCacheKey, visibleNamepaces, updatedShapeIds } = useShapes();
  const { selectedUuids } = useSelectedShapes();

  useEffect(() => {
    tc.clearForFeatures(updatedShapeIds);
  }, [updatedShapeIds]);

  if (idToken === null) {
    return null;
  }
  if (visibleNamepaces.length === 0) {
    return null;
  }

  return [
    new CxMVTLayer({
      id: "gf-mvt",
      // @ts-ignore
      cache: tc,
      // @ts-ignore
      onViewportLoad: (headers: Tile2DHeader[]) => {
        // triggers after all tiles in a viewport load
        tc.clear();
        setUpdateCount(updateCount + 1);
      },
      updateTriggers: {
        getFillColor: [selectedUuids, isHovering],
        getTileData: [tileCacheKey, visibleNamepaces],
      },
      // @ts-ignore
      ...tileArgs,
    }),
    new CxMVTLayer({
      id: "bg-mvt",
      // @ts-ignore
      cache: tc,
      updateTriggers: {
        getTileData: [updateCount],
        getFillColor: [selectedUuids, isHovering],
      },
      // @ts-ignore
      ...tileArgs,
    }),
  ];
}

const useTileArgs = (isHovering: any, setIsHovering: any) => {
  const { idToken } = useIdToken();
  const { visibleNamepaces, numShapes } = useShapes();

  const { isSelected, selectOneShapeUuid } = useSelectedShapes();

  const { cursorMode } = useCursorMode();

  useEffect(() => {
    setIsHovering(null);
  }, [cursorMode]);

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
  return {
    // @ts-ignore
    lineWidthMinPixels: 2,
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
    opacity: 0.2,
    parameters: {
      // don't blend two layers
      blend: true,
      blendFunc: [
        GL.SRC_ALPHA,
        GL.SRC_ALPHA,
        GL.ONE_MINUS_CONSTANT_ALPHA,
        GL.DST_COLOR,
      ],
    },
    getLineColor: [0, 0, 0, 150],
    getFillColor: (d: any) => {
      if (isSelected(d.properties.__uuid)) {
        // hidden
        return [250, 128, 114, 0];
      }
      if (isHovering === d.properties.__uuid) {
        // light blue in rgba
        return [173, 216, 230];
      }
      return [140, 170, 180];
    },
    extruded: false,
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
    maxRequests: -1, // unlimited connections, using HTTP/2
    maxCacheSize: 0,
    maxCacheByteSize: 0,
    renderSubLayers: (props: any) => {
      return new GeoJsonLayer({
        ...props,
      });
    },
  };
};
