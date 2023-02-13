import clsx from "clsx";
import { useRef } from "react";

export type ShowInPlaceOptionsType = "generated_sql" | "data_catalog" | null;

const Btn = ({
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
        "flex flex-row justify-center items-center flex-1 w-[5rem] h-10 text-sm leading-none",
        "rounded-lg p-1 pointer-events-auto cursor-pointer",
        "transition duration-300 ease-in-out bg-spBlue text-slate-100",
        className
      )}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

const btns = [
  {
    title: "See SQL",
    slug: "generated_sql",
  },
  {
    title: "Data catalog",
    slug: "data_catalog",
  },
  {
    title: "Download",
    slug: "download",
  },
];

export const SQLButtonBank = ({
  showInPlace,
  setShowInPlace,
}: {
  showInPlace: string | null;
  setShowInPlace: (val: ShowInPlaceOptionsType) => void;
}) => {
  const ref = useRef<HTMLDivElement>(null);

  if (showInPlace) {
    return null;
  }

  return (
    <div ref={ref} className={clsx("flex flex-row gap-1 mt-2")}>
      {btns.map((btn) => (
        <Btn
          key={btn.title}
          onClick={() => {
            if (showInPlace === btn.slug) {
              setShowInPlace(null);
              return;
            }
            setShowInPlace(btn.slug as ShowInPlaceOptionsType);
          }}
        >
          {btn.title}
        </Btn>
      ))}
    </div>
  );
};
