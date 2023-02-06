import clsx from "clsx";

export const LoadingSpinner = ({ isLoading }: { isLoading: boolean }) => {
  if (!isLoading) return null;

  return (
    <div
      className={clsx(
        "absolute top-0 left-0 z-50 w-full h-full",
        "flex flex-col justify-center items-center"
      )}
    >
      <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
      <div className="text-2xl font-bold">Loading data...</div>
    </div>
  );
};
