import clsx from "clsx";
import { useTheme } from "../../lib/hooks/census/use-theme";
import { useState } from "react";
import { CloseButton } from "../close-button";
import { ShowInPlaceOptionsType } from "./sql-button-bank";
export const SQLBar = ({
  generatedSql,
  setShowInPlace,
}: {
  generatedSql: string;
  setShowInPlace: (arg: ShowInPlaceOptionsType) => void;
}) => {
  const { theme } = useTheme();

  return (
    <div className="mt-3 relative pt-3">
      <div className="absolute top-0 right-0 p-5">
        <CloseButton onClick={() => setShowInPlace(null)} />
      </div>

      <div
        className={clsx(
          "flex flex-col rounded-lg p-5 pointer-events-auto cursor-pointer",
          theme.bgColor,
          theme.borderColor,
          theme.fontColor
        )}
      >
        <div
          onClick={(e) => e.stopPropagation()}
          className={clsx("font-mono cursor-auto")}
        >
          {generatedSql}
        </div>
      </div>
    </div>
  );
};
