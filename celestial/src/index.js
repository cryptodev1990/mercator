import * as ReactDOM from "react-dom/client";

import { CSVLoader } from "@loaders.gl/csv";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { load } from "@loaders.gl/core";
import {
  DeckGL,
  MapView,
  GeoJsonLayer,
  ScatterplotLayer,
  ScenegraphLayer,
  FlyToInterpolator,
} from "deck.gl";

import { SelectionLayer } from "@nebula.gl/layers";

import { useEffect, useRef, useState } from "react";
import StaticMap from "react-map-gl";
import along from "@turf/along";
import lineSlice from "@turf/line-slice";

import { toGeoJSON } from "@mapbox/polyline";
import { useInterval } from "./use-interval";

import rhumbBearing from "@turf/rhumb-bearing";
import { determineStatus, fake } from "./fake";
import length from "@turf/length";
import { DriverTable } from "./table";

const MAX_ROWS = 249;

const r = () => Math.round(Math.random() * 255);

const colorPalette = ((maxDriverId) => {
  return [...Array(1000).keys()].map((d, i) => [r(), r(), r(), 150]);
})();

const selectedFeatureIndexes = [];

const wrapFC = (fc) => {
  return {
    type: "FeatureCollection",
    features: fc,
  };
};

const MODEL_URL =
  "https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/google-3d/truck.gltf"; // eslint-disable-line

function randomCategorialColors(driverId) {
  return colorPalette[driverId];
}

function colorScale(driverId) {
  // return randomCategorialColors(driverId);
  return [255, 0, 0, 150];
}

const url =
  "https://nkkohsotcmbtyzqpxukw.supabase.co/storage/v1/object/public/logo/routes/routes.csv?t=2022-07-12T22%3A17%3A37.928Z";

const defaultViewport = {
  latitude: 33.820291694707045,
  longitude: -118.15905091193157,
  zoom: 6.738787618596184,
  pitch: 0,
  bearing: 0,
};

