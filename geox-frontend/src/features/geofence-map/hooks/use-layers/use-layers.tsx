import { GeoJsonLayer } from "@deck.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { featureToFeatureCollection } from "../../utils";
import { useCursorMode } from "../use-cursor-mode";
import { useShapes } from "../use-shapes";

import { useTiles } from "./use-tiles";
import { useModifyLayer } from "./use-modify-layer";
import { useEditLayer } from "./use-edit-layer";
import { useSelectedShapes } from "../use-selected-shapes";

export const useLayers = () => {
  const { tentativeShapes, selectedFeatureIndexes, setSelectedFeatureIndexes } =
    useShapes();

  const { selectedFeatureCollection, isSelected } = useSelectedShapes();

  const tiles = useTiles();
  const editLayer = useEditLayer();
  const modifyLayer = useModifyLayer();

  const { cursorMode, setCursorMode } = useCursorMode();

  return {
    layers: [
      tiles,
      // Renders the selected feature
      selectedFeatureCollection &&
        cursorMode === EditorMode.ViewMode &&
        new GeoJsonLayer({
          id: "geojson-view",
          pickable: true,
          // @ts-ignore
          getFillColor: [0, 0, 255, 100],
          getLineColor: [128, 128, 128, 255],
          lineWidthMinPixels: 1,
          onClick: (info: any) => {
            const { object } = info;
            if (object) {
              setCursorMode(EditorMode.ModifyMode);
              setSelectedFeatureIndexes([0]);
            } else {
              setSelectedFeatureIndexes([]);
            }
          },
          stroked: true,
          filled: true,
          // @ts-ignore
          data: selectedFeatureCollection,
        }),
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
      modifyLayer,
      selectedFeatureCollection &&
        [
          EditorMode.LassoDrawMode,
          EditorMode.SplitMode,
          EditorMode.EditMode,
        ].includes(cursorMode) &&
        editLayer,
    ],
  };
};
