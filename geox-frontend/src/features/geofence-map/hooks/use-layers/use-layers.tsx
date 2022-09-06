import { GeoJsonLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer, SelectionLayer } from "@nebula.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { useMapMatchMode } from "../use-map-match-mode";

import {
  ViewMode,
  DrawPolygonMode,
  ModifyMode,
  SplitPolygonMode,
  DrawPolygonByDraggingMode,
  TranslateMode,
} from "@nebula.gl/edit-modes";
import { featureToFeatureCollection } from "../../utils";
// @ts-ignore
import { useCursorMode } from "../use-cursor-mode";
import { useEditFunction } from "./use-edit-function";
import { useShapes } from "../use-shapes";
import { Feature, GeoShape } from "../../../../client";

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
    guideShapes,
  } = useShapes();
  const { cursorMode } = useCursorMode();

  function getFillColorFunc(datum: Feature) {
    if (selectedShapeUuids[datum?.properties?.__uuid]) {
      return [255, 0, 0, 150];
    }
    return [36, 99, 235, 150];
  }

  const modeArgs = {
    getFillColorFunc,
    selectedFeatureIndexes,
  };
  const { layer: mapMatchModeLayer } = useMapMatchMode(modeArgs);
  const { onEdit } = useEditFunction();

  function onCanvasClick(data: any) {
    if (cursorMode === EditorMode.ViewMode && data && !data.object) {
      clearSelectedShapeUuids();
      setSelectedFeatureIndexes([]);
    }
  }

  return {
    onCanvasClick,
    layers: [
      guideShapes.length > 0 &&
        new GeoJsonLayer({
          id: "geojson-i",
          pickable: true,
          // @ts-ignore
          getFillColor: [0, 255, 255, 100],
          getLineColor: [128, 128, 128, 255],
          lineWidthMinPixels: 1,
          stroked: true,
          filled: true,
          // @ts-ignore
          data: featureToFeatureCollection(guideShapes.map((x) => x.geojson)),
        }),
      tentativeShapes.length > 0 &&
        new GeoJsonLayer({
          id: "geojson-i",
          pickable: true,
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
      [
        EditorMode.EditMode,
        EditorMode.LassoDrawMode,
        EditorMode.ModifyMode,
        EditorMode.SplitMode,
        EditorMode.ViewMode,
      ].includes(cursorMode) &&
        new EditableGeoJsonLayer({
          id: "geojson",
          pickable: true,
          // @ts-ignore
          data: featureToFeatureCollection(
            shapes.map((x: GeoShape) => x.geojson)
          ),
          // @ts-ignore
          getFillColor: getFillColorFunc,
          // @ts-ignore
          selectedFeatureIndexes,
          modeConfig: {
            enableSnapping: true,
          },
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
            if (EditorMode.ViewMode !== cursorMode) {
              return;
            }
            if (event && event.rightButton) {
              selectOneShapeUuid(data.object.properties.__uuid);
              return;
            }
            if (data && data.object) {
              if (!selectedShapeUuids[data.object.properties.__uuid]) {
                selectOneShapeUuid(data.object.properties.__uuid);
                setSelectedFeatureIndexes([data.index]);
                scrollToSelectedShape(data.index);
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
            [EditorMode.ModifyMode]: ModifyMode,
            [EditorMode.SplitMode]: SplitPolygonMode,
            [EditorMode.ViewMode]: ViewMode,
          }[cursorMode],
          onEdit,
        }),
      cursorMode === EditorMode.LassoMode &&
        new SelectionLayer({
          id: "selection",
          // @ts-ignore
          selectionType: "rectangle",
          onSelect: ({ pickingInfos }: { pickingInfos: any }) => {
            const uuids = pickingInfos.map((x: any) => {
              return { uuid: x.object.properties.uuid };
            });
            // TODO
            // appendSelected(uuids, true);
          },
          layerIds: ["geojson-read"],
          getTentativeFillColor: () => [255, 0, 255, 100],
          getTentativeLineColor: () => [0, 0, 255, 255],
          getTentativeLineDashArray: () => [0, 0],
          lineWidthMinPixels: 3,
        }),
      cursorMode === EditorMode.LassoMode &&
        new GeoJsonLayer({
          id: "geojson-read",
          // @ts-ignore
          data: shapes.map((x) => x.shape),
          pickable: true,
          // @ts-ignore
          getFillColor: getFillColorFunc,
          lineWidthMinPixels: 3,
        }),
      cursorMode === EditorMode.TranslateMode &&
        new EditableGeoJsonLayer({
          id: "geojson",
          pickable: true,
          data: shapes.map((x) => x.geojson),
          // @ts-ignore
          getFillColor: getFillColorFunc,
          // @ts-ignore
          selectedFeatureIndexes,
          // @ts-ignore
          mode: TranslateMode,
        }),
      cursorMode === EditorMode.DrawPolygonFromRouteMode && mapMatchModeLayer,
    ],
  };
};
