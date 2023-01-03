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
    osmSearchGet: build.query<OsmSearchGetApiResponse, OsmSearchGetApiArg>({
      query: (queryArg) => ({
        url: `/osm/search`,
        params: { term: queryArg.term, method: queryArg.method },
      }),
    }),
    osmExecutePost: build.mutation<
      OsmExecutePostApiResponse,
      OsmExecutePostApiArg
    >({
      query: (queryArg) => ({
        url: `/osm/execute`,
        method: "POST",
        body: queryArg.intentPayload,
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
  /** status 200 Successful Response */ IntentResponse;
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
export type OsmSearchGetApiResponse =
  /** status 200 Successful Response */ ParsedEntity[];
export type OsmSearchGetApiArg = {
  /** Search term. */
  term: string;
  /** Search method, which can be one of 'fuzzy', 'category', or 'named_place'. */
  method: string;
};
export type OsmExecutePostApiResponse =
  /** status 200 Successful Response */ IntentResponse;
export type OsmExecutePostApiArg = {
  intentPayload: IntentPayload;
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
  matched_text?: string;
  match_type: string;
  geoids?: string[];
  m?: number;
};
export type ExecutorResponse = {
  geom: FeatureCollection;
  entities: ParsedEntity[];
};
export type ValidIntentNameEnum =
  | "x_in_y"
  | "area_near_constraint"
  | "raw_lookup"
  | "x_between_y_and_z";
export type XInYIntentArgs = {
  needle_place_or_amenity: ParsedEntity | string;
  haystack_place_or_amenity: ParsedEntity | string;
};
export type Distance = {
  m: number;
};
export type AreaNearConstraintIntentArgs = {
  named_place_or_amenity_0: ParsedEntity | string;
  distance_or_time_0: Distance | string;
  named_place_or_amenity_1: ParsedEntity | string;
  distance_or_time_1: Distance | string;
  named_place_or_amenity_2?: ParsedEntity | string;
  distance_or_time_2?: Distance | string;
  named_place_or_amenity_3?: ParsedEntity | string;
  distance_or_time_3?: Distance | string;
  named_place_or_amenity_4?: ParsedEntity | string;
  distance_or_time_4?: Distance | string;
  named_place_or_amenity_5?: ParsedEntity | string;
  distance_or_time_5?: Distance | string;
  named_place_or_amenity_6?: ParsedEntity | string;
  distance_or_time_6?: Distance | string;
  named_place_or_amenity_7?: ParsedEntity | string;
  distance_or_time_7?: Distance | string;
};
export type RawLookupIntentArgs = {
  search_term: string | ParsedEntity;
};
export type NamedPlaceParsedEntity = {
  lookup: string;
  matched_text?: string;
  match_type?: string;
  geoids?: string[];
  m?: number;
};
export type XBetweenYAndZIntentArgs = {
  named_place_or_amenity_0: ParsedEntity | string;
  named_place_or_amenity_1: NamedPlaceParsedEntity | string;
  named_place_or_amenity_2: NamedPlaceParsedEntity | string;
};
export type IntentResponse = {
  id: string;
  parse_result: ExecutorResponse;
  query: string;
  intents: ValidIntentNameEnum[];
  slots:
    | XInYIntentArgs
    | AreaNearConstraintIntentArgs
    | RawLookupIntentArgs
    | XBetweenYAndZIntentArgs;
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
export type IntentPayload = {
  name: ValidIntentNameEnum;
  args:
    | XInYIntentArgs
    | AreaNearConstraintIntentArgs
    | RawLookupIntentArgs
    | XBetweenYAndZIntentArgs;
};
export const {
  useOsmQueryGetQuery,
  useOsmRawQueryGetQuery,
  useOsmSqlGetQuery,
  useOsmSearchGetQuery,
  useOsmExecutePostMutation,
  useGetQuery,
  useHealthGetQuery,
  useHealthDbGetQuery,
} = injectedRtkApi;
