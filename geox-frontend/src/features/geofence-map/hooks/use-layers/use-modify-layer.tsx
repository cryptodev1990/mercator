import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { useEffect, useState } from "react";
import { MercatorModifyMode } from "../../../../lib/mercator-modify-mode/MercatorModifyMode";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { useSelectedShapes } from "../use-selected-shapes";
import { useShapes } from "../use-shapes";
import { useViewport } from "../use-viewport";

export function useModifyLayer() {
  const [localData, setLocalData] = useState<any>([]);
  const { selectedFeatureIndexes, setSelectedFeatureIndexes, updateShape } =
    useShapes();
  const { cursorMode } = useCursorMode();
  const { selectOneShapeUuid, isSelected, selectedFeatureCollection } =
    useSelectedShapes();
  const { viewport } = useViewport();

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
      console.log("onEdit", editType);
      if (
        ["addPosition", "removePosition", "finishMovePosition"].includes(
          editType
        )
      ) {
        updateShape({
          geojson: updatedData.features[editContext.featureIndexes[0]],
          uuid: updatedData.features[editContext.featureIndexes[0]].properties
            .__uuid,
        });
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
        selectOneShapeUuid((o.object as any).properties.__uuid);
        setSelectedFeatureIndexes([o.index]);
      }
    },
    onDragEnd: (event: any, info: any) => {
      // web call here
      if (!event.object.properties.guideType) {
        // Viewport drags should not affect moving points
        // This variable is only absent if we are moving points
        return;
      }
      // Move the points
      const shapeInEdit = event.layer.state.selectedFeatures[0];
      console.log("onDragEnd", shapeInEdit);
      updateShape({
        geojson: shapeInEdit,
        uuid: shapeInEdit.properties.__uuid,
      });
    },
    _subLayerProps: {
      guides: {
        stroked: true,
        // https://deck.gl/docs/api-reference/layers/geojson-layer#pointtypecircle-options
        pointRadiusMinPixels: 5,
        getPointRadius: 1,
        lineWidthMinPixels: 1,
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
        getFillColor: [0, 0, 0, 0],
      },
    },
  });
  return layer;
}
