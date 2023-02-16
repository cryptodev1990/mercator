import { useState } from "react";
import clsx from "clsx";
import { BiCaretDown } from "react-icons/bi";

import { useTheme } from "../../lib/hooks/census/use-theme";

const HideCaret = ({
  setIsFolded,
  isFolded,
}: {
  setIsFolded: (val: boolean) => void;
  isFolded: boolean;
}) => {
  return (
    <div>
      <button
        className={clsx(
          "pointer-events-auto w-5 h-5 flex flex-row justify-center items-center m-1",
          isFolded ? "transition rotate-180" : "transition rotate-0"
        )}
        onClick={() => setIsFolded(!isFolded)}
      >
        {isFolded ? <BiCaretDown /> : <BiCaretDown />}
      </button>
    </div>
  );
};

export const Hideable = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className: string;
}) => {
  const [isHidden, setIsHidden] = useState(false);

  return (
    <div className={className}>
      <HideCaret isFolded={isHidden} setIsFolded={setIsHidden} />
      <div className={clsx(isHidden && "invisible")}>{children}</div>
    </div>
  );
};

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
          <button className="" onClick={() => setIsFolded(!isFolded)}></button>
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
