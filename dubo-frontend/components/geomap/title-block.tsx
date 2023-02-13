import clsx from "clsx";
import { DuboLink } from "../dubo-link";
import { useEffect, useState } from "react";

const TitleBlock = ({ zoomThreshold }: { zoomThreshold: boolean }) => {
  const [hide, setHide] = useState(false);
  useEffect(() => {
    if (zoomThreshold) {
      setTimeout(() => {
        setHide(true);
      }, 500);
    } else {
      setHide(false);
    }
  }, [zoomThreshold]);
  if (hide) return null;
  return (
    <div
      className={clsx(
        "pl-1 sm:pl-0 sm:py-2 w-full flex flex-1 justify-start items-center gap-2",
        zoomThreshold && "animate-slideOut500", // slide out
        !zoomThreshold && "animate-fadeIn500" // slide in
      )}
    >
      <h1 className={"text-2xl font-black"}>Census Explorer</h1>
      <sub className="text-sm">
        Powered by <DuboLink />
      </sub>
    </div>
  );
};

export default TitleBlock;
