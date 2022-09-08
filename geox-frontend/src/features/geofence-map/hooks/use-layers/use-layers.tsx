import { GeoJsonLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { useMapMatchMode } from "../use-map-match-mode";

import {
  ViewMode,
  DrawPolygonMode,
  ModifyMode,
  SplitPolygonMode,
  DrawPolygonByDraggingMode,
} from "@nebula.gl/edit-modes";
import { featureToFeatureCollection } from "../../utils";
// @ts-ignore
import { useCursorMode } from "../use-cursor-mode";
import { useEditFunction } from "./use-edit-function";
import { useShapes } from "../use-shapes";
import { Feature, GeoShape } from "../../../../client";
import { useEffect, useState } from "react";
import { useUpdateShapeMutation } from "../openapi-hooks";

export const useLayers = () => {
  const {
    shapes,
    tentativeShapes,
    selectedShapeUuids,
    selectOneShapeUuid,
    clearSelectedShapeUuids,
    scrollToSelectedShape,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
  } = useShapes();

  const { mutate: updateShape } = useUpdateShapeMutation();

  // FeatureCollection
  const [localData, setLocalData] = useState<any>();

  useEffect(() => {
    setLocalData(() =>
      featureToFeatureCollection(shapes.map((s) => s.geojson))
    );
  }, [shapes]);

  useEffect(() => {
    setLocalData(() =>
      featureToFeatureCollection(shapes.map((s) => s.geojson))
    );
  }, []);

  const { cursorMode, setCursorMode } = useCursorMode();

  const SELECTED_RGB = [255, 0, 0, 150];

  function getFillColorFunc(datum: Feature) {
    if (selectedShapeUuids[datum?.properties?.__uuid]) {
      return SELECTED_RGB;
    }
    return [36, 99, 235, 150];
  }

  const modeArgs = {
    getFillColorFunc,
    selectedFeatureIndexes,
  };
  const { layer: mapMatchModeLayer } = useMapMatchMode(modeArgs);
  const { onEdit } = useEditFunction();

  return {
    layers: [
      tentativeShapes.length > 0 &&
        new GeoJsonLayer({
          id: "geojson-i",
          pickable: false,
          // @ts-ignore
          getFillColor: [0, 0, 255, 100],
          getLineColor: [128, 128, 128, 255],
          lineWidthMinPixels: 1,
          stroked: true,
          filled: true,
          // @ts-ignore
          data: featureToFeatureCollection(
            tentativeShapes.map((x) => x.geojson)
          ),
        }),
      [EditorMode.ModifyMode].includes(cursorMode) &&
        new EditableGeoJsonLayer({
          id: "geojson-modify",
          pickable: true,
          // @ts-ignore
          data: localData || [],
          // @ts-ignore
          getFillColor: getFillColorFunc,
          mode: ModifyMode,
          // @ts-ignore
          selectedFeatureIndexes,
          useUpdateTriggers: {
            getFillColor: [selectedShapeUuids],
          },
          onEdit: (e: any) => {
            const { updatedData, editType, editContext } = e;
            if (editType === "addFeature") {
              return;
            }
            setLocalData(updatedData);
            if (["addPosition", "removePosition"].includes(editType)) {
              updateShape(
                {
                  geojson: updatedData.features[editContext.featureIndexes[0]],
                  uuid: updatedData.features[editContext.featureIndexes[0]]
                    .properties.__uuid,
                },
                {
                  onSuccess: (data) => {
                    console.log("updated shape because of", editType);
                  },
                }
              );
            }
          },
          onClick: (e: any) => {
            if (e.object.properties.guideType) {
              // Click should not affect removing or adding points
              // This variable is only present if we are removing or adding points
            }
            if (e.object) {
              // Click of a layer should make that layer selected
              selectOneShapeUuid(e.object.properties.__uuid);
              setSelectedFeatureIndexes([e.index]);
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
            console.log("updated shape because of", "finishMove");
            updateShape({
              geojson: shapeInEdit,
              uuid: shapeInEdit.properties.__uuid,
            });
          },
          _subLayerProps: {
            guides: {
              stroked: true,
              // https://deck.gl/docs/api-reference/layers/geojson-layer#pointtypecircle-options
              pointRadiusMinPixels: 2,
              getPointRadius: 5,
              getFillColor: [255, 255, 255, 150],
              getLineColor: [0, 150, 255],
            },
          },
        }),
      [
        EditorMode.LassoDrawMode,
        EditorMode.SplitMode,
        EditorMode.ViewMode,
        EditorMode.EditMode,
      ].includes(cursorMode) &&
        new EditableGeoJsonLayer({
          id: "geojson-core",
          pickable: true,
          // @ts-ignore
          data: featureToFeatureCollection(
            shapes.map((x: GeoShape) => x.geojson)
          ),
          // @ts-ignore
          getFillColor: getFillColorFunc,
          // @ts-ignore
          selectedFeatureIndexes,
          useUpdateTriggers: {
            getFillColor: [selectedShapeUuids],
          },
          _subLayerProps: {
            guides: {
              stroked: true,
              // https://deck.gl/docs/api-reference/layers/geojson-layer#pointtypecircle-options
              pointRadiusMinPixels: 2,
              getPointRadius: 5,
              getFillColor: [255, 255, 255, 150],
              getLineColor: [0, 150, 255],
            },
          },
          onClick: (data: any, event: any) => {
            if (
              !event?.object?.properties?.guideType &&
              cursorMode === EditorMode.EditMode
            ) {
              return;
            }

            if (event && data?.object) {
              selectOneShapeUuid(data.object.properties.__uuid);
              setCursorMode(EditorMode.ModifyMode);
            }
            if (data && data.object) {
              if (!selectedShapeUuids[data.object.properties.__uuid]) {
                selectOneShapeUuid(data.object.properties.__uuid);
                setSelectedFeatureIndexes([data.index]);
                scrollToSelectedShape(data.index);
                setCursorMode(EditorMode.ModifyMode);
              } else {
                clearSelectedShapeUuids();
                setSelectedFeatureIndexes([]);
              }
            }
          },
          // @ts-ignore
          mode: {
            [EditorMode.EditMode]: DrawPolygonMode,
            [EditorMode.LassoDrawMode]: DrawPolygonByDraggingMode,
            [EditorMode.SplitMode]: SplitPolygonMode,
            [EditorMode.ViewMode]: ViewMode,
          }[cursorMode],
          onEdit,
        }),
      cursorMode === EditorMode.DrawPolygonFromRouteMode && mapMatchModeLayer,
    ],
  };
};
