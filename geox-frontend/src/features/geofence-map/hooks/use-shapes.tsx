import { useContext } from "react";
import { GeofencerContext } from "../contexts/geofencer-context";
import { GeoShapeContext } from "../contexts/geoshape/geoshape.context";

export const useShapes = () => {
  const {
    // Information about a shape, such as its name and UUID. It does not contain the shape's geometry.
    // Used as a temporary storage for shapes that are being added to the map, either through uploads or the command palette
    tentativeShapes,
    setTentativeShapes,
    shapeForPropertyEdit,
    setShapeForPropertyEdit,
    mapRef,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
  } = useContext(GeofencerContext);

  const gsc = useContext(GeoShapeContext);

  function clearSelectedFeatureIndexes() {
    setSelectedFeatureIndexes([]);
  }

  return {
    ...gsc,
    // metadata editing
    shapeForPropertyEdit,
    setShapeForPropertyEdit,
    // Shapes that could be added to the map
    tentativeShapes,
    setTentativeShapes,
    // Ref for the deck.gl container itself
    mapRef,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
    clearSelectedFeatureIndexes,
  };
};
