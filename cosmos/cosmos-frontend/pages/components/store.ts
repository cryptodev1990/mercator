import { configureStore, ThunkAction, Action } from "@reduxjs/toolkit";
import { searchSlice } from "./state/search-slice";
import { createWrapper } from "next-redux-wrapper";
import { searchApi } from "../../src/store/search-api";

export const makeStore = () =>
  configureStore({
    reducer: {
      [searchSlice.name]: searchSlice.reducer,
      [searchApi.reducerPath]: searchApi.reducer,
    },
    devTools: true,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(searchApi.middleware),
  });

export type AppStore = ReturnType<typeof makeStore>;
export type AppState = ReturnType<AppStore["getState"]>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  AppState,
  unknown,
  Action
>;

export const wrapper = createWrapper<AppStore>(makeStore);

export const store = makeStore();