const MapContainer = ({ parentData }) => {
  const { selectedDrivers, positions, setPositions, setSelectedDrivers } =
    parentData;
  const [data, setData] = useState(wrapFC([]));
  const [remainingRoute, setRemainingRoute] = useState(wrapFC([]));
  const [selectionEnabled, setSelectionEnabled] = useState(false);
  const [viewState, setViewState] = useState(defaultViewport);

  const viewStateDirty = useRef(false);
  const firstRun = useRef(true);

  // Feature: Viewport changes on select
  useEffect(() => {
    if (selectedDrivers.length === 0 && viewStateDirty.current) {
      setViewState((prevView) => {
        return {
          ...prevView,
          zoom: 6.7,
          pitch: 0,
          bearing: 0,
          transitionDuration: 200,
          transitionInterpolator: new FlyToInterpolator(),
        };
      });
    } else if (selectedDrivers.length === 1) {
      viewStateDirty.current = true;
      const { latitude, longitude, bearing } = positions.filter(
        (p) => p.driverId === selectedDrivers[0]
      )[0];
      setViewState({
        latitude,
        longitude,
        bearing: -bearing,
        pitch: 60,
        zoom: 9,
        transitionDuration: 200,
        transitionInterpolator: new FlyToInterpolator(),
      });
    } else {
      viewStateDirty.current = true;
    }
  }, [selectedDrivers]);

  // Feature: CMD to select multiple drivers
  useEffect(() => {
    document.addEventListener(
      "keydown",
      (e) => {
        if (e.metaKey) {
          setSelectionEnabled(true);
        }
      },
      false
    );
    document.addEventListener(
      "keyup",
      (e) => {
        setSelectionEnabled(false);
      },
      false
    );
  }, []);

  // Feature: Read driver routes
  useEffect(() => {
    function fetchData() {
      load(url, CSVLoader, { csv: { header: false, delimiter: "\t" } }).then(
        (input) => {
          let cleanedData = [];
          let numRows = 0;
          for (const line of input) {
            const cleanLine = toGeoJSON(line.column1);
            cleanedData.push({
              type: "Feature",
              geometry: cleanLine,
              properties: { driverId: numRows },
            });
            numRows++;
            if (numRows > MAX_ROWS) {
              break;
            }
          }
          setData(wrapFC(cleanedData));
        }
      );
    }
    fetchData();
  }, []);

  // Feature: Update data
  useInterval(() => {
    const newPositions = [];
    const newRemainingRoutes = [];
    let i = 0;
    if (data.features.length === 0) {
      return;
    }
    for (const d of data.features) {
      const dist = firstRun.current ? Math.random() * 500 : Math.random() * 0.5;
      const prevPt = [positions[i]?.longitude, positions[i]?.latitude];
      const prevDist = positions[i] ? positions[i].prevDistance : 0;
      const pt = along(d, prevDist + dist, { units: "miles" });
      const bearing = rhumbBearing(pt, prevPt);
      const pctComplete = (prevDist + dist) / length(d);

      if (pctComplete >= 1) {
        newPositions.push({
          latitude: pt.geometry.coordinates[1],
          longitude: pt.geometry.coordinates[0],
          prevDistance: prevDist + dist,
          state: "delivered",
          driverId: i,
          pctComplete: 1,
          bearing: 0,
        });
      } else {
        newPositions.push({
          latitude: pt.geometry.coordinates[1],
          longitude: pt.geometry.coordinates[0],
          prevDistance: prevDist + dist,
          state: firstRun.current
            ? "en_route"
            : determineStatus(positions[i].state),
          driverId: i,
          pctComplete,
          bearing,
        });
      }
      i++;
      if (selectedDrivers.includes(d.properties.driverId)) {
        const remainingRouteSlice = lineSlice(
          pt.geometry.coordinates,
          d.geometry.coordinates[d.geometry.coordinates.length - 1],
          d
        );
        newRemainingRoutes.push(remainingRouteSlice);
      }
    }
    firstRun.current = false;

    setRemainingRoute(wrapFC(newRemainingRoutes));
    setPositions(newPositions);
  }, 500);

  return (
    <div className="w-screen h-screen relative">
      <DeckGL
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        onClick={(info) => {
          if (!info.object) {
            setSelectedDrivers([]);
          }
        }}
        controller={true}
        initialViewState={viewState}
        getCursor={({ isDragging, isHovering }) =>
          isDragging ? "grabbing" : isHovering ? "pointer" : "grab"
        }
        layers={[
          selectionEnabled &&
            new SelectionLayer({
              id: "editable-layer",
              data,
              onSelect: ({ pickingInfos }) => {
                const selectedDrivers = pickingInfos.map(
                  (p) => p.object.driverId
                );
                setSelectedDrivers(selectedDrivers);
              },
              layerIds: ["scatterplot-layer", "scenegraph-layer"],
            }),
          remainingRoute.features &&
            new GeoJsonLayer({
              id: "path-layer",
              data: remainingRoute,
              strokeWidth: 2,
              lineWidthScale: 1.5,
              getLineColor: (d) => [0, 0, 255, 150],
              lineWidthMinPixels: 1,
              pickable: true,
            }),
          new ScatterplotLayer({
            id: "scatterplot-layer",
            data: positions,
            updateTriggers: {
              getPosition: [positions],
            },
            radiusScale: 100,
            radiusMinPixels: 10,
            getRadius: (d) => {
              if (selectedDrivers.includes(d.driverId)) {
                return 1500;
              }
              return 730;
            },
            onClick: (info) => {
              const driverId = info.object.driverId;
              const newSelectedDrivers = [...selectedDrivers, driverId];
              setSelectedDrivers(newSelectedDrivers);
            },
            getFillColor: (d) => {
              if (selectedDrivers.includes(d.driverId)) {
                return [0, 0, 255, 150];
              }
              if (viewState.zoom > 8) {
                return [0, 0, 0, 0];
              }
              if (d.state === "en_route") {
                return [0, 255, 0, 150];
              }
              if (d.state === "late") {
                return [255, 0, 0, 150];
              }
              if (d.state === "delivered") {
                return [255, 255, 0, 150];
              }
              return [0, 0, 0, 0];
            },
            getLineColor: (d) => {
              if (viewState.zoom <= 8) {
                return [0, 0, 0, 0];
              }
              if (d.state === "en_route") {
                return [0, 255, 0];
              }
              if (d.state === "late") {
                return [255, 0, 0];
              }
              if (d.state === "delivered") {
                return [255, 255, 0];
              }
            },
            getLineWidth: (d) => {
              if (viewState.zoom > 8) {
                return 500
              }
              return 1
            },
            transitions: {
              getPosition: {
                duration: 450,
                easing: (x) => Math.sin((x * Math.PI) / 2),
              },
            },
            stroked: true,
            filled: true,
            radiusScale: 6,
            getPosition: (d) => [d.longitude, d.latitude],
            parameters: {
              depthTest: false
            },
            pickable: true,
          }),
          viewState.zoom > 8 &&
            new ScenegraphLayer({
              id: "scenegraph-layer",
              data: positions,
              pickable: true,
              sizeMinPixels: 10,
              scenegraph: MODEL_URL,
              extruded: true,
              getPosition: (d) => [d.longitude, d.latitude, 300],
              getSize: (d) => {
                if (selectedDrivers.includes(d.driverId)) {
                  return 300;
                }
                return 0;
              },
              onClick: (info) => {
                if (!info.object) {
                  return;
                }
                const driverId = info.object.driverId;
                if (selectedDrivers.includes(driverId)) {
                  const newSelectedDrivers = selectedDrivers.filter(
                    (d) => d !== driverId
                  );
                  setSelectedDrivers(newSelectedDrivers);
                } else {
                  const newSelectedDrivers = [...selectedDrivers, driverId];
                  setSelectedDrivers(newSelectedDrivers);
                }
              },
              getOrientation: (d) => [0, -d.bearing, 90],
              transitions: {
                getPosition: {
                  duration: 450,
                  easing: (x) => Math.sin((x * Math.PI) / 2),
                },
                getOrientation: {
                  duration: 450,
                },
              },
              sizeScale: 10,
              _lighting: "pbr",
            }),
        ]}
      >
        <MapView id="map" width="100%" controller={true}>
          <StaticMap
            // mapStyle={"mapbox://styles/mapbox/dark-v10"}
            mapStyle={
              "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json"
            }
            mapboxAccessToken={
              "pk.eyJ1IjoiZHViZXIxMCIsImEiOiJjbDVmcDRkYTEwejFlM2pteHVpNTFteHZzIn0.Abi0pWf4xAfu3UhkidoofA"
            }
          />
        </MapView>
      </DeckGL>
    </div>
  );
};

