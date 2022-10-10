import {
  ViewMode,
  DrawPolygonMode,
  SplitPolygonMode,
  DrawPolygonByDraggingMode,
  // ModifyMode,
} from "@nebula.gl/edit-modes";

import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { useCursorMode } from "../use-cursor-mode";
import { useSelectedShapes } from "../use-selected-shapes";
import { useEditFunction } from "./use-edit-function";

export const useEditLayer = () => {
  const { cursorMode } = useCursorMode();
  const { selectedFeatureCollection } = useSelectedShapes();

  const { onEdit } = useEditFunction();
  const { selectedUuids } = useSelectedShapes();

  if (!selectedFeatureCollection) {
    return null;
  }

  // THIS IS NOT MODIFY MODE
  // This supports shape cuts and additions
  return new EditableGeoJsonLayer({
    id: "geojson-core",
    pickable: true,
    // @ts-ignore
    data: selectedFeatureCollection,
    // @ts-ignore
    getFillColor: [250, 128, 114, 150],
    // @ts-ignore
    selectedFeatureIndexes: [0],
    getPolygonOffset: () => [10, -60],
    updateTriggers: {
      getFillColor: [selectedUuids],
      getLineColor: [selectedUuids],
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
