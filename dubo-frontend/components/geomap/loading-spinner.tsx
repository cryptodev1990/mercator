import clsx from "clsx";
import { useEffect, useState } from "react";

import { TrackedText } from "../tracked-text";

export const LoadingSpinner = ({ isLoading }: { isLoading: boolean }) => {
  const [numEllipses, setNumEllipses] = useState(1);

  // animate the ellipses
  useEffect(() => {
    const interval = setInterval(() => {
      setNumEllipses((n: number) => (n + 1) % 4);
    }, 500);
    return () => clearInterval(interval);
  }, [numEllipses]);
  if (!isLoading) return null;

  return (
    <div
      className={clsx(
        "absolute top-0 left-0 z-50 w-full h-full",
        "flex flex-col justify-center items-center"
      )}
    >
      <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
      <div className="text-2xl font-bold px-2 py-1 rounded mt-2 w-32 text-left">
        <TrackedText text={"Loading" + ".".repeat(numEllipses)} />
      </div>
    </div>
  );
};
