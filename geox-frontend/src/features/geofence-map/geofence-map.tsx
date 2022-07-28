import DeckGL from "@deck.gl/react";

import { difference } from "@turf/turf";

import StaticMap from "react-map-gl";
import { GeoJsonLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer, SelectionLayer } from "@nebula.gl/layers";
import {
  ViewMode,
  DrawPolygonMode,
  DrawPolygonByDraggingMode,
  TranslateMode,
} from "@nebula.gl/edit-modes";
import {
  featureToFeatureCollection,
  geoShapesToFeatureCollection,
} from "./utils";
import {
  useAddShapeMutation,
  useGetAllShapesQuery,
} from "./hooks/openapi-hooks";

// @ts-ignore
import { useEditableMode } from "./tool-button-bank/hooks";

import {
  Feature,
  GeoShape,
  GetAllShapesRequestType,
  Polygon,
} from "../../client";
// @ts-ignore
import { useEditableShape, useSelectedShapes } from "./shape-editor/hooks";

// @ts-ignore
import { MODES } from "./tool-button-bank/modes";
import { useContext, useEffect, useState } from "react";
import { GeofencerContext } from "./context";
import { useMapMatchMode } from "./hooks/use-map-match-mode";
import { useIcDemoMode } from "./hooks/use-ic-demo-mode";
import { PathStyleExtension } from "@deck.gl/extensions";
import { RGBAColor } from "deck.gl";

const selectedFeatureIndexes: any[] = [];

const GeofenceMap = () => {
  const { viewport, tentativeShapes } = useContext(GeofencerContext);
  const { editableMode, options: editOptions } = useEditableMode();
  const { isSelected, appendSelected } = useSelectedShapes();

  const { setShapeForEdit } = useEditableShape();
  const { mutate: addShape } = useAddShapeMutation();

  function getFillColorFunc(datum: any) {
    if (isSelected(datum.properties.uuid)) {
      return [255, 0, 0, 150];
    }
    return [255, 255, 0, 150];
  }

  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);

  const modeArgs = {
    getFillColorFunc,
    selectedFeatureIndexes,
  };
  const { layer: mapMatchModeLayer } = useMapMatchMode(modeArgs);
  const { getLayers: getIcDemoLayers } = useIcDemoMode(modeArgs);

  // EditableGeojsonLayer function
  function onEdit({
    updatedData,
    editType,
  }: {
    updatedData: any;
    editType: string;
  }) {
    if (editType !== "addFeature") {
      return;
    }

    let mostRecentShape: Feature =
      updatedData.features[updatedData.features.length - 1];

    if (editOptions.denyOverlap && shapes) {
      for (const shape of shapes) {
        if (shape.uuid === mostRecentShape.properties.uuid) {
          continue;
        }
        const diffShape = difference(
          mostRecentShape as any,
          shape.geojson.geometry as any
        );
        if (diffShape === null) {
          return;
        }
        mostRecentShape = diffShape as Feature;
      }
    }
    const newShape = {
      geojson: mostRecentShape,
      name: "New shape",
    };
    addShape(newShape, {
      onSuccess: (data: any) => {
        setShapeForEdit(data as GeoShape);
      },
    });
  }

  const layers = [
    tentativeShapes &&
      tentativeShapes.length > 0 &&
      new GeoJsonLayer({
        id: "geojson-i",
        pickable: true,
        // @ts-ignore
        getFillColor: [0, 0, 255, 100],
        stroked: true,
        filled: true,
        data: {
          type: "FeatureCollection",
          features: tentativeShapes.map((x) => x.geojson),
        },
        mode: ViewMode,
      }),
    editableMode === MODES.ViewMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        mode: ViewMode,
      }),
    [MODES.EditMode, MODES.LassoDrawMode].includes(editableMode) &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        // @ts-ignore
        selectedFeatureIndexes,
        modeConfig: {
          enableSnapping: true,
        },
        mode:
          editableMode === MODES.EditMode
            ? DrawPolygonMode
            : DrawPolygonByDraggingMode,
        onEdit,
      }),
    editableMode === MODES.LassoMode &&
      new SelectionLayer({
        id: "selection",
        // @ts-ignore
        selectionType: "rectangle",
        onSelect: ({ pickingInfos }: { pickingInfos: any }) => {
          const uuids = pickingInfos.map((x: any) => {
            return { uuid: x.object.properties.uuid };
          });
          appendSelected(uuids, true);
        },
        layerIds: ["geojson-read"],
        getTentativeFillColor: () => [255, 0, 255, 100],
        getTentativeLineColor: () => [0, 0, 255, 255],
        getTentativeLineDashArray: () => [0, 0],
        lineWidthMinPixels: 3,
      }),
    editableMode === MODES.LassoMode &&
      new GeoJsonLayer({
        id: "geojson-read",
        // @ts-ignore
        data: geoShapesToFeatureCollection(shapes),
        pickable: true,
        // @ts-ignore
        getFillColor: getFillColorFunc,
        lineWidthMinPixels: 3,
      }),
    editableMode === MODES.TranslateMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        // @ts-ignore
        selectedFeatureIndexes,
        // @ts-ignore
        mode: TranslateMode,
      }),
    editableMode === MODES.DrawPolygonFromRouteMode && mapMatchModeLayer,
    ...getIcDemoLayers(editableMode === MODES.InstacartDemoMode),
  ];

  const getTooltip = (info: any) => {
    if (!info.object) {
      return null;
    }
    if (editableMode === MODES.ViewMode) {
      return `${info.object.properties.name}`;
    }
    return null;
  };

  return (
    <div>
      <DeckGL
        initialViewState={viewport}
        controller={{
          doubleClickZoom: false,
        }}
        useDevicePixels={false}
        // @ts-ignore
        layers={layers}
        getTooltip={getTooltip}
      >
        <StaticMap
          mapStyle={"mapbox://styles/mapbox/light-v9"}
          onLoad={(map: any) => {
            const attrib = document.createElement("span");
            attrib.innerText = "© Mercator Labs ";
            attrib.style.color = "black";
            document
              .getElementsByClassName("mapboxgl-ctrl-attrib-inner")[0]
              .prepend(attrib);
            document.getElementsByClassName("mapbox-improve-map")[0].remove();
          }}
          mapboxApiAccessToken={process.env.REACT_APP_MAPBOX_TOKEN}
        />
      </DeckGL>
    </div>
  );
};

export { GeofenceMap };
