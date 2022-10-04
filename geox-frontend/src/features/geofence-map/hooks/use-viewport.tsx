import { useContext } from "react";
import { GeofencerContext } from "../contexts/geofencer-context";
import { centroid, featureCollection, bbox } from "@turf/turf";
import { useShapes } from "./use-shapes";
import { GeoShape, GeoShapeCreate } from "../../../client";
import { bboxToZoom } from "../utils";
import { useSelectedShapes } from "./use-selected-shapes";

export const useViewport = () => {
  const { viewport, setViewport } = useContext(GeofencerContext);
  const { shapeMetadata, tentativeShapes, isSelected } = useShapes();
  const { selectedFeatureCollection } = useSelectedShapes();

  function _genShapes(category: string) {
    const selectedShapes = shapeMetadata?.filter((shape) =>
      isSelected(shape)
    ) as GeoShape[];

    let shapesForOperation: GeoShapeCreate[] | GeoShape[] = [];
    if (category === "tentative") {
      shapesForOperation = tentativeShapes;
    } else if (category === "selected") {
      shapesForOperation = selectedShapes;
    } else {
      // TODO what was this code path?
      // shapesForOperation = shapes;
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
    // get bounding box of all shapes
    if (!selectedFeatureCollection) return;
    const bounds = bbox(selectedFeatureCollection);
    const centroid = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2];
    const [latMin, latMax, lngMin, lngMax] = [
      bounds[1],
      bounds[3],
      bounds[0],
      bounds[2],
    ];
    const zoom = bboxToZoom([latMin, latMax, lngMin, lngMax]);

    if (!zoom) return;
    if (!Number.isFinite(centroid[0]) || !Number.isFinite(centroid[1])) return;

    setViewport({
      ...viewport,
      latitude: centroid[1],
      longitude: centroid[0],
      zoom,
    });
  };

  return { snapToCentroid, snapToBounds, viewport, setViewport };
};
