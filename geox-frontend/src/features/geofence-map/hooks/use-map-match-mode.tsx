import { DrawLineStringMode } from "@nebula.gl/edit-modes";

import { lineToPolygon } from "@turf/turf";

import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { useEffect, useState } from "react";
import { Feature, GetAllShapesRequestType } from "../../../client";
import { useDebounce } from "../../../hooks/use-debounce";
import { mapMatch } from "../api/gis";
import { geoShapesToFeatureCollection } from "../utils";
import { useAddShapeMutation, useGetAllShapesQuery } from "./openapi-hooks";

export const useMapMatchMode = ({
  getFillColorFunc,
  selectedFeatureIndexes,
}: {
  getFillColorFunc: (datum: any) => number[];
  selectedFeatureIndexes: any[];
}) => {
  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);
  const { mutate: addShape } = useAddShapeMutation();

  const [mapmatch, setMapMatch] = useState([]);
  const debouncedMapMatch = useDebounce(mapmatch, 1000);

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

  const layer = new EditableGeoJsonLayer({
    id: "geojson",
    pickable: true,
    data: geoShapesToFeatureCollection(shapes),
    // @ts-ignore
    getFillColor: getFillColorFunc,
    // @ts-ignore
    selectedFeatureIndexes,
    // @ts-ignore
    mode: DrawLineStringMode,
    onEdit: ({
      updatedData,
      editType,
    }: {
      updatedData: any;
      editType: string;
    }) => {
      console.log(editType);
      if (editType === "addFeature") {
        setMapMatch(updatedData.features[updatedData.features.length - 1]);
        return;
      }
    },
  });
  return { layer };
};
