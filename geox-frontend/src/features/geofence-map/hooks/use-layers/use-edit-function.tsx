// EditableGeojsonLayer function
import {
  GeoShape,
  GeoShapeCreate,
  MultiPolygon,
  GeoShapeMetadata,
} from "../../../../client";
import { Feature, flatten, unkinkPolygon, kinks } from "@turf/turf";

import { useShapes } from "../use-shapes";
import {
  useAddShapeMutation,
  useBulkAddShapesMutation,
  useUpdateShapeMutation,
} from "../openapi-hooks";
import { toast } from "react-hot-toast";

export function useEditFunction() {
  const {
    shapeMetadata,
    selectedShapeUuids,
    setShapeForPropertyEdit,
    clearSelectedShapeUuids,
    selectedFeatureIndexes,
    clearSelectedFeatureIndexes,
  } = useShapes();
  const { mutate: addShape } = useAddShapeMutation();
  const { mutate: bulkAdd } = useBulkAddShapesMutation();
  const { mutate: updateShape } = useUpdateShapeMutation();

  const addShapeAndEdit = async (shape: GeoShapeCreate) => {
    addShape(shape as any, {
      onSuccess: (data: any) => {
        const geoshape = data as GeoShape;
        const metadata = {
          properties: geoshape.geojson.properties,
          ...geoshape,
        } as GeoShapeMetadata;
        setShapeForPropertyEdit(metadata);
      },
    });
  };

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

      if (
        Object.keys(selectedShapeUuids).length > 1 ||
        selectedFeatureIndexes.length > 1
      ) {
        toast.error("Split should not select more than one shape");
        return;
      }
      const uuid = Object.keys(selectedShapeUuids)[0];

      const name = shapeMetadata.find((x) => x.uuid === uuid)?.name;
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

      bulkAdd(payload, {
        onSuccess: ({ num_shapes: numShapes }) => {
          // Remove previous shape
          updateShape(
            {
              uuid,
              should_delete: true,
            },
            {
              onSuccess: () => {
                toast.success(`Created ${numShapes} new shapes`);
                clearSelectedFeatureIndexes();
                clearSelectedShapeUuids();
              },
              onError: (error) => {
                toast.error(error);
              },
            }
          );
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

    addShapeAndEdit(newShape);
  }
  return { onEdit };
}
