import { Dispatch } from "react";
import { appendSearchResult, setInputText } from "src/search/search-slice";
import { addLayerStyle } from "src/shapes/shape-slice";
import { IntentResponse } from "src/store/search-api";
import { TAILWIND_COLORS } from "../colors";

let i = 0;

export function addNewLayer(data: IntentResponse, dispatch: Dispatch<any>) {
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

export function runNewSearch(searchQuery: string, dispatch: Dispatch<any>) {
  dispatch(setInputText(searchQuery));
}
