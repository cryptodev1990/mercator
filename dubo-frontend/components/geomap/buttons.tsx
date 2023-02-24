import clsx from "clsx";
import { Dispatch, SetStateAction } from "react";

const Button = ({
  onClick,
  children,
  className,
}: {
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <button
      className={clsx(
        "flex flex-row justify-center items-center flex-1 h-10 py-2 px-3 whitespace-nowrap text-sm leading-none",
        "p-1 pointer-events-auto cursor-pointer",
        "transition duration-300 ease-in-out bg-spBlue text-slate-100",
        className
      )}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

const Buttons = ({
  setShowSQLQuery,
  setShowDataTable,
}: {
  setShowSQLQuery: Dispatch<SetStateAction<boolean>>;
  setShowDataTable: Dispatch<SetStateAction<boolean>>;
}) => {
  const buttons = [
    {
      title: "See SQL",
      onClick: () => setShowSQLQuery(true),
    },
    {
      title: "Data catalog",
      onClick: () => window.open("/demos/census/data-catalog", "_blank"),
    },
    {
      title: "View table",
      onClick: () => setShowDataTable(true),
    },
  ];

  return (
    <div className={clsx("flex flex-row gap-1 mt-2")}>
      {buttons.map((button) => (
        <Button key={button.title} onClick={button.onClick}>
          {button.title}
        </Button>
      ))}
    </div>
  );
};

export default Buttons;
