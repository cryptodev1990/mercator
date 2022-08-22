// This is really just a scratchpad for testing stuff
// that I don't yet know how to get working.

import { HealthService } from "../../client";

import { useQuery } from "react-query";

const AuthComponent = () => {
  const { isLoading, isError, data, error } = useQuery(
    ["health"],
    () => {
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
    </div>
  );
};

export default AdminPage;
