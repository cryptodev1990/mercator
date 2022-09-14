import { createContext, useEffect } from "react";
import { toast } from "react-hot-toast";
import {
  usePollCopyTaskQuery,
  useTriggerCopyTaskMutation,
} from "../hooks/openapi-hooks";

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
    console.log("task", task);
  }, [task]);

  useEffect(() => {
    console.log("isLoading", isLoading);
  }, [isLoading]);

  useEffect(() => {
    // alert user if there is an error
    if (isError) {
      toast.error("Sync failed with the message: " + error);
    }
    if (isSuccess && isFetched && res?.task_result?.status === "success") {
      toast.success(
        "Sync completed successfully, uploaded " +
          res?.task_result?.numShapes ?? 0 + " shape(s)"
      );
    }
  }, [isError, isSuccess, isFetched]);

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