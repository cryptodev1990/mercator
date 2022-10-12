import { createContext, useContext, useReducer } from "react";
import { aggressiveLog } from "../../../../common/aggressive-log";
import { SelectionContext } from "../selection/selection.context";
import { geoshapeReducer, initialState } from "./geoshape.reducer";

export interface UndoContextI {
  undo: () => void;
  redo: () => void;
  startSnapshot: () => void;
  endSnapshot: () => void;
}

export const UndoContext = createContext<UndoContextI>({
  undo: () => {},
  redo: () => {},
  startSnapshot: () => {},
  endSnapshot: () => {},
});

UndoContext.displayName = "UndoContext";

export const UndoProvider = ({ children }: { children: any }) => {
  const { selectedFeatureCollection } = useContext(SelectionContext);
  const [state, dispatch] = useReducer(
    aggressiveLog(geoshapeReducer),
    initialState
  );

  function undo() {
    if (state.undoLog.length === 0) {
      return;
    }
    const lastOp = state.undoLog[state.undoLog.length - 1];
    // @ts-ignore
    if (lastOp.op === "ADD_SHAPE") {
      // deleteShapesApi([lastOp.payload.uuid]);
    } else if (lastOp.op === "DELETE_SHAPES") {
      // bulkAddShapes(lastOp.payload);
    } else if (lastOp.op === "UPDATE_SHAPE") {
      // updateShape(lastOp.payload);
    } else if (lastOp.op === "BULK_ADD_SHAPES") {
      // deleteShapes(lastOp.payload.map((shape: Geo) => shape.uuid));
    } else if (lastOp.op === "BULK_ADD_SHAPE_SPLIT") {
      // deleteShapes(lastOp.payload.map((shape) => shape.id));
    }
    dispatch({
      type: "OP_LOG_UNDO",
      op: lastOp.op,
      delta: lastOp.payload,
      currentValue: selectedFeatureCollection,
    });
  }

  function redo() {
    if (state.redoLog.length === 0) {
      return;
    }
    const lastOp = state.redoLog[state.redoLog.length - 1];
    // @ts-ignore
    if (lastOp.op === "ADD_SHAPE") {
      // deleteShapesApi([lastOp.payload.uuid]);
    } else if (lastOp.op === "DELETE_SHAPES") {
      // bulkAddShapes(lastOp.payload);
    } else if (lastOp.op === "UPDATE_SHAPE") {
      // updateShape(lastOp.payload);
    } else if (lastOp.op === "BULK_ADD_SHAPES") {
      // deleteShapes(lastOp.payload.map((shape: Geo) => shape.uuid));
    } else if (lastOp.op === "BULK_ADD_SHAPE_SPLIT") {
      // deleteShapes(lastOp.payload.map((shape) => shape.id));
    }
    dispatch({
      type: "OP_LOG_REDO",
      op: lastOp.op,
      payload: lastOp.payload,
    });
  }

  function startSnapshot() {
    dispatch({
      type: "SNAPSHOT_START",
      currentValue: selectedFeatureCollection,
    });
  }

  function endSnapshot() {
    dispatch({ type: "SNAPSHOT_END", currentValue: selectedFeatureCollection });
  }

  return (
    <UndoContext.Provider
      value={{
        undo,
        redo,
        startSnapshot,
        endSnapshot,
      }}
    >
      {children}
    </UndoContext.Provider>
  );
};
