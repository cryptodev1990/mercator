import axios from "axios";
import { useContext, useState } from "react";

import { _GeoJSONLoader as GeoJSONLoader } from "@loaders.gl/json";
import { load } from "@loaders.gl/core";
import { GeofencerContext } from "../context";

export const useConvertedGeojson = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { uploadedGeojson: geojson, setUploadedGeojson: setGeojson } =
    useContext(GeofencerContext);

  function convertJsonFileToGeojson(jsonFile: File) {
    const reader = new FileReader();
    reader.readAsText(new Blob([jsonFile]));
    reader.onload = (e: any) => {
      load(jsonFile, [GeoJSONLoader]).then((geojsonRes: any) => {
        if (geojsonRes && geojsonRes.type === "FeatureCollection") {
          setGeojson(geojsonRes.features);
        } else if (geojsonRes && geojsonRes.type === "Feature") {
          setGeojson([geojsonRes]);
        } else if (
          geojsonRes &&
          Array.isArray(geojsonRes) &&
          geojsonRes.length > 0 &&
          geojsonRes[0].type === "Feature"
        ) {
          setGeojson(geojsonRes);
        } else {
          setError(
            "Invalid GeoJSON - must be a list of Features or FeatureCollection"
          );
        }
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
      console.log(data);
      if (response.status !== 200 || data.status !== "success") {
        setError(data.error);
      }
      setGeojson(data);
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
