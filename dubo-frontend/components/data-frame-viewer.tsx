const DataFrameViewer = ({ header, data }: { header: string[]; data: any }) => {
  // Format like a pandas dataframe
  if (data.length === 0) {
    return <div className="text-center">No results</div>;
  }
  return (
    <table className="font-mono overflow-x-scroll">
      <thead className="bg-spBlue text-white">
        <tr>
          {header.map((h, i) => (
            <th className="border border-white p-1.5 text-center" key={i}>
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.slice(0, 10).map((row: any, i: number) => (
          <tr key={i}>
            {row.map((cell: any, j: number) => (
              <td className="border px-5 text-left" key={j}>
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DataFrameViewer;
