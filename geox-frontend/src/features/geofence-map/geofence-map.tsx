import DeckGL from "@deck.gl/react";

import StaticMap from "react-map-gl";

import { useCursorMode } from "./hooks/use-cursor-mode";

import { useContext } from "react";
// @ts-ignore
import { GeofencerContext } from "./context";
import { EditorMode } from "./cursor-modes";
import { useLayers } from "./hooks/use-layers/use-layers";

const GeofenceMap = () => {
  const { viewport } = useContext(GeofencerContext);
  const { cursorMode } = useCursorMode();

  const layers = useLayers();

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
    <div>
      <DeckGL
        initialViewState={viewport}
        controller={{
          doubleClickZoom: false,
        }}
        useDevicePixels={false}
        // @ts-ignore
        layers={layers}
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
