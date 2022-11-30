import React from "react";
import { GeoJsonLayer } from "@deck.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { featureToFeatureCollection } from "../../utils";
import { useCursorMode } from "../use-cursor-mode";
import { useShapes } from "../use-shapes";

import { useTiles } from "./use-tiles";
import { useModifyLayer } from "./use-modify-layer";
import { useEditLayer } from "./use-edit-layer";
import { useSelectedShapes } from "../use-selected-shapes";
import { useImageLayer } from "./use-image-layer";
import { SelectionLayer } from "@nebula.gl/layers";

export const useLayers = () => {
  const { tentativeShapes, setSelectedFeatureIndexes } = useShapes();

  const {
    selectedFeatureCollection,
    multiSelectedShapes,
    multiSelectedShapesUuids,
    addShapesToMultiSelectedShapes,
  } = useSelectedShapes();

  console.log("multiSelectedShapes", multiSelectedShapes);

  const tiles = useTiles();
  const editLayer = useEditLayer();
  const modifyLayer = useModifyLayer();
  const imageLayer = useImageLayer();

  const { cursorMode, setCursorMode } = useCursorMode();

  return {
    layers: [
      selectedFeatureCollection &&
        [
          EditorMode.LassoDrawMode,
          EditorMode.SplitMode,
          EditorMode.EditMode,
        ].includes(cursorMode) &&
        editLayer,
      false && imageLayer, // traceable image layer
      tiles ? tiles[0] : null,
      tiles ? tiles[1] : null,
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
          onClick: (info) => {
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
      multiSelectedShapes &&
        new GeoJsonLayer({
          id: "multi-select-geojson-view",
          pickable: true,
          // @ts-ignore
          getFillColor: [0, 0, 255, 100],
          getLineColor: [128, 128, 128, 255],
          lineWidthMinPixels: 1,
          onClick: (info) => {},
          stroked: true,
          filled: true,
          // @ts-ignore
          data: multiSelectedShapes,
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
          pointRadiusMinPixels: 7,
        }),
      modifyLayer,
      cursorMode === EditorMode.MultiSelectMode &&
        new SelectionLayer({
          id: "selection",
          selectionType: "polygon",
          onSelect: ({ pickingInfos }) => {
            console.log("pickingInfos", pickingInfos);
            const newObjs = [];
            for (const obj of pickingInfos) {
              newObjs.push(obj.object);
            }
            addShapesToMultiSelectedShapes(newObjs);
          },
          layerIds: ["gf-mvt"],
          getTentativeFillColor: () => [255, 0, 255, 100],
          getTentativeLineColor: () => [0, 0, 255, 255],
          getTentativeLineDashArray: () => [0, 0],
          lineWidthMinPixels: 3,
        }),
    ],
  };
};
