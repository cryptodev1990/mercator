import { Namespace } from "../../../../client";
import { Action } from "./action-types";

export interface State {
  activeNamespaces: Namespace[];
  visibleNamespaces: Namespace[];
}

export const initialState: State = {
  activeNamespaces: [],
  visibleNamespaces: [],
};

export function geoshapeReducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_ACTIVE_NAMESPACES": {
      return {
        ...state,
        activeNamespaces: action.namespaces,
      };
    }
    case "SET_VISIBLE_NAMESPACES": {
      return {
        ...state,
        visibleNamespaces: action.namespaces,
      };
    }
    default:
      return state;
  }
}
