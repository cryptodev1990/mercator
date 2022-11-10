import { useGetOneShapeByUuid } from "../../../hooks/use-openapi-hooks";

import { OldJsonEditor } from "./old-json-editor";
import { useShapes } from "../../../hooks/use-shapes";
import { useMemo } from "react";
import JsonEditor from "./json-editor";

interface IDictionary<T> {
  [index: string]: T;
}

// Feature: Editor for shape properties viewable in the second tab of the sidebar
export const ShapeEditor = () => {
  // add update shape mutation that only modifies shape metadata
  const {
    shapeForPropertyEdit,
    setShapeForPropertyEdit,
    updateShape,
    updateLoading,
  } = useShapes();
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
    properties.name =
      shapeForPropertyEdit.name || properties.name || "New shape";
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
      <div className="px-2">
        {" "}
        <h1 className="py-1 mt-2 bg-red font-semibold">Shape properties</h1>
        {/* <button
        title="Edit as raw JSON"
        className="btn btn-sm absolute top-2 right-1 text-sm flex flex-row bg-transparent border-none hover:bg-slate-500"
      >
        <BiPencil className="stroke-white fill-white" />
      </button> */}
        <div>
          {/* <OldJsonEditor
            properties={reformattedProperties as any}
            handleResults={handleSubmit}
            disableSubmit={updateLoading || oneShapeIsLoading}
          /> */}
          <JsonEditor
            uuid={shapeForPropertyEdit?.uuid}
            properties={reformattedProperties as any}
            handleResults={handleSubmit}
          />
        </div>
      </div>
    </div>
  );
};
