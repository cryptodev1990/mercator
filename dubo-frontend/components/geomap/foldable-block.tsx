import { useState } from "react";
import { useTheme } from "../../lib/hooks/census/use-theme";
import clsx from "clsx";
import { BiCaretDown, BiCaretUp } from "react-icons/bi";

export const FoldableBlock = ({
  title,
  contents,
}: {
  title: string;
  contents: string;
}) => {
  const [isFolded, setIsFolded] = useState(true);
  const { theme } = useTheme();

  return (
    <div
      className={clsx(
        "flex flex-col rounded-lg p-2 pointer-events-auto cursor-pointer",
        theme.bgColor,
        theme.borderColor,
        theme.fontColor
      )}
      onClick={() => setIsFolded(!isFolded)}
    >
      <div className="flex flex-row justify-between">
        <div className="text-lg font-bold">{title}</div>
        <div>
          <button className="" onClick={() => setIsFolded(!isFolded)}>
            {isFolded ? (
              <BiCaretDown className="transition rotate-0" />
            ) : (
              <BiCaretDown className="transition rotate-180" />
            )}
          </button>
        </div>
      </div>
      <div
        onClick={(e) => e.stopPropagation()}
        className={clsx(isFolded && "hidden", "font-mono cursor-auto")}
      >
        {contents}
      </div>
    </div>
  );
};
