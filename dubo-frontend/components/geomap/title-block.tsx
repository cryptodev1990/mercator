import clsx from "clsx";
import { DuboLink } from "../dubo-link";
import { useEffect, useState } from "react";

export const TitleBlock = ({ hideTitleBlock }: { hideTitleBlock: boolean }) => {
  const [hide, setHide] = useState(false);
  useEffect(() => {
    if (hideTitleBlock) {
      setTimeout(() => {
        setHide(true);
      }, 500);
    } else {
      setHide(false);
    }
  }, [hideTitleBlock]);
  if (hide) return null;
  return (
    <div
      className={clsx(
        "pl-2 py-2 w-full flex flex-1 justify-start items-center gap-1",
        hideTitleBlock && "animate-slideOut500", // slide out
        !hideTitleBlock && "animate-fadeIn500" // slide in
      )}
    >
      <h1 className={"text-2xl font-black"}>Census Explorer</h1>
      <sub className="text-sm">
        Powered by <DuboLink />
      </sub>
    </div>
  );
};
