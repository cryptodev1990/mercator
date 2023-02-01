import { useContext } from "react";
import { GeofencerContext } from "../contexts/geofencer-context";
import { GeoShapeWriteContext } from "../contexts/geoshape-write/context";
import { GeoShapeMetadataContext } from "../contexts/geoshape-metadata/context";

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
    tileUpdateCount,
    setTileUpdateCount,
    tilePropertyChange,
    setTilePropertyChange,
  } = useContext(GeofencerContext);

  const gswc = useContext(GeoShapeWriteContext);
  const gsmc = useContext(GeoShapeMetadataContext);

  function clearSelectedFeatureIndexes() {
    setSelectedFeatureIndexes([]);
  }

  return {
    ...gswc,
    ...gsmc,
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
    tileUpdateCount,
    setTileUpdateCount,
    tilePropertyChange,
    setTilePropertyChange,
  };
};
