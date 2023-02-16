// TODO - this is a placeholder for the queryable page
import useSWR from "swr";

import DuboPreview from "../../components/dubo-preview";

// @ts-ignore
const fetcher = (...args: any) => fetch(...args).then((res) => res.json());

const Queryable = ({
  slug,
  executions,
}: {
  slug: string[];
  executions: string[];
}) => {
  const { data, error } = useSWR(
    slug ? `/api/queryable/${slug.join("/")}` : null,
    fetcher
  );

  if (error) return <div>failed to load</div>;
  if (!data) return <div>loading...</div>;
  return <div></div>;
};

export default Queryable;
