import DeckGL from "@deck.gl/react";

import { featureCollection } from "@turf/turf";

import StaticMap from "react-map-gl";
import { GeoJsonLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer, SelectionLayer } from "@nebula.gl/layers";
import {
  ViewMode,
  DrawPolygonMode,
  DrawPolygonByDraggingMode,
  TranslateMode,
  DrawLineStringMode,
} from "@nebula.gl/edit-modes";
import { geoShapesToFeatureCollection } from "./utils";
import {
  useAddShapeMutation,
  useGetAllShapesQuery,
} from "./hooks/openapi-hooks";

import { useEditableMode } from "./tool-button-bank/hooks";
import { lineToPolygon } from "@turf/turf";

import { Feature, GetAllShapesRequestType } from "../../client";
import { useSelectedShapes } from "./metadata-editor/hooks";
import { MODES } from "./tool-button-bank/modes";
import { useContext, useEffect, useState } from "react";
import { GeofencerContext } from "./context";
import { useDebounce } from "../../hooks/use-debounce";
import { mapMatch } from "./hooks/gis-hooks";

const selectedFeatureIndexes: any[] = [];
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;

const GeofenceMap = () => {
  const { viewport } = useContext(GeofencerContext);
  const { editableMode } = useEditableMode();
  const { isSelected, appendSelected } = useSelectedShapes();
  const [mapmatch, setMapMatch] = useState([]);
  const debouncedMapMatch = useDebounce(mapmatch, 1000);

  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);
  const { mutate: addShape } = useAddShapeMutation();

  useEffect(() => {
    mapMatch(debouncedMapMatch).then((linestring: any) => {
      const newPoly = lineToPolygon({
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: linestring.coordinates,
        },
        properties: {},
      }) as Feature;
      addShape({ geojson: newPoly, name: "Map matched polygon" });
    });
  }, [debouncedMapMatch]);

  function getFillColorFunc(datum: any) {
    if (isSelected(datum.properties.uuid)) {
      return [255, 0, 0, 150];
    }
    return [255, 255, 0, 150];
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
    editableMode === MODES.DrawPolygonFromRouteMode &&
      new EditableGeoJsonLayer({
        id: "geojson",
        pickable: true,
        data: geoShapesToFeatureCollection(shapes),
        // @ts-ignore
        getFillColor: getFillColorFunc,
        // @ts-ignore
        selectedFeatureIndexes,
        // @ts-ignore
        mode: DrawLineStringMode,
        _subLayerProps: {
          // guides: {
          //   getLineColor: (guide: any) => {
          //     if (guide.properties.guideType === "tentative") {
          //       return [255, 0, 200, 0];
          //     } else if (guide.properties.editHandleType === "existing") {
          //       return [255, 0, 150, 255];
          //     }
          //     return [0, 0, 250, 255];
          //   },
          //   getPointRadius: (guide: any) => {
          //     if (guide.properties.guideType === "tentative") {
          //       return 100;
          //     }
          //   },
          // },
        },

        onEdit: ({
          updatedData,
          editType,
        }: {
          updatedData: any;
          editType: string;
        }) => {
          // TODO click one point, set it.
          // TODO start generating routes between the current point
          // and the prospective second point
          // TODO on click, add this polyline to a shape
          // TODO, if the shape gets clicked, close it
          // see docs https://nebula.gl/docs/api-reference/modes/overview#DrawLineStringMode
          console.log(editType);
          if (editType === "addFeature") {
            setMapMatch(updatedData.features[updatedData.features.length - 1]);
            return;
          }
        },
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
