// EditableGeojsonLayer function
import {
  GeoShapeCreate,
  MultiPolygon,
  GeoShapeMetadata,
} from "../../../../client";
import { Feature, unkinkPolygon, kinks } from "@turf/turf";

import { useShapes } from "../use-shapes";
import { toast } from "react-hot-toast";
import { useCursorMode } from "../use-cursor-mode";
import { EditorMode } from "../../cursor-modes";
import { useSelectedShapes } from "../use-selected-shapes";
import { useBulkDeleteShapesMutation } from "../openapi-hooks";

export function useEditFunction() {
  const {
    shapeMetadata,
    setShapeForPropertyEdit,
    selectedFeatureIndexes,
    clearSelectedFeatureIndexes,
    bulkAddFromSplit,
    addShapeAndEdit,
  } = useShapes();

  const { mutate: deleteShapesRaw } = useBulkDeleteShapesMutation();

  const { clearSelectedShapeUuids, numSelected, selectedUuids } =
    useSelectedShapes();
  const { setCursorMode } = useCursorMode();
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

      const name = shapeMetadata.find((x) => x.uuid === uuid)?.name;
      delete multiPolygon?.properties?.__uuid;
      const payload = [
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
        },
      ];

      bulkAddFromSplit(payload, {
        onSuccess: ({ num_shapes: numShapes }) => {
          // Remove previous shape -- note that we don't use the version
          // of this function from the useShapes hook because we're not interested
          // in logging the result of the delete to the undo history
          deleteShapesRaw([uuid], {
            onSuccess: () => {
              toast.success(`Created ${numShapes} new shapes`);
              setCursorMode(EditorMode.ViewMode);
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

    // Feature: edit kinked shapes
    if (kinks(mostRecentShape as any).features.length > 0) {
      mostRecentShape = unkinkPolygon(mostRecentShape as any) as any;
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
