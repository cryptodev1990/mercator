import { createSlice } from "@reduxjs/toolkit";
import { AppState } from "../store/store";
import { HYDRATE } from "next-redux-wrapper";

type Viewport = {
  latitude: number;
  longitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
};

// Type for our state
export interface GeoMapState {
  viewport: Viewport;
  layerStyles: any[];
}

// Initial state
const initialState: GeoMapState = {
  viewport: {
    latitude: 51.505,
    longitude: -0.09,
    zoom: 13,
  },
  layerStyles: [],
};

// Actual Slice
export const geoMapSlice = createSlice({
  name: "geoMap",
  initialState,
  extraReducers: {
    [HYDRATE]: (state, action) => {
      return {
        ...state,
        ...action.payload.geoMap,
      };
    },
  },
  reducers: {
    setViewport(state, action: { payload: Viewport }) {
      state.viewport = action.payload;
    },
  },
});

export const { setViewport } = geoMapSlice.actions;

export const selectGeoMapState = (state: AppState) => state.geoMap;

export default geoMapSlice.reducer;
