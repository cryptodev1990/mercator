const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

type TextNode = {
  text: string;
  start: number;
  end: number;
};

export type FeatureCollection = {
  type: string;
  features: Feature[];
  bbox?: number[];
};

type Feature = {
  type: string;
  geometry: Geometry;
  properties: Properties;
};

type Geometry = {
  type: string;
  coordinates: number[];
};

type Properties = {
  [key: string]: any;
};

export type SearchResponse = {
  query: string;
  parse: {
    intent: string;
    args: {
      subject: TextNode;
      predicate: TextNode;
      object: TextNode;
    };
  };
  results: FeatureCollection;
};

export async function search(
  query: string,
  bbox: number[]
): Promise<SearchResponse | undefined> {
  const params = new URLSearchParams();
  params.append("query", query);
  params.append("bbox", "" + bbox[0]);
  params.append("bbox", "" + bbox[1]);
  params.append("bbox", "" + bbox[2]);
  params.append("bbox", "" + bbox[3]);
  const preparedUrl = `${BACKEND_URL}/osm/search/v0/?` + params.toString();
  const res = await fetch(preparedUrl, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  try {
    const data = await res.json();
    return data;
  } catch (e) {
    console.error(e);
  }
}
