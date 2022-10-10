import { useContext } from "react";
import { GeofencerContext } from "../contexts/geofencer-context";
import { useBulkAddShapesMutation } from "./openapi-hooks";

export const useShapes = () => {
  const {
    // Information about a shape, such as its name and UUID. It does not contain the shape's geometry.
    shapeMetadata,
    setShapeMetadata,
    // Used as a temporary storage for shapes that are being added to the map, either through uploads or the command palette
    tentativeShapes,
    setTentativeShapes,
    shapeForPropertyEdit,
    setShapeForPropertyEdit,
    mapRef,
    shapeMetadataIsLoading,
    virtuosoRef,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
    numShapes,
    numShapesIsLoading,
  } = useContext(GeofencerContext);

  function scrollToSelectedShape(i: number) {
    if (virtuosoRef.current === null) {
      return;
    }
    virtuosoRef.current.scrollToIndex({
      index: i,
      align: "start",
      behavior: "smooth",
    });
  }

  function clearSelectedFeatureIndexes() {
    setSelectedFeatureIndexes([]);
  }

  const { mutate: addShapesBulk, isLoading: bulkAddLoading } =
    useBulkAddShapesMutation();

  return {
    shapeMetadata,
    setShapeMetadata,
    shapeMetadataIsLoading,
    // API - num shapes
    numShapes,
    numShapesIsLoading,
    // API call - bulk load
    addShapesBulk,
    bulkAddLoading,
    // metadata editing
    shapeForPropertyEdit,
    setShapeForPropertyEdit,
    // Shapes that could be added to the map
    tentativeShapes,
    setTentativeShapes,
    // Ref for the sidebar elements
    virtuosoRef,
    // Ref for the deck.gl container itself
    mapRef,
    scrollToSelectedShape,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
    clearSelectedFeatureIndexes,
  };
};
