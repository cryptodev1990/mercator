import { PropsWithChildren } from "react";
import clsx from "clsx";

type GradientHeaderProps = {
  className?: string;
};

export const GradientHeader = ({
  className,
  children,
}: PropsWithChildren<GradientHeaderProps>) => {
  return (
    <h1 className={clsx("text-2xl font-bold text-purple-500", className)}>
      {children}
    </h1>
  );
};
