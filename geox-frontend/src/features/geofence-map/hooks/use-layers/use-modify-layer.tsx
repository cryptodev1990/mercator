import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { useEffect, useState } from "react";
import { MercatorModifyMode } from "../../../../lib/mercator-modify-mode/MercatorModifyMode";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { usePutShapeMutation } from "../use-openapi-hooks";
import { useSelectedShapes } from "../use-selected-shapes";
import { useShapes } from "../use-shapes";
import { useViewport } from "../use-viewport";

export function useModifyLayer() {
  const [localData, setLocalData] = useState<any>([]);
  const { selectedFeatureIndexes, setSelectedFeatureIndexes } = useShapes();
  const { cursorMode } = useCursorMode();
  const { setSelectedShapeUuid, isSelected, selectedFeatureCollection } =
    useSelectedShapes();
  const { viewport } = useViewport();

  const { mutate: putShapeApi } = usePutShapeMutation();

  function getFillColorFunc(datum: any) {
    if (isSelected(datum?.properties?.__uuid)) {
      return [255, 0, 0, 150];
    }
    return [140, 170, 180];
  }

  useEffect(() => {
    if (selectedFeatureCollection) {
      setLocalData(selectedFeatureCollection);
    }
  }, [selectedFeatureCollection]);

  if (
    selectedFeatureCollection === null ||
    EditorMode.ModifyMode !== cursorMode
  ) {
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
      getFillColor: [selectedFeatureCollection],
      getLineColor: [selectedFeatureCollection],
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
        putShapeApi({
          geojson: updatedData.features[editContext.featureIndexes[0]],
          uuid: updatedData.features[editContext.featureIndexes[0]].properties
            .__uuid,
        });
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
        setSelectedShapeUuid((o.object as any).properties.__uuid);
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
          return isSelected(d?.properties?.__uuid)
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
