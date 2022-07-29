import { GeoJsonLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer, SelectionLayer } from "@nebula.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { useMapMatchMode } from "../use-map-match-mode";
import { useIcDemoMode } from "../use-ic-demo-mode";

import {
  ViewMode,
  DrawPolygonMode,
  DrawPolygonByDraggingMode,
  TranslateMode,
} from "@nebula.gl/edit-modes";
import { featureToFeatureCollection } from "../../utils";
import { useCursorMode } from "../use-cursor-mode";
import { useEditFunction } from "./use-edit-function";
import { useShapes } from "../use-shapes";
import { Feature, GeoShape } from "../../../../client";

const selectedFeatureIndexes: any[] = [];

export const useLayers = () => {
  const {
    shapes,
    tentativeShapes,
    selectedShapeUuids,
    clearSelectedShapeUuids,
    selectOneShapeUuid,
  } = useShapes();
  const { cursorMode } = useCursorMode();

  function getFillColorFunc(datum: Feature) {
    console.log(selectedShapeUuids);
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
  const { getLayers: getIcDemoLayers } = useIcDemoMode(modeArgs);
  const { onEdit } = useEditFunction();

  return [
    tentativeShapes.length > 0 &&
      new GeoJsonLayer({
        id: "geojson-i",
        pickable: true,
        // @ts-ignore
        getFillColor: [0, 0, 255, 100],
        stroked: true,
        filled: true,
        data: featureToFeatureCollection(tentativeShapes.map((x) => x.geojson)),
        mode: ViewMode,
      }),
    cursorMode === EditorMode.ViewMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: shapes.map((x: GeoShape) => x.geojson),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        onHover: (info: any) => {
          if (info && info.object) {
            selectOneShapeUuid(info.object.properties.__uuid);
          }
          if (info && !info.object && selectedShapeUuids) {
            clearSelectedShapeUuids();
          }
        },
        mode: ViewMode,
      }),

    [EditorMode.EditMode, EditorMode.LassoDrawMode].includes(cursorMode) &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
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
        mode:
          cursorMode === EditorMode.EditMode
            ? DrawPolygonMode
            : DrawPolygonByDraggingMode,
        onEdit: onEdit,
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
    ...getIcDemoLayers(cursorMode === EditorMode.InstacartDemoMode),
  ];
};
