// This is really just a scratchpad for testing stuff
// that I don't yet know how to get working.

import {
  CeleryAddTaskResult,
  CeleryTaskRunResponse,
  HealthService,
  OpenAPI,
  TasksService,
} from "../../client";

import { useQuery } from "react-query";
import { useEffect, useState } from "react";

const AddTaskComponent = ({ taskId }: { taskId: string }) => {
  const { isLoading, isError, data, error } = useQuery<CeleryAddTaskResult>(
    ["celery"],
    () => {
      return TasksService.getStatusTasksTaskIdGet(taskId);
    },
    {
      refetchInterval: 1000,
    }
  );
  if (isLoading) {
    return <div>Loading...</div>;
  }
  return <div>Data is {JSON.stringify(data)}</div>;
};

const AuthComponent = () => {
  const { isLoading, isError, data, error } = useQuery(
    ["health"],
    () => {
      console.log("got here");
      return HealthService.protectedHealthProtectedHealthGet();
    },
    {}
  );
  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (isError) {
    return <div>Error: {JSON.stringify(error)} </div>;
  }
  return <div>{JSON.stringify(data)}</div>;
};

// TODO get this working
const AdminPage = () => {
  // const { isLoading, isError, data, error } = useQuery<CeleryTaskRunResponse>(
  //   ["celery"],
  //   () => {
  //     return TasksService.runAddTaskTasksAddPost(1, 3);
  //   }
  // );

  // if (isLoading) {
  //   return <div>We have posted {data}</div>;
  // }

  // if (!data?.task_id) {
  //   return <div>No task id</div>;
  // }

  return (
    <div className="text-white">
      <p>React Query Take the Wheel:</p>
      <AuthComponent />
      {/* <AddTaskComponent taskId={data?.task_id} /> */}
    </div>
  );
};

export default AdminPage;
