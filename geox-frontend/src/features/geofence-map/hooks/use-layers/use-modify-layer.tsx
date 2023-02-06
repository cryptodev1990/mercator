import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { GeoShape } from "client";
import { addShapesToSelectedShapesAction } from "features/geofence-map/contexts/selection/actions";
import { useEffect, useState } from "react";
import { MercatorModifyMode } from "../../../../lib/mercator-modify-mode/MercatorModifyMode";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { usePutShapeMutation } from "../use-openapi-hooks";
import { useSelectedShapes } from "../use-selected-shapes";
import { useSelectedShapesUuids } from "../use-selected-shapes-uuids";
import { useShapes } from "../use-shapes";
import { useViewport } from "../use-viewport";

export function useModifyLayer() {
  const [localData, setLocalData] = useState<any>([]);
  const {
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
    dispatch,
    clearOptimisticShapeUpdates,
  } = useShapes();
  const { cursorMode } = useCursorMode();
  const { selectedShapes, dispatch: selectedDispatch } = useSelectedShapes();

  const selectedShapesUuids = useSelectedShapesUuids();

  const { viewport } = useViewport();
  const { mutate: putShapeApi } = usePutShapeMutation();

  function getFillColorFunc(datum: any) {
    if (selectedShapesUuids.includes(datum?.properties?.__uuid)) {
      return [255, 0, 0, 150];
    }
    return [140, 170, 180];
  }

  useEffect(() => {
    if (selectedShapes) {
      setLocalData({ type: "FeatureCollection", features: selectedShapes });
    }
  }, [selectedShapes]);

  if (EditorMode.ModifyMode !== cursorMode) {
    return null;
  }

  const layer = new EditableGeoJsonLayer({
    id: "geojson-modify",
    pickable: true,
    // @ts-ignore
    data: localData,
    // @ts-ignore
    getFillColor: getFillColorFunc,
    mode: MercatorModifyMode,
    // @ts-ignore
    selectedFeatureIndexes,
    pickingRadius: 20,
    pickingDepth: 5,
    updateTriggers: {
      getFillColor: [selectedShapes],
      getLineColor: [selectedShapes],
    },
    modeConfig: {
      viewport,
    },
    onEdit: (e: any) => {
      const { updatedData, editType, editContext } = e;
      setLocalData(updatedData);
      if (
        ["addPosition", "removePosition", "finishMovePosition"].includes(
          editType
        )
      ) {
        const newShape: GeoShape = {
          geojson: updatedData.features[editContext.featureIndexes[0]],
          uuid: updatedData.features[editContext.featureIndexes[0]].properties
            .__uuid,
        };
        dispatch({
          type: "SET_OPTIMISTIC_SHAPE",
          shape: newShape,
        });
        putShapeApi(newShape);
        return;
      }
    },
    onClick: (o: any, e: any) => {
      if (
        ["intermediate", "existing"].includes(
          (o.object as any).properties.editHandleType
        ) &&
        (o.object as any).properties.guideType === "editHandle"
      ) {
        // Click should not affect removing or adding points
        // This variable is only present if we are removing or adding points
        return;
      } else if (o.object) {
        // Click of a layer should make that layer selected
        selectedDispatch(addShapesToSelectedShapesAction([o.object]));
        setSelectedFeatureIndexes([o.index]);
      }
    },
    _subLayerProps: {
      guides: {
        stroked: true,
        // https://deck.gl/docs/api-reference/layers/geojson-layer#pointtypecircle-options
        pointRadiusMinPixels: 1,
        getPointRadius: 3,
        pointRadiusMaxPixels: 5,
        getLineColor: (d: any) => {
          if (
            d.properties.editHandleType === "existing" &&
            d.properties.guideType === "editHandle"
          ) {
            return [0, 0, 0, 255];
          }
          return [255, 255, 0, 255];
        },
        getFillColor: (d: any) => {
          if (
            d.properties.editHandleType === "intermediate" &&
            d.properties.guideType === "editHandle"
          ) {
            return [0, 0, 0, 0];
          }
          return [0, 0, 0];
        },
      },
      geojson: {
        stroked: true,
        filled: true,
        lineWidthMaxPixels: 1,
        getLineColor: (d: any) => {
          return selectedShapesUuids.includes(d?.properties?.__uuid)
            ? [0, 0, 0, 255]
            : [0, 0, 0, 100];
        },
        pickingRadius: 20,
        getFillColor: [250, 128, 114, 150],
      },
    },
  });
  return layer;
}
