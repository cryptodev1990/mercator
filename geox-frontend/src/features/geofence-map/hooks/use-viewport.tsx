import { useContext } from "react";
import { GeofencerContext } from "../contexts/geofencer-context";
import { centroid, featureCollection, bbox } from "@turf/turf";
import { useShapes } from "./use-shapes";
import { GeoShape, GeoShapeCreate } from "../../../client";
import { bboxToZoom } from "../utils";

export const useViewport = () => {
  const { viewport, setViewport } = useContext(GeofencerContext);
  const { shapes, tentativeShapes, shapeIsSelected } = useShapes();
  const selectedShapes = shapes?.filter((shape) =>
    shapeIsSelected(shape)
  ) as GeoShape[];

  function _genShapes(category: string) {
    let shapesForOperation: GeoShapeCreate[] | GeoShape[] = [];
    if (category === "tentative") {
      shapesForOperation = tentativeShapes;
    } else if (category === "selected") {
      shapesForOperation = selectedShapes;
    } else {
      shapesForOperation = shapes;
    }
    return shapesForOperation;
  }

  const snapToCentroid = ({ category }: { category: string }) => {
    let shapesForCentroid: GeoShapeCreate[] | GeoShape[] = _genShapes(category);
    const flattened = shapesForCentroid.map((shape) => shape.geojson);
    const ctr = centroid(featureCollection(flattened as any));
    const [lng, lat] = ctr.geometry.coordinates;
    setViewport({
      ...viewport,
      latitude: lat,
      longitude: lng,
    });
  };

  const snapToBounds = ({ category }: { category: string }) => {
    let shapesForBounds: GeoShapeCreate[] | GeoShape[] = _genShapes(category);
    // get bounding box of all shapes
    const flattened = shapesForBounds.map((shape) => shape.geojson);
    const bounds = bbox(featureCollection(flattened as any));
    const centroid = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2];
    const [latMin, latMax, lngMin, lngMax] = [
      bounds[1],
      bounds[3],
      bounds[0],
      bounds[2],
    ];
    const zoom = bboxToZoom([latMin, latMax, lngMin, lngMax]);

    setViewport({
      ...viewport,
      latitude: centroid[1],
      longitude: centroid[0],
      zoom,
    });
  };

  return { snapToCentroid, snapToBounds, viewport, setViewport };
};
