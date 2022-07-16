import DeckGL from "@deck.gl/react";

import { featureCollection } from "@turf/turf";

import StaticMap from "react-map-gl";
import { GeoJsonLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer, SelectionLayer } from "@nebula.gl/layers";
import {
  ViewMode,
  DrawPolygonMode,
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
import { useContext } from "react";
import { GeofencerContext } from "./geofencer-view";

const selectedFeatureIndexes: any[] = [];
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;

const GeofenceMap = () => {
  const { viewport } = useContext(GeofencerContext);
  const { editableMode } = useEditableMode();
  const { isSelected, appendSelected } = useSelectedShapes();

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
    [MODES.EditMode, MODES.LassoDrawMode].includes(editableMode) &&
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
        // onHover: (info: any) => {
        //   console.log(info);
        // },
        // @ts-ignore
        mode: TranslateMode,
        // onEdit: (e: any) => console.log(e),
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
          mapStyle={"mapbox://styles/mapbox/dark-v9"}
          mapboxApiAccessToken={MAPBOX_TOKEN}
        />
      </DeckGL>
    </div>
  );
};

export { GeofenceMap };
