import { useIdToken } from "../use-id-token";
import { useShapes } from "../use-shapes";
import { useCallback, useContext, useEffect } from "react";
import { MVTLayer } from "@deck.gl/geo-layers";
import { GeoJsonLayer } from "@deck.gl/layers";
import { geoShapesToFeatureCollection } from "../../utils";
import { DeckContext } from "../../contexts/deck-context";
import { useSelectedShapes } from "../use-selected-shapes";
import { useCursorMode } from "../use-cursor-mode";
import { EditorMode } from "../../cursor-modes";

const MAX_OPTIMISTIC_FEATURES = 30;

export function useTiles() {
  const { idToken } = useIdToken();
  const { hoveredUuid } = useContext(DeckContext);

  const tileArgs = useTileArgs();
  const {
    visibleNamespaces,
    deletedShapeIdSet,
    updatedShapeIdSet,
    optimisticShapeUpdates,
    clearOptimisticShapeUpdates,
    tileUpdateCount,
    setTileUpdateCount,
  } = useShapes();

  const { cursorMode } = useCursorMode();

  const { isSelected, selectedUuids } = useSelectedShapes();

  useEffect(() => {
    if (optimisticShapeUpdates.length > MAX_OPTIMISTIC_FEATURES) {
      clearOptimisticShapeUpdates();
      setTileUpdateCount(tileUpdateCount + 1);
    }
  }, [optimisticShapeUpdates]);

  if (idToken === null) {
    return null;
  }
  if (visibleNamespaces.length === 0) {
    return null;
  }

  const commonArgs = {
    lineWidthMinPixels: 2,
    pickable: true,
    extruded: false,
  };
  return [
    // @ts-ignore
    new GeoJsonLayer({
      id: "optimistic-layer",
      // @ts-ignore
      data: geoShapesToFeatureCollection(optimisticShapeUpdates),
      updateTriggers: {
        getLineColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          selectedUuids,
        ],
        getFillColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          hoveredUuid,
          selectedUuids,
        ],
      },
      getLineColor: (d: any) => {
        const uuid = d?.properties?.__uuid;
        if (deletedShapeIdSet.has(uuid)) {
          return [0, 0, 0, 0];
        }
        if (cursorMode === EditorMode.ModifyMode && isSelected(uuid)) {
          return [0, 0, 0, 0];
        }
        if (isSelected(uuid)) return [0, 0, 255, 50];
        if (hoveredUuid === uuid) return [255, 125, 0, 150];
        return [0, 0, 0, 150];
      },
      getFillColor: (d: any) => {
        // light blue in rgba
        const uuid = d?.properties?.__uuid;
        if (deletedShapeIdSet.has(uuid)) {
          return [0, 0, 0, 0];
        }
        if (cursorMode === EditorMode.ModifyMode && isSelected(uuid)) {
          return [0, 0, 0, 0];
        }
        if (isSelected(uuid)) return [0, 0, 255, 50];
        if (hoveredUuid === uuid) return [255, 125, 0, 150];
        return [173, 216, 230, 255];
      },
      ...commonArgs,
    }),
    new MVTLayer({
      id: "gf-mvt",
      // @ts-ignore
      getLineColor: (d: any) => {
        const uuid = d?.properties?.__uuid;
        if (deletedShapeIdSet.has(uuid) || updatedShapeIdSet.has(uuid)) {
          return [0, 0, 0, 0];
        }
        if (isSelected(uuid)) return [0, 0, 255, 50];
        if (hoveredUuid === uuid) return [255, 125, 0, 150];
        return [0, 0, 0, 150];
      },
      getFillColor: (d: any) => {
        const uuid = d?.properties?.__uuid;
        if (deletedShapeIdSet.has(uuid) || updatedShapeIdSet.has(uuid)) {
          return [0, 0, 0, 0];
        }
        if (isSelected(uuid)) return [0, 0, 255, 50];
        if (hoveredUuid === uuid) return [255, 125, 0, 150];
        return [173, 216, 230, 255];
      },
      updateTriggers: {
        getLineColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          hoveredUuid,
          selectedUuids,
        ],
        getFillColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          selectedUuids,
        ],
        getTileData: [tileUpdateCount],
      },
      ...tileArgs,
      ...commonArgs,
    }),
  ];
}

const useTileArgs = () => {
  const { idToken } = useIdToken();
  const { visibleNamespaces, numShapes } = useShapes();

  const getTileUrl = useCallback(() => {
    if (visibleNamespaces.length === 0) {
      return (
        process.env.REACT_APP_BACKEND_URL +
        "/backsplash/generate_shape_tile/{z}/{x}/{y}"
      );
    }
    const namespacesAsParams = visibleNamespaces.map(
      (x) => `namespace_ids=${x.id}`
    );
    return (
      process.env.REACT_APP_BACKEND_URL +
      `/backsplash/generate_shape_tile/{z}/{x}/{y}?${namespacesAsParams.join(
        "&"
      )}`
    );
  }, [visibleNamespaces, numShapes]);

  return {
    // @ts-ignore
    data: getTileUrl(),
    maxRequests: 6,
    loadOptions: {
      fetch: {
        method: "GET",
        caches: "max-age=0",
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      },
    },
  };
};
