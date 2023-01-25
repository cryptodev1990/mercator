// Construct a client that can be used to make requests to the Dubo API

/*
user_query
string
The question to answer

user_query
schemas
array[string]
The table schema(s) to use

Add string item
descriptions
array[string]
(query)
The table description(s) to use
*/

import axios, { ParamsSerializerOptions } from "axios";
import qs from "qs";

const BASE_URL = "https://dubo-api.mercator.tech/v1/dubo/query";

const duboClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    ["Content-Type"]: "application/json",
  },
});

const duboQuery = async (
  query: string,
  schemas?: string[],
  databaseSchema?: DatabaseSchema
) => {
  try {
    const response = await duboClient.get(
      databaseSchema ? `${BASE_URL}/${databaseSchema}` : BASE_URL,
      {
        params: {
          user_query: query,
          schemas,
        },
        paramsSerializer: {
          serialize: (params: ParamsSerializerOptions) => {
            return qs.stringify(params, { arrayFormat: "repeat" });
          },
        },
      }
    );

    return response.data;
  } catch (err) {
    console.log(err);
  }
};

export default duboQuery;
