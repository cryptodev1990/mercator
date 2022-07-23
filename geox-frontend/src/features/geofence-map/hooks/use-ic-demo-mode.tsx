import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { useEffect, useState } from "react";
import { Feature, GetAllShapesRequestType } from "../../../client";
import { mapMatch } from "../api/gis";
import { geoShapesToFeatureCollection } from "../utils";
import { useAddShapeMutation, useGetAllShapesQuery } from "./openapi-hooks";
import { DrawLineStringMode } from "@nebula.gl/edit-modes";
import { smoothWithAverage } from "./smooth-gps";
import { ScatterplotLayer } from "@deck.gl/layers";

export const useIcDemoMode = ({
  getFillColorFunc,
  selectedFeatureIndexes,
}: {
  getFillColorFunc: (datum: any) => number[];
  selectedFeatureIndexes: any[];
}) => {
  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.USER);
  const { mutate: addShape } = useAddShapeMutation();

  const [smoothableShape, setSmoothableShape] = useState<any>(null);

  useEffect(() => {
    if (!smoothableShape) {
      return;
    }
    const clean = {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: smoothWithAverage(
          smoothableShape.geometry.coordinates
        ).map((x: any) => [x[0], x[1]]),
      },
      // TODO store general properties in the backend
      properties: { name: "Smoothed GPS trace" },
    };
    mapMatch(clean).then((linestring: any) => {
      const geojson = {
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: linestring.geometry.coordinates,
        },
        properties: {},
      } as Feature;
      addShape({ geojson, name: "Smoothed GPS trace" });
    });
  }, [smoothableShape]);

  function getLayers(render: boolean) {
    if (!render) {
      return [];
    }
    const layers = [
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
          guides: {
            pointType: "circle",
            _subLayerProps: {
              "points-circle": {
                // Styling for editHandles goes here
                type: ScatterplotLayer,
                radiusScale: 2,
                stroked: true,
                getLineWidth: 1,
                radiusMinPixels: 4,
                radiusMaxPixels: 8,
                getRadius: 2,
                getFillColor: [220, 10, 0],
                getLineColor: [250, 250, 250],
              },
            },
          },
          geojson: {
            getLineColor: (x: any) => {
              if (x.properties.name.includes("Smoothed")) {
                return [150, 255, 255];
              }
              return [255, 0, 0];
            },
          },
        },
        onEdit: ({
          updatedData,
          editType,
        }: {
          updatedData: any;
          editType: string;
        }) => {
          if (editType === "addFeature") {
            setSmoothableShape(
              updatedData.features[updatedData.features.length - 1]
            );
            addShape({
              geojson: updatedData.features[updatedData.features.length - 1],
              name: "GPS trace",
            });
            return;
          }
        },
      }),
    ];
    return layers;
  }

  return { getLayers };
};