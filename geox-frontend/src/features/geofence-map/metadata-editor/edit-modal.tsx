import { GeoShape, GeoShapeCreate, GeoShapeUpdate } from "../../../client";
import { useMetadataEditModal } from "./hooks";

import React, { useEffect } from "react";

import {
  useAddShapeMutation,
  useUpdateShapeMutation,
} from "../hooks/openapi-hooks";

import { JsonEditor } from "./json-editor";
import { useMemo } from "react";

interface IDictionary<T> {
  [index: string]: T;
}

export const EditModal = ({
  shape,
}: {
  shape: GeoShape | GeoShapeCreate | GeoShapeUpdate;
}) => {
  const { shapeForEdit, setShapeForEdit } = useMetadataEditModal();
  const { mutate: addShape, isSuccess: addSuccess } = useAddShapeMutation();
  const { mutate: updateShape, isSuccess: updateSuccess } =
    useUpdateShapeMutation();

  const handleSubmit = (properties: IDictionary<string>) => {
    if ((shape as GeoShape).uuid) {
      const geojson = shapeForEdit?.geojson || shape.geojson;
      if (geojson) {
        geojson.properties = properties;
      }
      updateShape({
        name: shape.name,
        geojson,
        uuid: (shape as GeoShape).uuid,
        should_delete: false,
      });
    } else {
      const geojson = (shapeForEdit as GeoShapeCreate).geojson;
      geojson.properties = properties;
      addShape({
        name: properties.name || "New Polygon",
        geojson,
      });
    }
  };

  useEffect(() => {
    if (updateSuccess || addSuccess) {
      setShapeForEdit(null);
    }
  }, [updateSuccess, addSuccess]);

  const reformattedProperties = useMemo(() => {
    return Object.keys(shapeForEdit?.geojson.properties).map((k) => {
      return { key: k, value: shapeForEdit?.geojson.properties[k] };
    });
  }, [shapeForEdit]);

  return (
    <div>
      <h1>Shape properties</h1>
      <JsonEditor
        properties={reformattedProperties}
        handleResults={handleSubmit}
      />
    </div>
  );
};
