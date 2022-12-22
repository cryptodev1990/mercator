import { Dispatch } from "react";
import { appendSearchResult } from "src/search/search-slice";
import { addLayerStyle } from "src/shapes/shape-slice";
import { SearchResponse } from "src/store/search-api";
import { TAILWIND_COLORS } from "./colors";

export function generateLayerId() {
  return Math.random().toString(36).substr(2, 9);
}

let i = 0;

export function addNewLayer(data: SearchResponse, dispatch: Dispatch<any>) {
  // get number of layers already in the store
  dispatch(appendSearchResult(data));
  dispatch(
    addLayerStyle({
      id: data.query,
      lineThicknessPx: 1,
      paint: TAILWIND_COLORS[i % TAILWIND_COLORS.length].rgb,
      opacity: 1,
      type: data.query ?? "unknown",
    })
  );
  i += 1;
}
