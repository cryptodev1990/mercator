import {
  ViewMode,
  DrawPolygonMode,
  SplitPolygonMode,
  DrawPolygonByDraggingMode,
} from "@nebula.gl/edit-modes";

import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { useSelectedShapes } from "../use-selected-shapes";
import { useEditFunction } from "./use-edit-function";

export const useEditLayer = () => {
  const { cursorMode } = useCursorMode();

  const { onEdit } = useEditFunction();
  const { selectedShapes } = useSelectedShapes();

  // THIS IS NOT MODIFY MODE
  // This supports shape cuts and additions
  return new EditableGeoJsonLayer({
    id: "geojson-core",
    pickable: true,
    // @ts-ignore
    data: { type: "FeatureCollection", features: selectedShapes },
    // @ts-ignore
    getFillColor: [250, 128, 114, 150],
    // @ts-ignore
    selectedFeatureIndexes: [0],
    getPolygonOffset: () => [10, -60],
    extruded: true,
    stroked: true,
    filled: true,
    updateTriggers: {
      getFillColor: [selectedShapes.length],
      getLineColor: [selectedShapes.length],
    },
    _subLayerProps: {
      guides: {
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
    },
    // @ts-ignore
    mode: {
      [EditorMode.EditMode]: DrawPolygonMode,
      [EditorMode.LassoDrawMode]: DrawPolygonByDraggingMode,
      [EditorMode.SplitMode]: SplitPolygonMode,
      [EditorMode.ViewMode]: ViewMode,
    }[cursorMode],
    onEdit,
  });
};
