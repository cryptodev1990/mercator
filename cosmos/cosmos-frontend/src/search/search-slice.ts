import { createSlice } from "@reduxjs/toolkit";
import { IntentResponse } from "../store/search-api";
import { AppState } from "../store/store";
import { HYDRATE } from "next-redux-wrapper";

// Type for our state
export interface SearchState {
  searchResults: IntentResponse[];
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
  extraReducers: {
    [HYDRATE]: (state, action) => {
      return {
        ...state,
        ...action.payload.search,
      };
    },
  },
  reducers: {
    setSearchResults(state, action: { payload: IntentResponse[] }) {
      state.searchResults = action.payload;
    },
    appendSearchResult(state, action: { payload: IntentResponse }) {
      state.searchResults = state.searchResults.concat(action.payload);
      state.inputText = "";
    },
    deleteOneSearchResult(state, action: { payload: string }) {
      state.searchResults = state.searchResults.filter(
        (result) => result.query !== action.payload
      );
    },
    clearSearchResults(state) {
      state.searchResults = [];
    },
    setInputText(state, actions: { payload: string }) {
      state.inputText = actions.payload;
    },
    clearInputText(state) {
      state.inputText = null;
    },
    reset(state) {
      state.searchResults = [];
      state.inputText = null;
    },
  },
});

export const {
  setSearchResults,
  appendSearchResult,
  deleteOneSearchResult,
  setInputText,
  clearInputText,
  clearSearchResults,
} = searchSlice.actions;

export const selectSearchState = (state: AppState) => state.search;

export default searchSlice.reducer;
