import { PropsWithChildren } from "react";
import clsx from "clsx";

type ContainerProps = {
  className?: string;
  [key: string]: any;
};

export const Container = ({
  className,
  ...props
}: PropsWithChildren<ContainerProps>): JSX.Element => {
  return (
    <div
      className={clsx("mx-auto max-w-7xl px-4 sm:px-6 lg:px-8", className)}
      {...props}
    />
  );
};