const DriverCard = ({ driver, unselect, status }) => {
  const notify = () => toast("Messaged driver");

  const [enableMessage, setEnableMessage] = useState(false);
  return (
    <div className="card w-96 bg-base-100 shadow-xl">
      <div className="absolute top-0 right-0 p-3">
        <button className="btn btn-square" onClick={unselect}>
          X
        </button>
      </div>
      <div className="card-body">
        <h2 className="card-title">
          <a className="link link-tertiary" href="#">
            {fake(driver, "name")}
          </a>{" "}
          for{" "}
          <a className="link link-tertiary" href="#">
            {fake(driver, "shipping")}
          </a>
          <div className="badge badge-info">{status}</div>
        </h2>
        {enableMessage && <textarea></textarea>}
        <div className="card-actions">
          <button
            className="btn btn-primary"
            onClick={() => {
              setEnableMessage(!enableMessage);
              enableMessage && notify();
            }}
          >
            SMS
          </button>
          {!enableMessage && <button className="btn btn-primary">Call</button>}
          {!enableMessage && (
            <button className="btn btn-warning">Take offline</button>
          )}
        </div>
      </div>
    </div>
  );
};

function ymdhms() {
  const currentTime = new Date();
  return (
    currentTime.getFullYear() +
    "-" +
    (currentTime.getMonth() + 1) +
    "-" +
    currentTime.getDate() +
    " " +
    currentTime.getHours() +
    ":" +
    currentTime.getMinutes() +
    ":" +
    currentTime.getSeconds()
  );
}

