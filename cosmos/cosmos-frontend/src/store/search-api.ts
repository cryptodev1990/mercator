import { emptySplitApi as api } from "./empty-api";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    osmQueryGet: build.query<OsmQueryGetApiResponse, OsmQueryGetApiArg>({
      query: (queryArg) => ({
        url: `/osm/query`,
        params: { query: queryArg.query },
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
    osmShapeForIdGet: build.query<
      OsmShapeForIdGetApiResponse,
      OsmShapeForIdGetApiArg
    >({
      query: (queryArg) => ({
        url: `/osm/shape_for_id`,
        params: { osm_id: queryArg.osmId },
      }),
    }),
    autocompleteSearchGet: build.query<
      AutocompleteSearchGetApiResponse,
      AutocompleteSearchGetApiArg
    >({
      query: (queryArg) => ({
        url: `/autocomplete/search`,
        params: { text: queryArg.text, limit: queryArg.limit },
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
  /** status 200 Successful Response */ SearchResponse;
export type OsmQueryGetApiArg = {
  /** Query text string. */
  query: string;
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
export type OsmShapeForIdGetApiResponse =
  /** status 200 Successful Response */ OsmShapeForIdResponse;
export type OsmShapeForIdGetApiArg = {
  /** OSM id. */
  osmId: number;
};
export type AutocompleteSearchGetApiResponse =
  /** status 200 Successful Response */ string[];
export type AutocompleteSearchGetApiArg = {
  /** Incomplete text. */
  text: string;
  /** Maximum number of results to return */
  limit?: number;
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
export type ParsedEntity = {
  lookup: string;
  match_type: string;
  geoids: string[];
};
export type ExecutorResponse = {
  geom: FeatureCollection;
  entities: ParsedEntity[];
};
export type SearchResponse = {
  id: string;
  parse_result: ExecutorResponse;
  query: string;
  intents: string[];
  slots: {
    [key: string]: string;
  };
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
export type OsmShapeForIdResponse = {
  osm_id: number;
  result: Feature;
};
export const {
  useOsmQueryGetQuery,
  useOsmRawQueryGetQuery,
  useOsmSqlGetQuery,
  useOsmShapeForIdGetQuery,
  useAutocompleteSearchGetQuery,
  useGetQuery,
  useHealthGetQuery,
  useHealthDbGetQuery,
} = injectedRtkApi;
