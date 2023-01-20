import DeckGL from "@deck.gl/react";

import StaticMap from "react-map-gl";

// @ts-ignore
import { useCursorMode } from "../../hooks/use-cursor-mode";
import { EditorMode } from "../../cursor-modes";
import { useLayers } from "../../hooks/use-layers/use-layers";
import { useViewport } from "../../hooks/use-viewport";
import { useShapes } from "../../hooks/use-shapes";
import { useContext, useEffect } from "react";
import { DeckContext } from "../../contexts/deck-context";
import { useSelectedShapes } from "../../hooks/use-selected-shapes";
import { getCursorFromCursorMode } from "./utils";
import "../../../../../node_modules/mapbox-gl/dist/mapbox-gl.css";
import { useIsochrones } from "../../../../hooks/use-isochrones";
import { UIContext } from "../../contexts/ui-context";
import _ from "lodash";
import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";

const GeofenceMap = () => {
  const { viewport, setViewport } = useViewport();
  const { cursorMode, setOptions, setCursorMode } = useCursorMode();
  const {
    mapRef,
    clearSelectedFeatureIndexes,
    deleteShapes,
    addShape,
    setShapeForPropertyEdit,
    deletedShapeIdSet,
  } = useShapes();

  const { data: allNamespaces } = useGetNamespaces();
  const {
    selectedUuids,
    multiSelectedShapesUuids,
    clearSelectedShapeUuids,
    isSelected,
    setSelectedShapeUuid,
    addShapesToMultiSelectedShapes,
    removeShapeFromMultiSelectedShapes,
  } = useSelectedShapes();

  const { deckRef, hoveredUuid, setHoveredUuid } = useContext(DeckContext);
  const { getIsochrones } = useIsochrones();
  const { isochroneParams } = useContext(UIContext);

  // register the backspace key to delete a shape if a shape is selected
  useEffect(() => {
    const bspaceHandler = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement) {
        return;
      }
      if (event.key === "Backspace" && !event.metaKey && selectedUuids.length) {
        deleteShapes(selectedUuids, {
          onSuccess: () => {
            clearSelectedShapeUuids();
            setCursorMode(EditorMode.ViewMode);
          },
        });
      }
      if (
        event.key === "Backspace" &&
        event.metaKey &&
        multiSelectedShapesUuids.length
      ) {
        deleteShapes(multiSelectedShapesUuids, {
          onSuccess: () => {
            clearSelectedShapeUuids();
            setCursorMode(EditorMode.ViewMode);
          },
        });
      }
    };

    function undoHandler(event: KeyboardEvent) {
      if (event.target instanceof HTMLInputElement) {
        return;
      }
      if (event.key === "z" && event.metaKey && event.shiftKey) {
        // redo();
      } else if (event.key === "z" && event.metaKey) {
        // undo();
      }
    }

    function escFunction(event: KeyboardEvent) {
      if (event.key === "Escape") {
        // @ts-ignore
        setOptions((prevOptions) => {
          return { ...prevOptions, cursorMode: EditorMode.ViewMode };
        });
        clearSelectedFeatureIndexes();
        clearSelectedShapeUuids();
        setShapeForPropertyEdit(null);
      }
    }

    document.addEventListener("keydown", bspaceHandler);
    document.addEventListener("keydown", escFunction);
    document.addEventListener("keydown", undoHandler);
    return () => {
      document.removeEventListener("keydown", bspaceHandler);
      document.removeEventListener("keydown", escFunction);
      document.removeEventListener("keydown", undoHandler);
    };
  }, [multiSelectedShapesUuids, selectedUuids, deleteShapes]);

  const { layers } = useLayers();

  const getTooltip = (info: any) => {
    if (!info || !info.object || !info.object.properties) {
      return null;
    }
    if (deletedShapeIdSet.has(info.object.properties.__uuid)) {
      return null;
    }
    if (cursorMode === EditorMode.ViewMode) {
      return {
        text: `${info.object.properties.name || "Shape"}`,
        className: "pointer-events-none",
      };
    }
    return null;
  };

  const handleLeftClick = (event: MouseEvent) => {
    const selectedShape = allNamespaces
      ?.flatMap((x) => x.shapes ?? [])
      .find((shape) => isSelected(shape.uuid));
    if (
      selectedShape &&
      (cursorMode === EditorMode.ViewMode ||
        cursorMode === EditorMode.ModifyMode)
    ) {
      setShapeForPropertyEdit(selectedShape);
    }
  };

  useEffect(() => {
    if (mapRef?.current) {
      let ref = mapRef.current;
      ref.addEventListener("click", handleLeftClick, false);

      return () => {
        ref.removeEventListener("click", handleLeftClick, false);
      };
    }
  }, [mapRef, selectedUuids]);

  return (
    <div ref={mapRef}>
      <DeckGL
        ref={deckRef}
        initialViewState={viewport}
        onViewStateChange={({ viewState, oldViewState }) =>
          setViewport(viewState)
        }
        onClick={({ x, y, coordinate }: any, e: any) => {
          const multipleObjects = deckRef.current.pickMultipleObjects({ x, y });

          const nonDeletedShapes = multipleObjects.filter(
            (feature: any) =>
              ![...deletedShapeIdSet].includes(feature.object.properties.__uuid)
          );

          const object = nonDeletedShapes[0]?.object;

          if (window.location.hash === "#click") {
          }

          if (cursorMode === EditorMode.DrawIsochroneMode) {
            getIsochrones(
              coordinate as number[],
              isochroneParams.timeInMinutes,
              isochroneParams.travelMode || "car"
            ).then((isochrones) => {
              addShape({
                name: "Isochrone",
                geojson: isochrones,
              });
            });
            return;
          }

          if (!object || !object.properties?.__uuid) {
            return;
          }
          const uuid = object.properties.__uuid;
          if (deletedShapeIdSet.has(uuid)) {
            return;
          }
          if (cursorMode === EditorMode.SplitMode) {
            return;
          }
          // if you click already selected shape, deselect it
          if (
            !selectedUuids.length &&
            e.leftButton &&
            cursorMode === EditorMode.ViewMode &&
            e.changedPointers[0].metaKey &&
            multiSelectedShapesUuids.includes(uuid)
          ) {
            removeShapeFromMultiSelectedShapes(uuid);
          }
          if (
            !selectedUuids.length &&
            e.leftButton &&
            cursorMode === EditorMode.ViewMode &&
            e.changedPointers[0].metaKey &&
            !multiSelectedShapesUuids.includes(uuid)
          ) {
            const filteredObject = {
              ...object,
              properties: _.omit(object.properties, ["layerName"]),
            };
            addShapesToMultiSelectedShapes([filteredObject]);
          }

          if (
            e.leftButton &&
            (cursorMode === EditorMode.ViewMode ||
              cursorMode === EditorMode.ModifyMode) &&
            !isSelected(uuid) &&
            !e.changedPointers[0].metaKey
          ) {
            setSelectedShapeUuid(uuid);
          }
        }}
        onHover={({ object, x, y }: any) => {
          // handle hover across two tile layers
          if (!object || !object.properties?.__uuid) {
            if (hoveredUuid) {
              setHoveredUuid(null);
            }
            return;
          }
          // console.log("hovered", object.properties);
          const uuid = object.properties.__uuid;
          if (deletedShapeIdSet.has(uuid)) {
            return [0, 0, 0, 0];
          }
          if (uuid === hoveredUuid || cursorMode === EditorMode.SplitMode) {
            return;
          }
          setHoveredUuid(uuid);
        }}
        // @ts-ignore
        getCursor={(e) => getCursorFromCursorMode(e, cursorMode)}
        controller={{
          // @ts-ignore
          doubleClickZoom: false,
          touchRotate: false,
          dragRotate: false,
        }}
        useDevicePixels={true}
        // @ts-ignore
        layers={layers}
        getTooltip={getTooltip}
      >
        <StaticMap
          mapStyle={"mapbox://styles/mapbox/light-v9"}
          onLoad={(map: any) => {
            const attrib = document.createElement("span");
            attrib.innerText = "© Mercator ";
            attrib.style.color = "#2d2d2d";
            document
              .getElementsByClassName("mapboxgl-ctrl-attrib-inner")[0]
              .prepend(attrib);
            document.getElementsByClassName("mapbox-improve-map")[0].remove();
          }}
          mapboxApiAccessToken={process.env.REACT_APP_MAPBOX_TOKEN}
        />
      </DeckGL>
    </div>
  );
};

export { GeofenceMap };
