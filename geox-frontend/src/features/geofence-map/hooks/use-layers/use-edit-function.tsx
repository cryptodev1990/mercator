// EditableGeojsonLayer function
import { GeoShape, GeoShapeCreate, MultiPolygon } from "../../../../client";
import { Feature, difference, flatten, Geometry } from "@turf/turf";

// @ts-ignore
import { useCursorMode } from "../use-cursor-mode";

import {
  clearSelectedFeatureIndexes,
  selectedFeatureIndexes,
} from "./use-layers";

import { useShapes } from "../use-shapes";
import { useAddShapeMutation, useUpdateShapeMutation } from "../openapi-hooks";

export function useEditFunction() {
  const { options } = useCursorMode();
  const {
    shapes,
    selectedShapeUuids,
    setShapeForMetadataEdit,
    clearSelectedShapeUuids,
    setTentativeShapes,
  } = useShapes();
  const { mutate: addShape } = useAddShapeMutation();
  const { mutate: updateShape } = useUpdateShapeMutation();

  const addShapeAndEdit = async (shape: GeoShapeCreate) => {
    addShape(shape as any, {
      onSuccess: (data: any) => {
        const geoshape = data as GeoShape;
        setShapeForMetadataEdit(geoshape);
      },
    });
  };

  function onEdit({
    updatedData,
    editType,
  }: {
    updatedData: any;
    editType: string;
  }) {
    console.log(editType);
    if (editType === "split") {
      let editedShape: Feature<MultiPolygon> =
        updatedData.features[selectedFeatureIndexes[0]];

      // There should be no split that selects more than one shape
      if (
        Object.keys(selectedShapeUuids).length > 1 ||
        selectedFeatureIndexes.length > 1 ||
        shapes[selectedFeatureIndexes[0]].uuid !==
          Object.keys(selectedShapeUuids)[0]
      ) {
        console.log(
          Object.keys(selectedShapeUuids).length > 1 ||
            selectedFeatureIndexes.length > 1 ||
            shapes[selectedFeatureIndexes[0]].uuid !==
              Object.keys(selectedShapeUuids)[0]
        );
        throw new Error("Split should not select more than one shape");
      }
      const uuid = editedShape?.properties?.__uuid;
      const flattenedShapes = flatten(editedShape as any);

      for (const shape of flattenedShapes.features) {
        addShape({
          geojson: shape as any,
          name: shapes.find((x) => x.uuid === uuid)?.name,
        });
      }
      updateShape(
        {
          uuid,
          should_delete: true,
        },
        {
          onSettled: () => {
            clearSelectedFeatureIndexes();
            clearSelectedShapeUuids();
          },
        }
      );
      return;
    }
    if (["movePosition"].includes(editType)) {
      let editedShape: Feature<Geometry> =
        updatedData.features[selectedFeatureIndexes[0]];
      const uuid = editedShape?.properties?.__uuid;
      setTentativeShapes([
        {
          geojson: editedShape as any,
          name: shapes.find((x) => x.uuid === uuid)?.name,
        } as GeoShapeCreate,
      ]);
      return;
    }
    if (
      ["removePosition", "addPosition", "finishMovePosition"].includes(editType)
    ) {
      setTentativeShapes([]);
      updateShape({
        uuid: shapes[selectedFeatureIndexes[0]].uuid,
        geojson: updatedData.features[selectedFeatureIndexes[0]],
      });
      return;
    }

    if (editType !== "addFeature") {
      return;
    }

    let mostRecentShape: Feature =
      updatedData.features[updatedData.features.length - 1];

    if (options.denyOverlap && shapes) {
      for (const shape of shapes) {
        if (shape.uuid === mostRecentShape?.properties?.uuid) {
          continue;
        }
        const diffShape = difference(
          mostRecentShape as any,
          shape.geojson as any
        );
        if (diffShape === null) {
          return;
        }
        mostRecentShape = diffShape as Feature;
      }
    }

    const newShape = {
      geojson: mostRecentShape,
      name: "New shape",
    } as GeoShapeCreate;
    // TODO Correct type issue
    addShapeAndEdit(newShape);
  }
  return { onEdit };
}
