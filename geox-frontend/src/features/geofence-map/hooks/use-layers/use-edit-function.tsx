// EditableGeojsonLayer function
import {
  GeoShapeCreate,
  MultiPolygon,
  GeoShapeMetadata,
  Polygon,
} from "../../../../client";
import { Feature, unkinkPolygon, kinks, union } from "@turf/turf";

import { useShapes } from "../use-shapes";
import { toast } from "react-hot-toast";
import { useCursorMode } from "../use-cursor-mode";
import { EditorMode } from "../../cursor-modes";
import { useSelectedShapes } from "../use-selected-shapes";
import { useBulkDeleteShapesMutation } from "../use-openapi-hooks";

function injectJitterToPolygon(polygon: MultiPolygon | Polygon): MultiPolygon {
  const jitter = 0.0000000001;
  return {
    ...polygon,
    coordinates: polygon.coordinates.map((ring) =>
      // @ts-ignore
      ring.map(([lon, lat]: number[]) => [
        lon + jitter * Math.random(),
        lat + jitter * Math.random(),
      ])
    ),
  };
}

export function useEditFunction() {
  const {
    shapeMetadata,
    setShapeForPropertyEdit,
    selectedFeatureIndexes,
    clearSelectedFeatureIndexes,
    bulkAddFromSplit,
    addShapeAndEdit,
    setTileUpdateCount,
  } = useShapes();

  const { mutate: deleteShapesRaw } = useBulkDeleteShapesMutation();

  const { clearSelectedShapeUuids, numSelected, selectedUuids } =
    useSelectedShapes();
  const { cursorMode, setCursorMode } = useCursorMode();
  const { clearOptimisticShapeUpdates } = useShapes();
  function onEdit({
    updatedData,
    editType,
    editContext,
  }: {
    updatedData: any;
    editType: string;
    editContext: any;
  }) {
    // Feature: split a shape
    if (editType === "split") {
      // TODO this has to be rethought
      // we either split the shape on the server or
      // we have an EditableGeojsonLayer that only has the selected shapes in it
      let multiPolygon: Feature<MultiPolygon> = updatedData.features[0];
      const cut = multiPolygon.geometry.coordinates[0];
      const rest = multiPolygon.geometry.coordinates.slice(1);

      if (numSelected > 1 || selectedFeatureIndexes.length > 1) {
        toast.error("Split should not select more than one shape");
        return;
      }
      const uuid = selectedUuids[0];

      const shape = shapeMetadata.find((x) => x.uuid === uuid);
      const name = shape?.name ?? "New shape";
      const namespaceId = shape?.namespace_id;
      delete multiPolygon?.properties?.__uuid;
      const payload: GeoShapeCreate[] = [
        {
          geojson: {
            type: "Feature",
            geometry: {
              type: "MultiPolygon",
              coordinates: [cut] as any,
            },
            properties: {
              ...multiPolygon.properties,
              __parent_uuid: uuid,
            },
          },
          name,
          namespace: namespaceId,
        },
        {
          geojson: {
            type: "Feature",
            geometry: {
              type: "MultiPolygon",
              coordinates: rest as any,
            },
            properties: {
              ...multiPolygon.properties,
              __parent_uuid: uuid,
            },
          },
          name,
          namespace: namespaceId,
        },
      ];

      bulkAddFromSplit(payload, {
        onSuccess: () => {
          // Remove previous shape -- note that we don't use the version
          // of this function from the useShapes hook because we're not interested
          // in logging the result of the delete to the undo history
          deleteShapesRaw([uuid], {
            onSuccess: () => {
              // @ts-ignore
              setTileUpdateCount((x) => x + 1);
              setCursorMode(EditorMode.ViewMode);
              clearOptimisticShapeUpdates();
              clearSelectedFeatureIndexes();
              clearSelectedShapeUuids();
            },
            onError: (error: any) => {
              toast.error(error);
            },
          });
        },
        onError: (error) => {
          toast.error("Error splitting shape");
          console.error(error);
        },
      });
      return;
    }

    if (editType !== "addFeature") {
      return;
    }

    // Feature: Add a shape
    const { featureIndexes } = editContext;
    let mostRecentShape: Feature = updatedData.features[featureIndexes[0]];

    if (cursorMode === EditorMode.LassoDrawMode) {
      // Patches a bug in turf.js where it can't handle a duplicate vertex in unkinkPolygon
      // @ts-ignore
      mostRecentShape.geometry = injectJitterToPolygon(
        // @ts-ignore
        mostRecentShape.geometry
      );
    }

    // Feature: edit kinked shapes
    if (kinks(mostRecentShape as any).features.length > 0) {
      mostRecentShape = unkinkPolygon(mostRecentShape as any) as any;

      // @ts-ignore
      mostRecentShape = mostRecentShape.features.reduce(
        (acc: any, feature: any) => union(acc, feature),
        // @ts-ignore
        mostRecentShape.features[0]
      );
    }

    const newShape = {
      geojson: mostRecentShape,
      name: "New shape",
    } as GeoShapeCreate;

    addShapeAndEdit(newShape, (metadata: GeoShapeMetadata) => {
      setShapeForPropertyEdit(metadata);
    });
  }
  return { onEdit };
}
