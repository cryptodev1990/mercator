// EditableGeojsonLayer function
import { GeoShape } from "../../../../client";
import { Feature, difference } from "@turf/turf";
import { useCursorMode } from "../use-cursor-mode";
import { useShapes } from "../use-shapes";
import { useAddShapeMutation } from "../openapi-hooks";

export function useEditFunction() {
  const { options } = useCursorMode();
  const { shapes, setShapeForMetadataEdit } = useShapes();
  const { mutate: addShape } = useAddShapeMutation();

  function onEdit({
    updatedData,
    editType,
  }: {
    updatedData: any;
    editType: string;
  }) {
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
    };
    // TODO Correct type issue
    addShape(newShape as any, {
      onSuccess: (data: any) => {
        const geoshape = data as GeoShape;
        setShapeForMetadataEdit(geoshape);
      },
    });
  }
  return { onEdit };
}
