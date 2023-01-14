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
import { DataFrame } from "./dubo-preview";
// @ts-ignore
import qs from "qs";

const BASE_URL = "https://dubo-api.mercator.tech/v1/dubo/query";

const duboClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    ["Content-Type"]: "application/json",
  },
});

const duboQuery = async (query: string, schemas: string[]) => {
  const response = await duboClient.get(BASE_URL, {
    params: {
      user_query: query,
      schemas,
    },
    paramsSerializer: {
      serialize: (params: ParamsSerializerOptions) => {
        return qs.stringify(params, { arrayFormat: "repeat" });
      },
    },
  });
  return response.data;
};

export function sniff(df: DataFrame) {
  const columns = df.columns;
  const counter: any = {};
  // count the number of any type in first 100 rows
  let i = 0;
  for (const row of df.data) {
    for (const col of columns) {
      const type = typeof row[col];
      if (counter[col]) {
        if (counter[col][type]) {
          counter[col][type] += 1;
        } else {
          counter[col][type] = 1;
        }
      } else {
        counter[col] = {};
        counter[col][type] = 1;
      }
    }
    if (i > 100) {
      break;
    }
    i += 1;
  }

  const types = [];
  for (const col of columns) {
    // set seach column to the most common type
    // if the column name is zip, zip_code, zcta, then the type is string
    if (["zip", "zip_code", "zcta"].includes(col.toLowerCase())) {
      types.push("TEXT");
      continue;
    }
    const type = Object.keys(counter[col]).reduce((a, b) =>
      counter[col][a] > counter[col][b] ? a : b
    );

    types.push(jsTypeToSqliteType(type));
  }

  return types;
}

function jsTypeToSqliteType(type: string) {
  switch (type) {
    case "string":
      return "TEXT";
    case "number":
      return "REAL";
    case "boolean":
      return "INTEGER";
    default:
      return "TEXT";
  }
}

export const convertZip = (potentialZip: number) => {
  return potentialZip.toString().padStart(5, "0");
};

export default duboQuery;
