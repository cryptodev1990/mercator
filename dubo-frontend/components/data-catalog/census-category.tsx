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
        "h-20 text-slate-100 cursor-pointer rounded-xl",
        "flex-[0_48%] flex flex-col justify-center items-center overflow-hidden",
        "hover:bg-sky-500",
        color
      )}
    >
      <div className={clsx("text-md font-sans2 whitespace-normal")}>
        {category}
      </div>
    </button>
  );
};

export default CensusCategory;
