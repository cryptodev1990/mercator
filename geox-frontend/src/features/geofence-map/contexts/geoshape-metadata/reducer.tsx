import { Namespace } from "../../../../client";
import { Action } from "./action-types";

export interface State {
  activeNamespaceIDs: string[];
  visibleNamespaceIDs: string[];
}

export const initialState: State = {
  activeNamespaceIDs: [],
  visibleNamespaceIDs: [],
};

export function geoshapeReducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_ACTIVE_NAMESPACES": {
      return {
        ...state,
        activeNamespaceIDs: action.namespaces,
      };
    }
    case "SET_VISIBLE_NAMESPACES": {
      return {
        ...state,
        visibleNamespaceIDs: action.namespaces,
      };
    }
    default:
      return state;
  }
}
