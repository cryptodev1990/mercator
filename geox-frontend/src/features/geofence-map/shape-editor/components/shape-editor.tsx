import { useUpdateShapeMutation } from "../../hooks/openapi-hooks";

import { JsonEditor } from "./json-editor";
import { useShapes } from "../../hooks/use-shapes";

interface IDictionary<T> {
  [index: string]: T;
}

export const ShapeEditor = () => {
  const { mutate: updateShape } = useUpdateShapeMutation();

  const { shapeForMetadataEdit, setShapeForMetadataEdit } = useShapes();

  const handleSubmit = (properties: IDictionary<string>) => {
    if (
      !shapeForMetadataEdit ||
      !shapeForMetadataEdit.uuid ||
      !shapeForMetadataEdit.geojson
    ) {
      return;
    }
    const shapeUuid = shapeForMetadataEdit.uuid;
    updateShape(
      {
        name: properties.name,
        geojson: {
          ...(shapeForMetadataEdit.geojson as any),
          properties,
        },
        uuid: shapeUuid,
        should_delete: false,
      },
      {
        onSuccess: () => setShapeForMetadataEdit(null),
      }
    );
  };

  const { properties } = shapeForMetadataEdit?.geojson ?? {};
  const reformattedProperties = properties
    ? Object.keys(properties).map((k) => {
        return { key: k, value: properties[k] };
      })
    : [];

  if (!shapeForMetadataEdit || reformattedProperties === null) {
    return <div>The metadata editor needs a shape to edit</div>;
  }

  return (
    <div>
      <h1 className="px-2 py-1 bg-red font-semibold uppercase">
        Shape properties
      </h1>
      <div>
        <JsonEditor
          properties={reformattedProperties}
          handleResults={handleSubmit}
        />
      </div>
    </div>
  );
};
