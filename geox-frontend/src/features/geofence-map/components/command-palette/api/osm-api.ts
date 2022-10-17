import axios from "axios";

export const getOSMData = async (
  query: string,
  geographicReference: string
) => {
  const res = await axios.get(process.env.REACT_APP_BACKEND_URL + "/osm", {
    params: {
      query,
      geographic_reference: geographicReference,
    },
  });
  return res.data;
};
