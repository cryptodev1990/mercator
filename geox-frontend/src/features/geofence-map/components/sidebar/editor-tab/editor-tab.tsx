import {
  useGetOneShapeByUuid,
  useUpdateShapeMutation,
} from "../../../hooks/use-openapi-hooks";
import { useShapes } from "../../../hooks/use-shapes";
import { useMemo } from "react";
import JsonEditor from "./json-editor";
import { GeoShape } from "client";

interface IDictionary<T> {
  [index: string]: T;
}

// Feature: Editor for shape properties viewable in the second tab of the sidebar
export const ShapeEditor = () => {
  // add update shape mutation that only modifies shape metadata
  const {
    shapeForPropertyEdit,
    setShapeForPropertyEdit,
    partialUpdateShape,
    dispatch,
  } = useShapes();
  const { data: oneShape, isLoading: oneShapeIsLoading } = useGetOneShapeByUuid(
    shapeForPropertyEdit?.uuid || ""
  );

  const {
    mutate: updateShapeApi,
    isLoading: updateShapeIsLoading,
    error: updateShapeError,
    isSuccess: updateShapeIsSuccess,
    data: updateShapeResponse,
  } = useUpdateShapeMutation();

  const handleSubmit = (formData: IDictionary<string>) => {
    if (
      !shapeForPropertyEdit ||
      !shapeForPropertyEdit.uuid ||
      !oneShape ||
      oneShapeIsLoading
    ) {
      return;
    }
    const shapeUuid = shapeForPropertyEdit.uuid;
    const { namespace, ...properties } = formData;

    const newShape = {
      name: properties.name,
      namespace,
      geojson: {
        ...(oneShape?.geojson as any),
        properties,
      },
      uuid: shapeUuid,
    };

    dispatch({
      type: "OP_LOG_ADD",
      op: "UPDATE_SHAPE",
      payload: newShape,
    });
    dispatch({ type: "UPDATE_SHAPE_LOADING", shapes: [newShape as GeoShape] });
    updateShapeApi(newShape, {
      onSuccess: () => setShapeForPropertyEdit(null),
    });
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
        <h1 className="py-1 mt-2 bg-red font-semibold">Shape properties</h1>
        <div>
          <JsonEditor
            uuid={shapeForPropertyEdit?.uuid}
            properties={reformattedProperties as any}
            handleResults={handleSubmit}
            namespaceId={shapeForPropertyEdit?.namespace_id}
          />
        </div>
      </div>
    </div>
  );
};
