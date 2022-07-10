import {
  CeleryAddTaskResult,
  CeleryTaskRunResponse,
  TasksService,
} from "../../client";

import { useQuery } from "react-query";

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

// TODO get this working
const AdminPage = () => {
  const { isLoading, isError, data, error } = useQuery<CeleryTaskRunResponse>(
    ["celery"],
    () => {
      return TasksService.runAddTaskTasksAddPost(1, 3);
    }
  );

  if (isLoading) {
    return <div>We have posted {data}</div>;
  }

  if (!data?.task_id) {
    return <div>No task id</div>;
  }

  return (
    <div>
      <p>React Query Take the Wheel:</p>
      <AddTaskComponent taskId={data?.task_id} />
    </div>
  );
};

export default AdminPage;
