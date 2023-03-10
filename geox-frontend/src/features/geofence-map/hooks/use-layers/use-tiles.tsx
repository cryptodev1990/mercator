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
import { useGetNamespaces } from "../use-openapi-hooks";
import { useSelectedShapesUuids } from "../use-selected-shapes-uuids";

const MAX_OPTIMISTIC_FEATURES = 30;

export function useTiles() {
  const { idToken } = useIdToken();
  const { hoveredUuid } = useContext(DeckContext);

  const tileArgs = useTileArgs();
  const {
    visibleNamespaceIDs,
    deletedShapeIdSet,
    updatedShapeIdSet,
    optimisticShapeUpdates,
    clearOptimisticShapeUpdates,
    tileUpdateCount,
    setTileUpdateCount,
    tilePropertyChange,
  } = useShapes();

  const { cursorMode } = useCursorMode();

  const selectedShapesUuids = useSelectedShapesUuids();

  const { data: allNamespaces } = useGetNamespaces();

  useEffect(() => {
    if (optimisticShapeUpdates.length > MAX_OPTIMISTIC_FEATURES) {
      clearOptimisticShapeUpdates();
      setTileUpdateCount(tileUpdateCount + 1);
    }
  }, [optimisticShapeUpdates]);

  if (idToken === null) {
    return null;
  }
  if (visibleNamespaceIDs.length === 0) {
    return null;
  }

  console.log("optimisticShapeUpdates", optimisticShapeUpdates);

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
          selectedShapesUuids.length,
        ],
        getFillColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          hoveredUuid,
          selectedShapesUuids.length,
        ],
      },
      getLineColor: (d: any) => {
        const uuid = d?.properties?.__uuid;
        if (deletedShapeIdSet.has(uuid)) {
          return [0, 0, 0, 0];
        }
        if (
          (cursorMode === EditorMode.ModifyMode ||
            cursorMode === EditorMode.SplitMode) &&
          selectedShapesUuids.includes(uuid)
        ) {
          return [0, 0, 0, 0];
        }
        if (selectedShapesUuids.includes(uuid)) return [0, 0, 255];
        if (hoveredUuid === uuid) return [255, 125, 0, 150];
        return [0, 0, 0, 150];
      },
      getFillColor: (d: any) => {
        // light blue in rgba
        const uuid = d?.properties?.__uuid;
        const optimisticShape: any = optimisticShapeUpdates.find(
          (shape) => shape.uuid === uuid
        );
        const namespace = allNamespaces?.find(
          (namespace) => namespace.id === optimisticShape?.namespace_id
        );
        if (namespace?.properties?.color) {
          const color = namespace?.properties?.color;
          return [color.r, color.g, color.b];
        }
        if (deletedShapeIdSet.has(uuid)) {
          return [0, 0, 0, 0];
        }
        if (
          (cursorMode === EditorMode.ModifyMode ||
            cursorMode === EditorMode.SplitMode) &&
          selectedShapesUuids.includes(uuid)
        ) {
          return [0, 0, 0, 0];
        }
        if (selectedShapesUuids.includes(uuid)) return [0, 0, 255];
        if (hoveredUuid === uuid) return [0, 0, 255, 50];
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
        if (hoveredUuid === uuid) return [255, 125, 0];
        return [0, 0, 0];
      },
      getFillColor: (d: any) => {
        const uuid = d?.properties?.__uuid;
        if (
          deletedShapeIdSet.has(uuid) ||
          updatedShapeIdSet.has(uuid) ||
          selectedShapesUuids.includes(uuid)
        ) {
          return [0, 0, 0, 0];
        }
        const namespace_id = d?.properties?.__namespace_id;
        const namespace = allNamespaces?.find(
          (namespace) => namespace.id === namespace_id
        );
        if (namespace?.properties?.color) {
          const color = namespace?.properties?.color;
          return [color.r, color.g, color.b];
        }

        return [173, 216, 230];
      },
      updateTriggers: {
        getLineColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          hoveredUuid,
          visibleNamespaceIDs.length,
        ],
        getFillColor: [
          deletedShapeIdSet.size,
          updatedShapeIdSet.size,
          tilePropertyChange,
          hoveredUuid,
          selectedShapesUuids.length,
          visibleNamespaceIDs.length,
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
  const { visibleNamespaceIDs, numShapes } = useShapes();

  const getTileUrl = useCallback(() => {
    if (visibleNamespaceIDs.length === 0) {
      return (
        process.env.REACT_APP_BACKEND_URL +
        "/backsplash/generate_shape_tile/{z}/{x}/{y}"
      );
    }
    const namespacesAsParams = visibleNamespaceIDs.map(
      (namespaceID: string) => `namespace_ids=${namespaceID}`
    );
    return (
      process.env.REACT_APP_BACKEND_URL +
      `/backsplash/generate_shape_tile/{z}/{x}/{y}?${namespacesAsParams.join(
        "&"
      )}`
    );
  }, [visibleNamespaceIDs, numShapes]);

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
