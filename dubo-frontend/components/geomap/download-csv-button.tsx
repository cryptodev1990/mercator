export const DownloadCSVButton = () => {
  return (
    <div className="bg-slate-500 rounded-md shadow-md text-white">
      <div className="flex flex-row justify-center items-center space-x-2 p-2">
        <div className="rounded-full h-5 w-5 bg-gray-900"></div>
        <div>
          <button
            onClick={() => {
              let csvContent = "data:text/csv;charset=utf-8,";
              const encodedUri = encodeURI(csvContent + "TODO");
              const link = document.createElement("a");
              link.setAttribute("href", encodedUri);
              link.setAttribute("download", "data.csv");
              link.click();
            }}
          >
            Download as CSV
          </button>
        </div>
      </div>
    </div>
  );
};
