import { useContext } from "react";
import { DbSyncContext } from "../contexts/db-sync-context";

export const useDbSync = () => {
  const { triggerCopyTask, isLoading, isError, isSuccess } =
    useContext(DbSyncContext);
  return {
    triggerCopyTask,
    isLoading,
    isError,
    isSuccess,
  };
};
