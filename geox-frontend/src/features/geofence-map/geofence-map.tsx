import DeckGL from "@deck.gl/react";

import StaticMap from "react-map-gl";

// @ts-ignore
import { useCursorMode } from "./hooks/use-cursor-mode";

import { EditorMode } from "./cursor-modes";
import { useLayers } from "./hooks/use-layers/use-layers";
import { useViewport } from "./hooks/use-viewport";
import { useShapes } from "./hooks/use-shapes";
import { useContext, useEffect } from "react";
import { useBulkDeleteShapesMutation } from "./hooks/openapi-hooks";
import { toast } from "react-hot-toast";
import { DeckContext } from "./contexts/deck-context";

const GeofenceMap = () => {
  const { viewport, setViewport } = useViewport();
  const { cursorMode, setOptions } = useCursorMode();
  const {
    selectedShapeUuids,
    mapRef,
    clearSelectedShapeUuids,
    clearSelectedFeatureIndexes,
  } = useShapes();

  const { deckRef } = useContext(DeckContext);

  const { mutate: deleteShapes } = useBulkDeleteShapesMutation();

  // register the backspace key to delete a shape if a shape is selected
  useEffect(() => {
    const bspaceHandler = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement) {
        return;
      }
      if (event.key === "Backspace") {
        if (selectedShapeUuids) {
          const selectedShapeUuidsArray = Object.keys(selectedShapeUuids);
          for (const uuid of selectedShapeUuidsArray) {
            deleteShapes([uuid]);
          }
        }
      }
    };

    function undoHandler(event: KeyboardEvent) {
      if (event.key === "z" && event.metaKey) {
        toast.error("Undo is not currently supported.");
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
  }, [selectedShapeUuids, deleteShapes]);

  const { layers } = useLayers();

  const getTooltip = (info: any) => {
    if (!info || !info.object || !info.object.properties) {
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

  return (
    <div ref={mapRef}>
      <DeckGL
        ref={deckRef}
        initialViewState={viewport}
        onViewStateChange={({ viewState, oldViewState }) =>
          setViewport(viewState)
        }
        // @ts-ignore
        getCursor={(e) => {
          switch (cursorMode) {
            case EditorMode.ViewMode:
              if (e.isDragging) {
                return "grabbing";
              }
              if (e.isHovering) {
                return "pointer";
              }
              return "grab";
            case EditorMode.EditMode:
            case EditorMode.LassoDrawMode:
              return "crosshair";
            case EditorMode.SplitMode:
              return 'url("/scissors.png"), cell';
            case EditorMode.ModifyMode:
              if (e.isDragging) {
                return "grabbing";
              }
              if (e.isHovering) {
                return "pointer";
              }
              return "grab";
            default:
              return "pointer";
          }
        }}
        controller={{
          // @ts-ignore
          doubleClickZoom: false,
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
            attrib.innerText = "© Mercator Labs ";
            attrib.style.color = "black";
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
