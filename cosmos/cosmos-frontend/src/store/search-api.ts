import { emptySplitApi as api } from "./empty-api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    osmQueryGet: build.query<OsmQueryGetApiResponse, OsmQueryGetApiArg>({
      query: (queryArg) => ({
        url: `/osm/query`,
        params: {
          query: queryArg.query,
          bbox: queryArg.bbox,
          limit: queryArg.limit,
        },
      }),
    }),
    osmRawQueryGet: build.query<
      OsmRawQueryGetApiResponse,
      OsmRawQueryGetApiArg
    >({
      query: (queryArg) => ({
        url: `/osm/raw-query`,
        params: { query: queryArg.query },
      }),
    }),
    osmSqlGet: build.query<OsmSqlGetApiResponse, OsmSqlGetApiArg>({
      query: (queryArg) => ({
        url: `/osm/sql`,
        params: { query: queryArg.query },
      }),
    }),
    get: build.query<GetApiResponse, GetApiArg>({
      query: () => ({ url: `/` }),
    }),
    healthGet: build.query<HealthGetApiResponse, HealthGetApiArg>({
      query: () => ({ url: `/health` }),
    }),
    healthDbGet: build.query<HealthDbGetApiResponse, HealthDbGetApiArg>({
      query: () => ({ url: `/health/db` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as searchApi };
export type OsmQueryGetApiResponse =
  /** status 200 Successful Response */ OsmSearchResponse;
export type OsmQueryGetApiArg = {
  /** Query text string. */
  query: string;
  /** Bounding box to restrict the search: min_lon, min_lat, max_lon, max_lat */
  bbox?: any[];
  /** Maximum number of results to return */
  limit?: number;
};
export type OsmRawQueryGetApiResponse =
  /** status 200 Successful Response */ OsmRawQueryResponse;
export type OsmRawQueryGetApiArg = {
  /** Query text string */
  query: string;
};
export type OsmSqlGetApiResponse =
  /** status 200 Successful Response */ OsmRawQueryResponse;
export type OsmSqlGetApiArg = {
  /** Query text string */
  query: string;
};
export type GetApiResponse = /** status 200 Successful Response */ any;
export type GetApiArg = void;
export type HealthGetApiResponse = /** status 200 Successful Response */ any;
export type HealthGetApiArg = void;
export type HealthDbGetApiResponse = /** status 200 Successful Response */ any;
export type HealthDbGetApiArg = void;
export type Point = {
  type?: "Point";
  coordinates: any[];
};
export type MultiPoint = {
  type?: "MultiPoint";
  coordinates: any[][];
};
export type LineString = {
  type?: "LineString";
  coordinates: any[][];
};
export type MultiLineString = {
  type?: "MultiLineString";
  coordinates: any[][][];
};
export type Polygon = {
  type?: "Polygon";
  coordinates: any[][][];
};
export type MultiPolygon = {
  type?: "MultiPolygon";
  coordinates: any[][][][];
};
export type Feature = {
  type?: "Feature";
  id?: string | number;
  properties?: object;
  geometry:
    | ({
        type: "Point";
      } & Point)
    | ({
        type: "MultiPoint";
      } & MultiPoint)
    | ({
        type: "LineString";
      } & LineString)
    | ({
        type: "MultiLineString";
      } & MultiLineString)
    | ({
        type: "Polygon";
      } & Polygon)
    | ({
        type: "MultiPolygon";
      } & MultiPolygon);
  bbox?: any[];
};
export type FeatureCollection = {
  type?: "FeatureCollection";
  features?: Feature[];
  bbox?: any[];
};
export type OsmSearchResponse = {
  query: string;
  label?: string;
  parse?: object;
  results: FeatureCollection;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type OsmRawQueryResponse = {
  query: string;
  results: object[];
};
export const {
  useOsmQueryGetQuery,
  useOsmRawQueryGetQuery,
  useOsmSqlGetQuery,
  useGetQuery,
  useHealthGetQuery,
  useHealthDbGetQuery,
} = injectedRtkApi;
