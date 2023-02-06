import { Dispatch, SetStateAction } from "react";

const SuggestedQueries = ({
  queries,
  handleSqlQuery,
  setDuboQuery,
  setQuery,
}: {
  queries: { query: string; sql: string }[];
  handleSqlQuery: (sql: string) => void;
  setDuboQuery: Dispatch<SetStateAction<string>>;
  setQuery: (prompt: string) => void;
}) => {
  return (
    <div className="flex gap-1 flex-wrap">
      {queries.map(({ query, sql }, index) => (
        <span
          key={index}
          className={`
            px-2 sm:px-4 py-2 rounded sm:rounded-full border border-spBlue
            text-sm w-max cursor-pointer sm:truncate sm:text
            transition duration-300 ease bg-spBlue text-white
          `}
          onClick={() => {
            handleSqlQuery(sql);
            setQuery(query);
            setDuboQuery(query);
          }}
        >
          {query}
        </span>
      ))}
    </div>
  );
};

export default SuggestedQueries;
