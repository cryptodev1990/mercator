import axios from "axios";
import { useContext, useEffect, useState } from "react";

import { _GeoJSONLoader as GeoJSONLoader } from "@loaders.gl/json";
import { load } from "@loaders.gl/core";
import { GeofencerContext } from "../../../contexts/geofencer-context";
import { simplify } from "@turf/turf";
import { toast } from "react-hot-toast";
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

const MB_20 = 20 * 1024 * 1024;

export const useConvertedGeojson = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialUploadSize, setInitialUploadSize] = useState(0);
  const { uploadedGeojson: geojson, setUploadedGeojson: setGeojson } =
    useContext(GeofencerContext);

  useEffect(() => {
    if (initialUploadSize > MB_20) {
      toast("File is too large and will be simplified.");
      const res = [];
      for (let i = 0; i < geojson.length; i++) {
        const simplified = simplify(geojson[i] as any, {
          tolerance: 0.001,
          highQuality: true,
        });
        res[i] = simplified;
      }
      setGeojson(res);
      setInitialUploadSize(0);
    }
  }, [initialUploadSize]);

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
        if (transform && transform.nameKey) {
          for (let i = 0; i < out.length; i++) {
            if (out[i].properties) {
              out[i].properties.name = out[i].properties[transform.nameKey];
            }
          }
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
    convertJsonFileToGeojson,
  };
};
