import { createContext, useState } from "react";
import { IntentResponse } from "src/store/search-api";

type Layer = {
  id: number;
  data: any;
  getFillColor?: any;
  getLineColor?: any;
  getRadius?: any;
  getLineWidth?: any;
  getElevation?: any;
  filled?: boolean;
  stroked?: boolean;
  extruded?: boolean;
  wireframe?: boolean;
};

let id = 0;

type GeoContextType = {
  layers: Layer[];
  appendLayer: (layer: Layer) => void;
  removeLayer: (id: string) => void;
  getLayerFromIntentResponse: (intentResponse: IntentResponse) => Layer;
};

export const GeoContext = createContext<GeoContextType>({
  layers: [],
  appendLayer: () => {},
  removeLayer: () => {},
  getLayerFromIntentResponse: () => ({
    id: 0,
    data: {},
    getFillColor: [150, 255, 50],
    getLineColor: [150, 255, 50],
  }),
});

const GeoContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [layers, setLayers] = useState<Layer[]>([]);

  const appendLayer = (layer: Layer) => {
    setLayers([...layers, layer]);
  };

  const removeLayer = (id: string) => {
    // setLayers(layers.filter((x) => x.id !== id));
  };

  const getLayerFromIntentResponse = (intentResponse: IntentResponse) => {
    const {
      parse_result: { geom },
    } = intentResponse;
    id += 1;
    const color = [
      Math.random() * 255,
      Math.random() * 255,
      Math.random() * 255,
    ];
    return {
      id,
      data: geom,
      getFillColor: color,
      getLineColor: [255, 255, 255],
      getRadius: 100,
      filled: true,
      extruded: true,
      wireframe: true,
    };
  };

  return (
    <GeoContext.Provider
      value={{
        layers,
        appendLayer,
        removeLayer,
        getLayerFromIntentResponse,
      }}
    >
      {children}
    </GeoContext.Provider>
  );
};

export default GeoContextProvider;
