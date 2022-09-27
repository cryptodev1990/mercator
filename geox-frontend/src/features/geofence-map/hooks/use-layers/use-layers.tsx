import { GeoJsonLayer } from "@deck.gl/layers";
import { MVTLayer } from "@deck.gl/geo-layers";
import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { EditorMode } from "../../cursor-modes";
import { useMapMatchMode } from "../use-map-match-mode";

import {
  ViewMode,
  DrawPolygonMode,
  SplitPolygonMode,
  DrawPolygonByDraggingMode,
  // ModifyMode,
} from "@nebula.gl/edit-modes";
import { featureToFeatureCollection } from "../../utils";
// @ts-ignore
import { useCursorMode } from "../use-cursor-mode";
import { useEditFunction } from "./use-edit-function";
import { useShapes } from "../use-shapes";
import { Feature, GeoShape } from "../../../../client";
import { useEffect, useState } from "react";
import { useUpdateShapeMutation } from "../openapi-hooks";
import { useViewport } from "../use-viewport";

import { ModifyMode } from "../../../../lib/mercator-modify-mode/MercatorModifyMode";
import { useAuth0 } from "@auth0/auth0-react";

export const useLayers = () => {
  const { getAccessTokenSilently } = useAuth0();
  const [accessToken, setAccessToken] = useState<any>(null);

  useEffect(() => {
    getAccessTokenSilently({
      audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
      ignoreCache: false,
      detailedResponse: true,
    }).then((token) => {
      setAccessToken(token.id_token);
    });
  }, []);

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

  const { mutate: updateShape, isLoading } = useUpdateShapeMutation();
  const { viewport } = useViewport();

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

  useEffect(() => {}, [localData]);

  const { cursorMode, setCursorMode } = useCursorMode();

  const SELECTED_RGB = [255, 0, 0, 150];

  function getFillColorFunc(datum: Feature) {
    if (selectedShapeUuids[datum?.properties?.__uuid]) {
      return SELECTED_RGB;
    }
    if (isLoading) {
      return [255, 255, 255, 100];
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
      window.location.hash === "#tiling" &&
        accessToken !== null &&
        new MVTLayer({
          id: "geofence-mvt",
          data:
            process.env.REACT_APP_BACKEND_URL +
            "/backsplash/generate_shape_tile/{z}/{x}/{y}",
          loadOptions: {
            fetch: {
              method: "GET",
              headers: {
                Authorization: `Bearer ${accessToken}`,
              },
            },
          },
          onHover: ({ object, x, y }) => {
            if (object) {
              // @ts-ignore
              const { properties } = object;
              console.log(properties);
              // @ts-ignore
            }
          },
          pickable: true,
          maxRequests: 6,
          // @ts-ignore
          getLineColor: [192, 192, 192],
          getFillColor: [140, 170, 180],
          lineWidthMinPixels: 1,
          stroked: true,
          filled: true,
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
      [EditorMode.ModifyMode].includes(cursorMode) &&
        new EditableGeoJsonLayer({
          id: "geojson-modify",
          pickable: true,
          // @ts-ignore
          data: localData ?? [],
          // @ts-ignore
          getFillColor: getFillColorFunc,
          mode: ModifyMode,
          // @ts-ignore
          selectedFeatureIndexes,
          pickingRadius: 20,
          pickingDepth: 5,
          useUpdateTriggers: {
            getFillColor: [selectedShapeUuids, isLoading],
            getLineColor: [selectedShapeUuids, isLoading],
          },
          modeConfig: {
            viewport,
          },
          extruded: true,
          billboard: true,
          onEdit: (e: any) => {
            const { updatedData, editType, editContext } = e;
            setLocalData(updatedData);
            if (["addPosition", "removePosition"].includes(editType)) {
              updateShape({
                geojson: updatedData.features[editContext.featureIndexes[0]],
                uuid: updatedData.features[editContext.featureIndexes[0]]
                  .properties.__uuid,
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
                return [255, 0, 0, 200];
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
              lineWidthMaxPixels: 2,
              getLineColor: (d: any) => {
                return selectedShapeUuids[d?.properties?.__uuid]
                  ? [0, 0, 0, 255]
                  : [0, 0, 0, 100];
              },
              pickingRadius: 20,
              getFillColor: [0, 0, 0, 0],
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
