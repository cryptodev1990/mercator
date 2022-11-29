import { createSlice } from "@reduxjs/toolkit";
import { OsmSearchResponse } from "../store/search-api";
import { AppState } from "../store/store";

// Type for our state
export interface SearchState {
  searchResults: OsmSearchResponse[];
  inputText: string | null;
}

// Initial state
const initialState: SearchState = {
  searchResults: [],
  inputText: null,
};

// Actual Slice
export const searchSlice = createSlice({
  name: "search",
  initialState,
  reducers: {
    setSearchResults(state, action: { payload: OsmSearchResponse[] }) {
      state.searchResults = action.payload;
    },
    appendSearchResult(state, action: { payload: OsmSearchResponse }) {
      state.searchResults = state.searchResults.concat(action.payload);
    },
    deleteOneSearchResult(state, action: { payload: string }) {
      state.searchResults = state.searchResults.filter(
        (result) => result.query !== action.payload
      );
    },
    setInputText(state, actions: { payload: string }) {
      state.inputText = actions.payload;
    },
  },
});

export const {
  setSearchResults,
  appendSearchResult,
  deleteOneSearchResult,
  setInputText,
} = searchSlice.actions;

export const selectSearchState = (state: AppState) => state.search;

export default searchSlice.reducer;
