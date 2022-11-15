import axios from "axios";
import { useContext, useState } from "react";

import { _GeoJSONLoader as GeoJSONLoader } from "@loaders.gl/json";
import { load } from "@loaders.gl/core";
import { GeofencerContext } from "../../../contexts/geofencer-context";
import { Feature } from "../../../../../client";

function normalizeGeojson(
  geojson: any,
  handleError: any
): Feature[] | undefined {
  let out: Feature[];
  if (geojson && geojson.type === "FeatureCollection") {
    out = geojson.features;
    return out;
  } else if (geojson && geojson.type === "Feature") {
    out = [geojson];
    return out;
  } else if (
    geojson &&
    Array.isArray(geojson) &&
    geojson.length > 0 &&
    geojson[0].type === "Feature"
  ) {
    out = geojson;
    return out;
  } else {
    handleError(
      "Invalid GeoJSON - must be a list of Features or FeatureCollection"
    );
  }
}

export const useConvertedGeojson = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialUploadSize, setInitialUploadSize] = useState(0);
  const { uploadedGeojson: geojson, setUploadedGeojson: setGeojson } =
    useContext(GeofencerContext);

  function convertJsonFileToGeojson(jsonFile: File, transform?: any) {
    const reader = new FileReader();
    const blob = new Blob([jsonFile]);
    reader.readAsText(blob);
    const bytes = blob.size;
    reader.onload = () => {
      load(jsonFile, [GeoJSONLoader]).then((geojsonRes: any) => {
        const out = normalizeGeojson(geojsonRes, () => {});
        if (!out) {
          setError(
            "Invalid GeoJSON - must be a list of Features or FeatureCollection"
          );
          return;
        }
        setGeojson(out);
        setInitialUploadSize(bytes);
      });
    };
  }

  const URL = "https://geox-uploader.fly.dev/upload";

  async function fetchGeoJson(file: File) {
    const form = new FormData();
    form.append("data", file);
    let data = [];

    try {
      setLoading(true);

      const response = await axios.post(URL, form, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      data = response.data;
      data = data.data;
      if (response.status !== 200 || data.status !== "success") {
        setError(data.error);
      }
      const out = normalizeGeojson(data, () => {});
      if (!out) {
        setError("Invalid file - upload failed");
        return;
      }
      setGeojson(out);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return {
    error,
    geojson,
    loading,
    fetchGeoJson,
    initialUploadSize,
    convertJsonFileToGeojson,
  };
};