const InfoCard = ({ positions }) => {
  const [now, setNow] = useState(ymdhms());
  const [stats, setStats] = useState({});
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPulse((prevPulse) => prevPulse + 1);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setNow(ymdhms());
    const newStats = {};
    for (let i = 0; i < positions.length; i++) {
      if (positions[i].state === "late") {
        newStats.late = (newStats.late || 0) + 1;
      }
      if (positions[i].state === "en_route") {
        newStats.en_route = (newStats.en_route || 0) + 1;
      }
      if (positions[i].state === "delivered") {
        newStats.delivered = (newStats.delivered || 0) + 1;
      }
    }
    setStats(newStats);
  }, [pulse]);

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <div class="stat-desc">Last updated {now}</div>
        <div class="stats shadow">
          <div class="stat">
            <div class="stat-title">Active drivers</div>
            <div class="stat-value">{positions.length || "-"}</div>
          </div>
          <div class="stat text-green-500">
            <div class="stat-title ">En Route</div>
            <div class="stat-value">{stats.en_route || "-"}</div>
          </div>
          <div class="stat text-red-500">
            <div class="stat-title">Late</div>
            <div class="stat-value">{stats.late || "-"}</div>
          </div>
          <div class="stat text-yellow-500">
            <div class="stat-title">Idle</div>
            <div class="stat-value">{stats.delivered || "-"}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Sidebar = ({ parentData }) => {
  const { selectedDrivers, positions, setPositions, setSelectedDrivers } =
    parentData;
  return (
    <div className="relative m-4">
      {selectedDrivers.length === 1 && (
        <DriverCard
          status={positions[selectedDrivers[0]].state}
          driver={selectedDrivers[0]}
          unselect={() => setSelectedDrivers([])}
        />
      )}
      {!selectedDrivers ||
        (selectedDrivers.length === 0 && <InfoCard positions={positions} />)}
      {selectedDrivers.length > 1 && (
        <DriverTable drivers={selectedDrivers} positions={positions} />
      )}
    </div>
  );
};

function App() {
  const [positions, setPositions] = useState([]);
  const [selectedDrivers, setSelectedDrivers] = useState([]);
  const parentData = {
    selectedDrivers,
    setSelectedDrivers,
    positions,
    setPositions,
  };

  return (
    <div className="h-screen flex">
      <div className="text-slate-100 h-screen bold bg-slate-500 p-5 flex flex-col">
        <div className="bg-red-300 w-fit px-3 py-7 rounded-tl-md">
          <h1 className="uppercase font-extrabold leading-none select-none text-white text-lg">
            Celestial
          </h1>
          <span className="text-sm uppercase">
            by{" "}
            <span className="text-yellow-300 hover:text-blue-400">
              <a href="https://mercator.tech">Mercator</a>
            </span>
          </span>
        </div>
        <div className="my-5">
          <label className="label">
            <span class="label-text">Region</span>
          </label>
          <select class="select select-primary w-full max-w-xs">
            <option>Pacific</option>
            <option>US East</option>
          </select>
        </div>
      </div>

      <div className="absolute z-10 bottom-0">
        <Sidebar parentData={parentData} />
      </div>
      <div className="h-[90vh]">
        <MapContainer parentData={parentData} />
      </div>
      <ToastContainer />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("react-container")).render(<App />);
