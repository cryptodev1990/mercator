import { CloseButton } from "../close-button";
import SQL from "../sql";

import { ShowInPlaceOptionsType } from "./sql-button-bank";

const SQLBar = ({
  generatedSql,
  setShowInPlace,
  theme,
}: {
  generatedSql: string;
  setShowInPlace: (arg: ShowInPlaceOptionsType) => void;
  theme: string;
}) => {
  return (
    <div className="mt-6 relative">
      <div className="absolute top-2 right-2">
        <CloseButton onClick={() => setShowInPlace(null)} />
      </div>

      <div
        onClick={(e) => e.stopPropagation()}
        className="font-mono cursor-auto"
        key={theme}
      >
        <SQL
          query={generatedSql}
          light={theme === "light"}
          className="!p-5 rounded max-w-3xl mx-auto"
        />
      </div>
    </div>
  );
};

export default SQLBar;
