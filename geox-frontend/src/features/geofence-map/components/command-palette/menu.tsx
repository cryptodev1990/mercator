import { useEffect } from "react";
import { useState } from "react";
import { AiOutlineClose } from "react-icons/ai";
import { Feature } from "../../../../client";
import { bboxToZoom } from "../../utils";
import { getNominatimData } from "./api/nominatim-api";
import { getOSMData } from "./api/osm-api";

export const Menu = ({
  onNominatim,
  onOSM,
  onBuffer,
  onPublish,
  onDelete,
  onIsochrone,
}: {
  onNominatim: any;
  onOSM: any;
  onBuffer: any;
  onPublish: any;
  onDelete: any;
  onIsochrone: any;
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
        // extract the location from the command
        const values = value.match(/get (.*) in (.*)$/);
        if (!values) {
          setError(
            "Command must be in the format 'get <amenity> in <location>'"
          );
          return;
        }
        const res = await getOSMData(values![1], values![2]);
        const features = res as Feature[];
        onOSM(features);
      } else if (value.startsWith("draw ")) {
        if (value.endsWith("buffer")) {
          // extract number and unit from string
          const values = value.match(/^draw (\d+)m buffer$/);
          onBuffer(values![1] ?? 100, "meters");
        } else if (value.endsWith("drive")) {
          // extract number from string
          const values = value.match(/^draw (\d+) (\w+) drive*/);
          onIsochrone(values![1] ?? 10, values![2] ?? "minute");
        }
      } else if (value.startsWith("publish")) {
        onPublish();
      } else if (value.startsWith("delete")) {
        onDelete();
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
            <span className="hover:cursor-pointer">
              <AiOutlineClose />
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
