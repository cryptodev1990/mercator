import { configureStore, ThunkAction, Action } from "@reduxjs/toolkit";
import { searchSlice } from "../search/search-slice";
import { createWrapper } from "next-redux-wrapper";
import { searchApi } from "./search-api";
import { setupListeners } from "@reduxjs/toolkit/dist/query";
import { geoMapSlice } from "src/shapes/shape-slice";

export const makeStore = () => {
  const store = configureStore({
    reducer: {
      [searchSlice.name]: searchSlice.reducer,
      [geoMapSlice.name]: geoMapSlice.reducer,
      [searchApi.reducerPath]: searchApi.reducer,
    },
    devTools: true,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(searchApi.middleware),
  });
  setupListeners(store.dispatch);
  return store;
};

export type AppStore = ReturnType<typeof makeStore>;
export type AppState = ReturnType<AppStore["getState"]>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  AppState,
  unknown,
  Action
>;

export const wrapper = createWrapper<AppStore>(makeStore);
