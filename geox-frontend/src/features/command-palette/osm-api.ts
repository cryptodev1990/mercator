import axios from "axios";

export const getOSMData = async (query: string) => {
  return axios.get(process.env.REACT_APP_BACKEND_URL + "/osm/demo");
};
