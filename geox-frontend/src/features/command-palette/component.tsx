import { useEffect } from "react";
import { useState } from "react";
import { AiOutlineClose } from "react-icons/ai";
import { Feature } from "../../client";
import { bboxToZoom } from "../geofence-map/utils";
import { getNominatimData } from "./nominatim-api";
import { getOSMData } from "./osm-api";

export const CommandPalette = ({
  onNominatim,
  onOSM,
  onBuffer,
  onPublish,
}: {
  onNominatim: any;
  onOSM: any;
  onBuffer: any;
  onPublish: any;
}) => {
  const [hidden, setHidden] = useState<boolean>(true);
  const [value, setValue] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    try {
      const GOKEN = "go ";
      if (value.startsWith(GOKEN)) {
        const res = await getNominatimData(value.replace(GOKEN, ""));
        const datum = res.data[0];
        const { lat: latitude, lon: longitude } = datum;
        const zoom = bboxToZoom(datum.boundingbox);
        // cleanup
        res.data.length > 0
          ? onNominatim({
              zoom,
              latitude: +latitude,
              longitude: +longitude,
              bearing: 0,
              pitch: 0,
            })
          : setError("No results");
      } else if (value.startsWith("get ")) {
        const res = await getOSMData(value.replace("get ", ""));
        const features = res.data.features as Feature[];
        onOSM(features);
      } else if (value.startsWith("draw ")) {
        onBuffer(500, "meters");
      } else if (value.startsWith("publish")) {
        onPublish();
      } else {
        console.error("Not valid");
        setError("Not valid");
      }
      setValue("");
      setError(null);
      setHidden(true);
      // success
    } catch (e: any) {
      setError(e);
    }
  }

  useEffect(() => {
    async function shortkey(event: KeyboardEvent) {
      if (
        (event.ctrlKey || event.key === "Meta") &&
        event.shiftKey &&
        event.key === "P"
      ) {
        setHidden((oldState) => !oldState);
      }
    }

    document.body.addEventListener("keydown", shortkey, false);

    return () => {
      document.body.removeEventListener("keydown", shortkey, false);
    };
  }, []);

  if (hidden) {
    return null;
  }

  return (
    <div
      className={`fixed p-3 px-4 mr-5 border z-[100] top-[11%] right-[37%] rounded width-screen bg-blue-400 height-[300px] ${
        error ? "border-red-400" : ""
      }`}
    >
      <div className="fixed p-3 px-4 mr-5 border z-[100] top-[11%] right-[37%] rounded width-screen bg-blue-400 height-[300px]">
        <input
          onBlur={() => {
            setHidden(true);
            setError(null);
            setValue("");
          }}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e: any) => (e.key === "Enter" ? handleSubmit() : null)}
          autoFocus
          className="h-15 p-2 w-[400px] rounded"
        ></input>
        <div className="absolute top-0 right-0">
          <div
            className="transition cursor-pointer hover:text-white"
            onClick={() => setHidden(true)}
          >
            <a href="#">
              <AiOutlineClose />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
