import DeckGL from "@deck.gl/react";
import { mvtLayer } from "./instantiated-layers";

import StaticMap from "react-map-gl";
import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { geoShapesToFeatureCollection } from "./utils";
import {
  useAddShapeMutation,
  useEditMode,
  useGetAllShapesQuery,
  useSelectedShapes,
} from "./hooks";
import { GetAllShapesRequestType } from "../../client";

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
  const { editMode } = useEditMode();
  const { mutate: addShape } = useAddShapeMutation();

  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);
  const { appendSelected, removeAllSelections, removeSelection, isSelected } =
    useSelectedShapes();

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
      return;
    }
    const mostRecentShape =
      updatedData.features[updatedData.features.length - 1];
    addShape({ geojson: mostRecentShape, name: "test" });
  }

  const layers = [
    clingToVector ? mvtLayer : null,
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
      mode: editMode,
      onEdit,
    }),
  ];

  return (
    <div>
      <DeckGL
        initialViewState={initialViewState}
        controller={true}
        useDevicePixels={false}
        // @ts-ignore
        layers={layers}
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
