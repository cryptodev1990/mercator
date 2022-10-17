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

const GeofenceMap = () => {
  const { viewport, setViewport } = useViewport();
  const { cursorMode, setOptions, setCursorMode } = useCursorMode();
  const { mapRef, clearSelectedFeatureIndexes, deleteShapes } = useShapes();

  const { selectedUuids, clearSelectedShapeUuids } = useSelectedShapes();

  const { deckRef } = useContext(DeckContext);

  // register the backspace key to delete a shape if a shape is selected
  useEffect(() => {
    const bspaceHandler = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement) {
        return;
      }
      if (event.key === "Backspace") {
        if (selectedUuids) {
          for (const uuid of selectedUuids) {
            deleteShapes([uuid], {
              onSuccess: () => {
                clearSelectedShapeUuids();
                setCursorMode(EditorMode.ViewMode);
              },
            });
          }
        }
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
  }, [selectedUuids, deleteShapes]);

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
        getCursor={(e) => getCursorFromCursorMode(e, cursorMode)}
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
