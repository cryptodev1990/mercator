import DeckGL from "@deck.gl/react";
import { mvtLayer } from "./instantiated-layers";

import { featureCollection, intersect } from "@turf/turf";

import StaticMap from "react-map-gl";
import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import {
  ViewMode,
  DrawPolygonMode,
  DrawPolygonByDraggingMode,
  TranslateMode,
} from "@nebula.gl/edit-modes";
import { geoShapesToFeatureCollection } from "./utils";
import {
  useAddShapeMutation,
  useGetAllShapesQuery,
} from "./hooks/openapi-hooks";

import { useEditableMode } from "./tool-button-bank/hooks";

import { GetAllShapesRequestType } from "../../client";
import { useSelectedShapes } from "./metadata-editor/hooks";
import { MODES } from "./tool-button-bank/modes";

const initialViewState = {
  longitude: -73.986022,
  maxZoom: 20,
  latitude: 40.730743,
  zoom: 12,
};

const selectedFeatureIndexes: any[] = [];
const clingToVector = false;
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;

const GeofenceMap = () => {
  const { editableMode } = useEditableMode();
  const { isSelected } = useSelectedShapes();

  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);
  const { mutate: addShape } = useAddShapeMutation();

  function getFillColorFunc(datum: any) {
    if (isSelected(datum.properties.uuid)) {
      return [255, 0, 0];
    }
    return [255, 255, 0];
  }

  // EditableGeojsonLayer function
  function onEdit({
    updatedData,
    editType,
  }: {
    updatedData: any;
    editType: string;
  }) {
    if (editType !== "addFeature") {
      if (updatedData) {
        // use turf to check for an interaction with the existing feature collection
        featureCollection(updatedData);
      }
      return;
    }
    const mostRecentShape =
      updatedData.features[updatedData.features.length - 1];
    addShape({ geojson: mostRecentShape, name: "test" });
  }

  const layers = [
    clingToVector ? mvtLayer : null,
    editableMode === MODES.ViewMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        // @ts-ignore
        selectedFeatureIndexes,
        // onHover: (info: any) => {
        //   console.log(info);
        // },
        // @ts-ignore
        mode: ViewMode,
        onEdit,
      }),
    editableMode === MODES.EditMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        // @ts-ignore
        selectedFeatureIndexes,
        // onHover: (info: any) => {
        //   console.log(info);
        // },
        // @ts-ignore
        mode: DrawPolygonMode,
        onEdit,
      }),
    editableMode === MODES.LassoMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        // @ts-ignore
        selectedFeatureIndexes,
        // onHover: (info: any) => {
        //   console.log(info);
        // },
        // @ts-ignore
        mode: DrawPolygonByDraggingMode,
        onEdit: (e: any) => console.log(e),
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
        // onHover: (info: any) => {
        //   console.log(info);
        // },
        // @ts-ignore
        mode: TranslateMode,
        onEdit: (e: any) => console.log(e),
      }),
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
        initialViewState={initialViewState}
        controller={{
          doubleClickZoom: false,
        }}
        useDevicePixels={false}
        // @ts-ignore
        layers={layers}
        getTooltip={getTooltip}
      >
        <StaticMap
          mapStyle={"mapbox://styles/mapbox/dark-v9"}
          mapboxApiAccessToken={MAPBOX_TOKEN}
        />
      </DeckGL>
    </div>
  );
};

export { GeofenceMap };
