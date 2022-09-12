import axios from "axios";
import { useContext, useEffect, useState } from "react";

import { _GeoJSONLoader as GeoJSONLoader } from "@loaders.gl/json";
import { load } from "@loaders.gl/core";
import { GeofencerContext } from "../context";
import { simplify } from "@turf/turf";
import { toast } from "react-hot-toast";
import { Feature } from "../../../client";

export const useConvertedGeojson = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialUploadSize, setInitialUploadSize] = useState(0);
  const { uploadedGeojson: geojson, setUploadedGeojson: setGeojson } =
    useContext(GeofencerContext);

  useEffect(() => {
    if (initialUploadSize > 20000000) {
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
    reader.onload = (e: any) => {
      let out: Feature[] = [];
      load(jsonFile, [GeoJSONLoader]).then((geojsonRes: any) => {
        if (geojsonRes && geojsonRes.type === "FeatureCollection") {
          out = geojsonRes.features;
        } else if (geojsonRes && geojsonRes.type === "Feature") {
          out = [geojsonRes];
        } else if (
          geojsonRes &&
          Array.isArray(geojsonRes) &&
          geojsonRes.length > 0 &&
          geojsonRes[0].type === "Feature"
        ) {
          out = geojsonRes;
        } else {
          setError(
            "Invalid GeoJSON - must be a list of Features or FeatureCollection"
          );
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
