import { Dispatch, SetStateAction } from "react";

import { CloseButton } from "../close-button";
import SQL from "../sql";

const SQLBar = ({
  generatedSql,
  setShowSQLQuery,
  theme,
}: {
  generatedSql: string;
  setShowSQLQuery: Dispatch<SetStateAction<boolean>>;
  theme: string;
}) => {
  return (
    <div className="mt-6 relative w-full animate-fadeIn100">
      <div className="absolute top-2 right-2">
        <CloseButton onClick={() => setShowSQLQuery(false)} />
      </div>

      <div
        onClick={(e) => e.stopPropagation()}
        className="font-mono cursor-auto"
        key={theme}
      >
        <SQL query={generatedSql} light={theme === "light"} className="!p-5" />
      </div>
    </div>
  );
};

export default SQLBar;
