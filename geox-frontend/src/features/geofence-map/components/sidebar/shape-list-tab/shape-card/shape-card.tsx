import Loading from "react-loading";
import { MetadataEditButton } from "./edit-button";
import simplur from "simplur";

import toast from "react-hot-toast";
import {
  TargetIcon,
  DeleteIcon,
} from "../../../../../../common/components/icons";
import { useViewport } from "../../../../hooks/use-viewport";
import { useCursorMode } from "../../../../hooks/use-cursor-mode";
import { EditorMode } from "../../../../cursor-modes";
import { GeoShapeMetadata } from "../../../../../../client/models/GeoShapeMetadata";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { DragHandle } from "./drag-handle";
import { SHAPE_CARD_IMAGE } from "./drag-images";
import React, { useContext, useState } from "react";
import { UIContext } from "../../../../contexts/ui-context";
import { usePatchShapeMutation } from "features/geofence-map/hooks/use-openapi-hooks";
import {
  addShapesToSelectedShapesAction,
  clearSelectedShapesAction,
} from "features/geofence-map/contexts/selection/actions";
import { useSelectedShapesUuids } from "features/geofence-map/hooks/use-selected-shapes-uuids";
import { GeofencerService } from "client";

export const ShapeCard = ({ shape }: { shape: GeoShapeMetadata }) => {
  const { deleteShapes, updateLoading, clearSelectedFeatureIndexes, dispatch } =
    useShapes();

  const { mutate: patchShapeById } = usePatchShapeMutation();
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const { confirmDelete, setHeading } = useContext(UIContext);

  const { dispatch: selectionDispatch } = useSelectedShapes();
  const { setCursorMode } = useCursorMode();
  const { snapToBounds } = useViewport();

  const selectedShapesUuids = useSelectedShapesUuids();

  const selectionBg = "text-blue-800";
  const selectionOpacity = "opacity-100";
  const numProperties = Object.keys(shape.properties).filter(
    (x) => !x.startsWith("__")
  ).length;
  return (
    <div
      draggable={false}
      key={shape.uuid}
      onMouseLeave={() => setIsHovered(false)}
      onMouseEnter={() => setIsHovered(true)}
      className={`h-13 p-3 max-w-sm snap-start bg-slate-600 border-gray-200 ${selectionBg}`}
    >
      <div className="flex flex-row justify-left items-center">
        <DragHandle
          shape={shape}
          dragImage={SHAPE_CARD_IMAGE}
          // dataTip={`Drag into ${shape.name} another folder`}
        />
        <EditableLabel
          value={shape?.name || "New shape"}
          onChange={(newName) => {
            if (newName !== shape.name) {
              patchShapeById({
                uuid: shape.uuid,
                namespace: shape.namespace_id,
                name: newName,
              });
            }
          }}
          className="text-1xl font-sans tracking-tight text-white truncate"
        />
        <div
          className={`transition flex flex-row justify-start space-x-1 ${selectionOpacity} ml-auto`}
        >
          {isHovered && (
            <>
              <MetadataEditButton shape={shape} />
              <button
                className="cx-btn-square hover:bg-red-400 hover:border-red-400 box-border"
                disabled={updateLoading}
                onClick={(e: any) => {
                  setHeading("Delete geofence?");
                  if (!shape.uuid) toast.error("Delete shape failed");
                  else {
                    const coords = [e.clientX, e.clientY];
                    confirmDelete(coords, () => {
                      deleteShapes([shape.uuid]);
                      selectionDispatch(clearSelectedShapesAction());
                      clearSelectedFeatureIndexes();
                      setCursorMode(EditorMode.ViewMode);
                    });
                  }
                }}
              >
                {updateLoading ? (
                  <Loading height={8} width={8} />
                ) : (
                  <DeleteIcon className="fill-white" />
                )}
              </button>
              <button
                className="cx-btn-square hover:bg-green-400 hover:border-green-400 box-border"
                data-tip="Zoom to"
                onClick={() => {
                  dispatch({ type: "SET_LOADING", value: true });
                  selectionDispatch(clearSelectedShapesAction());

                  GeofencerService.getShapeByUuid(shape.uuid).then(
                    (sh: any) => {
                      selectionDispatch(
                        addShapesToSelectedShapesAction([sh.geojson])
                      );
                      snapToBounds({ category: "selected" });
                      dispatch({ type: "SET_LOADING", value: false });
                    }
                  );
                }}
              >
                <TargetIcon className={"fill-gray-400 animate-puls"} />
              </button>
            </>
          )}
          {!isHovered && numProperties > 0 && (
            <div
              className="
              whitespace-nowrap
            text-xs
            font-sans
            tracking-tight text-white box-border select-none overflow-none text-ellipsis"
            >
              {simplur`${numProperties} propert[y|ies]`}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
