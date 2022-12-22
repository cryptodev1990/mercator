import {
  configureStore,
  ThunkAction,
  Action,
  createListenerMiddleware,
} from "@reduxjs/toolkit";
import { searchSlice } from "../search/search-slice";
import { createWrapper } from "next-redux-wrapper";
import { searchApi } from "./search-api";
import { setupListeners } from "@reduxjs/toolkit/dist/query";
import { geoMapSlice } from "src/shapes/shape-slice";
import { snapToBounds } from "src/lib/geo-utils";

const listenerMiddleware = createListenerMiddleware();

// looks for new results in the search slice and updates the viewport in the geoMapSlice
listenerMiddleware.startListening({
  actionCreator: searchSlice.actions.appendSearchResult,
  effect: async (action, listenerApi) => {
    const { dispatch } = listenerApi;
    const { payload } = action;
    const bounds = snapToBounds(payload.parse_result.geom);
    const viewport = {
      ...bounds,
    };
    // if any of the viewport values are undefined, don't update the viewport
    if (Object.values(viewport).some((v) => v === undefined)) {
      console.warn("Viewport values are undefined");
      return;
    } else {
      // @ts-ignore
      dispatch(geoMapSlice.actions.setViewport(viewport));
    }
  },
});

export const makeStore = () => {
  const store = configureStore({
    reducer: {
      [searchSlice.name]: searchSlice.reducer,
      [geoMapSlice.name]: geoMapSlice.reducer,
      [searchApi.reducerPath]: searchApi.reducer,
    },
    devTools: true,
    middleware: (getdefaultmiddleware) =>
      getdefaultmiddleware()
        .prepend(listenerMiddleware.middleware)
        .concat(searchApi.middleware),
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
