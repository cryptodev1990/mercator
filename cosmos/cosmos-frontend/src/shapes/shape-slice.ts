import { createSlice } from "@reduxjs/toolkit";
import { AppState } from "../store/store";
import { HYDRATE } from "next-redux-wrapper";

export type Viewport = {
  latitude: number;
  longitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
};

export type LayerStyle = {
  id: string;
  type: string;
  lineThicknessPx: number;
  opacity: number;
  paint: number[];
};

// Type for our state
export interface GeoMapState {
  viewport: Viewport;
  layerStyles: LayerStyle[];
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
    addLayerStyle(state, action: { payload: LayerStyle }) {
      state.layerStyles = state.layerStyles.concat(action.payload);
    },
    removeLayerStyle(state, action: { payload: string }) {
      state.layerStyles = state.layerStyles.filter(
        (style) => style.id !== action.payload
      );
    },
    updateStyle(
      state,
      action: {
        payload: {
          id: string;
          lineThicknessPx?: number;
          paint?: number[];
          opacity?: number;
        };
      }
    ) {
      state.layerStyles = state.layerStyles.map((style) =>
        style.id === action.payload.id ? { ...style, ...action.payload } : style
      );
    },
  },
});

export const { setViewport, addLayerStyle, removeLayerStyle, updateStyle } =
  geoMapSlice.actions;

export const selectGeoMapState = (state: AppState) => state.geoMap;

export default geoMapSlice.reducer;
