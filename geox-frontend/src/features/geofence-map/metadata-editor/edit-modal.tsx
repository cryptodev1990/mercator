import { GeoShape, GeoShapeCreate, GeoShapeUpdate } from "../../../client";
import { useMetadataEditModal } from "./hooks";

import React, { useEffect, useRef } from "react";
import {
  useAddShapeMutation,
  useUpdateShapeMutation,
} from "../hooks/openapi-hooks";

const View = (props: any) => {
  return (
    <div
      className="modal fade absolute z-40 w-100 left-10"
      tabIndex={-1}
      role="dialog"
    >
      <div className="relative w-auto pointer-events-none">
        <div className="border-none shadow-lg relative flex flex-col w-full pointer-events-auto bg-white bg-clip-padding rounded-md text-current">
          <div className="modal-header flex flex-shrink-0 items-center justify-between p-4 border-b border-gray-200 rounded-t-md">
            <h5
              className="text-xl font-medium leading-normal text-gray-800"
              id="exampleModalScrollableLabel"
            >
              Edit Geofence
            </h5>
          </div>
          <div className="modal-body relative p-4">{props.children}</div>
          <div className="modal-footer flex flex-shrink-0 flex-wrap items-center justify-end p-4 border-t border-gray-200 rounded-b-md">
            <button>Save changes</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const EditModal = ({
  shape,
}: {
  shape: GeoShape | GeoShapeCreate | GeoShapeUpdate;
}) => {
  const { shapeForEdit, setShapeForEdit } = useMetadataEditModal();
  const { mutate: addShape, isSuccess: addSuccess } = useAddShapeMutation();
  const { mutate: updateShape, isSuccess: updateSuccess } =
    useUpdateShapeMutation();
  const inputRef: any = useRef(null);

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = (event) => {
    event.preventDefault();
    const { name } = (event.target as any).elements;
    if ((shape as GeoShape).uuid) {
      updateShape({
        name: name.value || shape.name,
        uuid: (shape as GeoShape).uuid,
        should_delete: false,
      });
    } else {
      addShape({
        name: name.value,
        geojson: (shapeForEdit as GeoShapeCreate).geojson,
      });
    }
  };

  useEffect(() => {
    if (inputRef.current) {
      console.log("ref!");
      inputRef.current.focus();
    }
  }, [shapeForEdit]);

  useEffect(() => {
    if (updateSuccess || addSuccess) {
      setShapeForEdit(null);
    }
  }, [updateSuccess, addSuccess]);

  return (
    <View>
      <form className="text-black" onSubmit={handleSubmit}>
        <input
          name="name"
          type="text"
          placeholder="Shape name"
          ref={inputRef}
        />
        <input
          type="submit"
          className="inline-block px-6 py-2.5 bg-blue-600 text-white font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-blue-700 hover:shadow-lg focus:bg-blue-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-blue-800 active:shadow-lg transition duration-150 ease-in-out ml-1"
          value="Submit"
        ></input>
        <button
          onClick={() => setShapeForEdit(null)}
          type="button"
          className="inline-block px-6 py-2.5 bg-purple-600 text-white font-medium text-xs leading-tight uppercase rounded shadow-md hover:bg-purple-700 hover:shadow-lg focus:bg-purple-700 focus:shadow-lg focus:outline-none focus:ring-0 active:bg-purple-800 active:shadow-lg transition duration-150 ease-in-out"
          data-bs-dismiss="modal"
        >
          Close
        </button>
      </form>
    </View>
  );
};
