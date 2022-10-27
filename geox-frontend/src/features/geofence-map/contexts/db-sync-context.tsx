import { createContext, useEffect } from "react";
import { toast } from "react-hot-toast";
import simplur from "simplur";
import {
  usePollCopyTaskQuery,
  useTriggerCopyTaskMutation,
} from "../hooks/use-openapi-hooks";

export const DbSyncContext = createContext({
  triggerCopyTask: () => {},
  isLoading: false,
  isError: false,
  isSuccess: false,
});
DbSyncContext.displayName = "DbSyncContext";

export const DbSyncContextContainer = ({ children }: { children: any }) => {
  const { mutate: triggerCopyTask, data: task } = useTriggerCopyTaskMutation();
  const {
    isLoading,
    isError,
    isSuccess,
    isFetched,
    error,
    data: res,
  } = usePollCopyTaskQuery(task?.task_id);

  useEffect(() => {
    // alert user if there is an error
    if (isError) {
      toast.error("Sync failed with the message: " + error);
    }
    if (isSuccess && isFetched && res?.task_result?.status === "success") {
      toast.success(
        "Sync completed successfully, uploaded " +
          simplur`{res?.task_result?.numShapes ?? 0} shape[|s]`
      );
    }
  }, [isError, isSuccess, isFetched, error, res?.task_result?.status]);

  return (
    <DbSyncContext.Provider
      value={{
        triggerCopyTask,
        isLoading,
        isError,
        isSuccess,
      }}
    >
      {children}
    </DbSyncContext.Provider>
  );
};
