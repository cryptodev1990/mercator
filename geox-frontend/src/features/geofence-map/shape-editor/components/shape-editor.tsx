import {
  useGetOneShapeByUuid,
  useUpdateShapeMutation,
} from "../../hooks/openapi-hooks";

import { JsonEditor } from "./json-editor";
import { useShapes } from "../../hooks/use-shapes";
import { useMemo } from "react";

interface IDictionary<T> {
  [index: string]: T;
}

// Feature: Editor for shape properties viewable in the second tab of the sidebar
export const ShapeEditor = () => {
  const { mutate: updateShape, isLoading: editIsLoading } =
    useUpdateShapeMutation();
  // add update shape mutation that only modifies shape metadata
  const { shapeForPropertyEdit, setShapeForPropertyEdit } = useShapes();
  const { data: oneShape, isLoading: oneShapeIsLoading } = useGetOneShapeByUuid(
    shapeForPropertyEdit?.uuid || ""
  );

  const handleSubmit = (properties: IDictionary<string>) => {
    if (
      !shapeForPropertyEdit ||
      !shapeForPropertyEdit.uuid ||
      !oneShape ||
      oneShapeIsLoading
    ) {
      return;
    }
    const shapeUuid = shapeForPropertyEdit.uuid;
    updateShape(
      {
        name: properties.name,
        geojson: {
          ...(oneShape?.geojson as any),
          properties,
        },
        uuid: shapeUuid,
        should_delete: false,
      },
      {
        onSuccess: () => setShapeForPropertyEdit(null),
      }
    );
  };

  const reformattedProperties = useMemo(() => {
    if (!shapeForPropertyEdit?.uuid) {
      return {};
    }
    const { properties } = shapeForPropertyEdit;
    properties.name = properties.name || "New shape";
    return properties
      ? Object.keys(properties).map((k) => {
          return { key: k, value: properties[k] };
        })
      : [];
  }, [shapeForPropertyEdit]);

  if (!shapeForPropertyEdit) {
    return <div>The metadata editor needs a shape to edit</div>;
  }

  return (
    <div>
      <h1 className="px-2 py-1 bg-red font-semibold uppercase">
        Shape properties
      </h1>
      <div>
        <JsonEditor
          properties={reformattedProperties as any}
          handleResults={handleSubmit}
          disableSubmit={editIsLoading || oneShapeIsLoading}
        />
      </div>
    </div>
  );
};
