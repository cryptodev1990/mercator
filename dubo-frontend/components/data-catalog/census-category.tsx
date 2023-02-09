import clsx from "clsx";

const CensusCategory = ({
  category,
  color,
  onClick,
}: {
  category: string;
  color: string;
  onClick: () => void;
}) => {
  // A square containing the name of the category
  // On click, we place the category name in the search bar
  // and then we filter the results
  return (
    <button
      onClick={onClick}
      className={clsx(
        "h-32 w-32 text-slate-100 cursor-pointer mb-1 mr-1 rounded-xl",
        "flex flex-col justify-start items-center overflow-hidden",
        "hover:bg-sky-500",
        color
      )}
    >
      <div
        className={clsx(
          "text-left px-11/24",
          "text-md font-sans2 leading-none my-auto"
        )}
      >
        {category}
      </div>
    </button>
  );
};

export default CensusCategory;
