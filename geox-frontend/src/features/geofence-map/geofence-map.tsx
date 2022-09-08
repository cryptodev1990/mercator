import DeckGL from "@deck.gl/react";

import StaticMap from "react-map-gl";

// @ts-ignore
import { useCursorMode } from "./hooks/use-cursor-mode";

import { EditorMode } from "./cursor-modes";
import { useLayers } from "./hooks/use-layers/use-layers";
import { useViewport } from "./hooks/use-viewport";
import { useShapes } from "./hooks/use-shapes";

const GeofenceMap = () => {
  const { viewport, setViewport } = useViewport();
  const { cursorMode } = useCursorMode();

  const { mapRef } = useShapes();

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
        initialViewState={viewport}
        onViewStateChange={({ viewState, oldViewState }) =>
          setViewport(viewState)
        }
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
