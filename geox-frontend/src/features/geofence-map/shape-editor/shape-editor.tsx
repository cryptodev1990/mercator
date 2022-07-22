import { useEditableShape } from "./hooks";

import { useUpdateShapeMutation } from "../hooks/openapi-hooks";

import { JsonEditor } from "./json-editor";
import { useMemo } from "react";

interface IDictionary<T> {
  [index: string]: T;
}

export const ShapeEditor = () => {
  const { mutate: updateShape } = useUpdateShapeMutation();

  const { shapeForEdit, setShapeForEdit } = useEditableShape();
  console.log("shapeForEdit", shapeForEdit);
  const handleSubmit = (properties: IDictionary<string>) => {
    if (!shapeForEdit || !shapeForEdit.geojson) {
      return;
    }

    updateShape(
      {
        name: properties.name,
        geojson: {
          ...shapeForEdit.geojson,
          properties,
        },
        uuid: shapeForEdit.uuid,
        should_delete: false,
      },
      {
        onSuccess: (data, variables, context) => {
          setShapeForEdit(null);
        },
      }
    );
  };

  if (!shapeForEdit || !shapeForEdit.geojson) {
    return null;
  }
  const { properties } = shapeForEdit.geojson;
  const reformattedProperties = properties
    ? Object.keys(properties).map((k) => {
        return { key: k, value: properties[k] };
      })
    : [];

  if (!shapeForEdit || reformattedProperties === null) {
    return <div>The metadata editor needs a shape to edit</div>;
  }

  return (
    <div>
      <h1 className="p-2 font-mono">Shape properties</h1>
      <div>
        <JsonEditor
          properties={reformattedProperties}
          handleResults={handleSubmit}
        />
      </div>
    </div>
  );
};
