import axios from "axios";
import { useContext, useState } from "react";
import toast from "react-hot-toast";

import { _GeoJSONLoader as GeoJSONLoader } from "@loaders.gl/json";
import { load } from "@loaders.gl/core";
import { GeofencerContext } from "../../../contexts/geofencer-context";
import { Feature } from "../../../../../client";

function normalizeGeojson(geojson: any): Feature[] | undefined {
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
    throw "Invalid GeoJSON - must be a list of Features or FeatureCollection";
  }
}

export const useConvertedGeojson = () => {
  const [loading, setLoading] = useState(false);
  const { uploadedGeojson: geojson, setUploadedGeojson: setGeojson } =
    useContext(GeofencerContext);

  async function convertJsonFileToGeojson(jsonFile: File) {
    setLoading(true);
    const FeatureCollection = await load(jsonFile, [GeoJSONLoader]);
    try {
      const response: any = normalizeGeojson(FeatureCollection);
      setGeojson(response);
    } catch (error: any) {
      toast.error(error);
    }
    setLoading(false);
  }

  const URL = "https://geox-uploader.fly.dev/upload";

  async function fetchGeoJson(file: File) {
    const form = new FormData();
    let data = [];
    setLoading(true);
    try {
      const response = await axios.post(URL, form, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      data = response.data;
      data = data.data;
      if (response.status !== 200 || data.status !== "success") {
        toast.error(data.error);
      }
      const out: any = normalizeGeojson(data);
      setGeojson(out);
    } catch (error: any) {
      toast.error(error);
    }
    setLoading(false);
  }

  return {
    geojson,
    loading,
    fetchGeoJson,
    convertJsonFileToGeojson,
  };
};
