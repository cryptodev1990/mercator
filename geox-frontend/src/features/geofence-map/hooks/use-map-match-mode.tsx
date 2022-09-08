import { DrawLineStringMode } from "@nebula.gl/edit-modes";

import { lineToPolygon } from "@turf/turf";

import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { useEffect, useState } from "react";
import { Feature } from "../../../client";
import { useDebounce } from "../../../hooks/use-debounce";
import { mapMatch } from "../api/gis";
import { featureToFeatureCollection } from "../utils";
import { useAddShapeMutation } from "./openapi-hooks";
import { useShapes } from "./use-shapes";

export const useMapMatchMode = ({
  getFillColorFunc,
  selectedFeatureIndexes,
}: {
  getFillColorFunc: (datum: any) => number[];
  selectedFeatureIndexes: any[];
}) => {
  const { shapes } = useShapes();
  const { mutate: addShape } = useAddShapeMutation();

  const [mapmatch, setMapMatch] = useState([]);
  const debouncedMapMatch = useDebounce(mapmatch, 1000);

  useEffect(() => {
    if (!debouncedMapMatch.length) {
      return;
    }
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
    // @ts-ignore
    data: featureToFeatureCollection(shapes.map((x) => x.geojson)),
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
