import React, { useMemo } from "react";
import { GeoJsonLayer } from "@deck.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { featureToFeatureCollection } from "../../utils";
import { useCursorMode } from "../use-cursor-mode";
import { useShapes } from "../use-shapes";
import _ from "lodash";
import { Feature, simplify } from "@turf/turf";
import { useTiles } from "./use-tiles";
import { useModifyLayer } from "./use-modify-layer";
import { useEditLayer } from "./use-edit-layer";
import { useSelectedShapes } from "../use-selected-shapes";
import { useImageLayer } from "./use-image-layer";
import { SelectionLayer } from "@nebula.gl/layers";
import { addShapesToSelectedShapesAction } from "features/geofence-map/contexts/selection/actions";
import { useSelectedShapesUuids } from "../use-selected-shapes-uuids";

export const useLayers = () => {
  const { tentativeShapes, deletedShapeIds } = useShapes();

  const { selectedShapes, dispatch: selectionDispatch } = useSelectedShapes();

  const selectedShapesUuids = useSelectedShapesUuids();
  const memoizedTentativeShapes = useMemo(
    () =>
      simplify(
        {
          type: "FeatureCollection",
          features: tentativeShapes.map((x) => x.geojson) as Feature[],
        },
        { tolerance: 0.001 }
      ),
    [tentativeShapes.length]
  );

  const tiles = useTiles();
  const editLayer = useEditLayer();
  const modifyLayer = useModifyLayer();
  const imageLayer = useImageLayer();

  const { cursorMode, setCursorMode } = useCursorMode();

  return {
    layers: [
      selectedShapes &&
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
      selectedShapes &&
        cursorMode === EditorMode.ViewMode &&
        new GeoJsonLayer({
          id: "selected-shapes",
          pickable: true,
          // @ts-ignore
          getFillColor: (d: any) => {
            const uuid = d?.properties?.__uuid;
            if (selectedShapesUuids.includes(uuid)) return [0, 0, 255];
            return [0, 0, 255, 100];
          },
          updateTriggers: {
            getLineColor: [selectedShapesUuids.length],
            getFillColor: [selectedShapesUuids.length],
          },
          getLineColor: [128, 128, 128, 255],
          lineWidthMinPixels: 1,
          onClick: (info) => {
            const { object } = info;
            if (object) {
              setCursorMode(EditorMode.ModifyMode);
            } else {
            }
          },
          stroked: true,
          filled: true,
          // @ts-ignore
          data: { type: "FeatureCollection", features: selectedShapes },
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
          data: memoizedTentativeShapes,
          pointRadiusMinPixels: 7,
        }),
      modifyLayer,
      cursorMode === EditorMode.MultiSelectMode &&
        new SelectionLayer({
          id: "selection",
          // @ts-ignore
          selectionType: "polygon",
          // @ts-ignore
          onSelect: ({ pickingInfos }) => {
            const newObjs = [];
            for (const obj of pickingInfos) {
              if (!deletedShapeIds.includes(obj.object.properties.__uuid)) {
                newObjs.push(obj.object);
              }
            }
            const distinctShapes = _.uniqBy(newObjs, "properties.__uuid");
            selectionDispatch(addShapesToSelectedShapesAction(distinctShapes));
            setCursorMode(EditorMode.ViewMode);
          },
          layerIds: ["gf-mvt", "optimistic-layer"],
          getTentativeFillColor: () => [255, 0, 255, 100],
          getTentativeLineColor: () => [0, 0, 255, 255],
          getTentativeLineDashArray: () => [0, 0],
          lineWidthMinPixels: 3,
        }),
    ],
  };
};
