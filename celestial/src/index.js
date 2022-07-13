import * as ReactDOM from "react-dom/client";

import { CSVLoader } from "@loaders.gl/csv";
import { load } from "@loaders.gl/core";
import { DeckGL, PathLayer, MapView } from "deck.gl";
import { useEffect, useState } from "react";
import StaticMap from "react-map-gl";

const url =
  "https://nkkohsotcmbtyzqpxukw.supabase.co/storage/v1/object/public/logo/routes/routes.csv?t=2022-07-12T22%3A17%3A37.928Z";

const MapContainer = () => {
  const [data, setData] = useState([]);
  useEffect(() => {
    function fetchData() {
      load(url, CSVLoader, { csv: { header: false } }).then((input) => {
        setData(input);
      });
    }
    fetchData();
  }, []);
  return (
    <div className="w-screen h-screen relative">
      <DeckGL
        controller={true}
        initialViewState={{
          longitude: -122.41669,
          latitude: 37.7853,
          zoom: 11,
          pitch: 0,
          bearing: 0,
        }}
        layers={[
          new PathLayer({
            id: "path-layer",
            data: [],
            pickable: true,
            widthScale: 20,
            widthMinPixels: 2,
            getPath: (d) => d.path,
            getColor: [255, 0, 0],
            getWidth: (d) => 5,
          }),
        ]}
      >
        <MapView id="map" width="50%" controller={true}>
          <StaticMap
            mapboxAccessToken={
              "pk.eyJ1IjoiZHViZXIxMCIsImEiOiJjbDVmcDRkYTEwejFlM2pteHVpNTFteHZzIn0.Abi0pWf4xAfu3UhkidoofA"
            }
          />
        </MapView>
      </DeckGL>
    </div>
  );
};

function App() {
  return (
    <div>
      <div className="text-blue-500 bold bg-slate-200">Hey!</div>
      <MapContainer />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("react-container")).render(<App />);
