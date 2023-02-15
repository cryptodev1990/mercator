import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import simplur from "simplur";
import { AgGridReact } from "ag-grid-react";
import { QueryExecResult } from "sql.js";
import Visualizer from "./visualizer";
import { format } from "date-fns";
import fileDownload from "js-file-download";
import DownloadDropdown from "./download-dropdown";

export const DataTable = ({
  rows,
  columns,
}: {
  rows: object[];
  columns: object[];
}) => {
  const gridRef = useRef<AgGridReact | null>(null);
  const [rowData, setRowData] = useState<object[] | null>(null);
  const [columnDefs, setColumnDefs] = useState<object[] | null>(null);

  useEffect(() => {
    setRowData(rows);
    setColumnDefs(columns);
  }, [rows, columns]);

  const defaultColDef = useMemo(
    () => ({ sortable: true, filter: true, resizable: true }),
    []
  );

  const handleCSVExport = useCallback(() => {
    const date = new Date();

    gridRef?.current?.api.exportDataAsCsv({
      fileName: `${format(date, "yyyy-MM-dd")}_${format(
        date,
        "hh.mm.ss"
      )} export.csv`,
    });
  }, []);

  const handleJSONExport = () => {
    const date = new Date();

    fileDownload(
      new Blob([JSON.stringify(rowData, null, 2)], {
        type: "application/json",
      }),
      `${format(date, "yyyy-MM-dd")}_${format(date, "hh.mm.ss")} export.json`
    );
  };

  return (
    <div className="mt-6 animate-fadeIn100">
      <div className="flex justify-between">
        <p className="text-lg">
          Results: {simplur`${rows.length} row[|s] returned`}
        </p>
        <DownloadDropdown
          handleCSVExport={handleCSVExport}
          handleJSONExport={handleJSONExport}
        />
      </div>
      <div className="mt-2 ag-theme-alpine" style={{ height: 300 }}>
        <AgGridReact
          ref={gridRef}
          defaultColDef={defaultColDef}
          rowData={rowData}
          columnDefs={columnDefs}
        />
      </div>
    </div>
  );
};

const DataTableContainer = ({
  results,
  showVis,
}: {
  results: QueryExecResult[];
  showVis: boolean;
}) => {
  const res = results[0];
  const { values, columns } = res;

  const rowData = values.map((row) =>
    columns.reduce((acc, c, index) => ({ ...acc, [c]: row[index] }), {})
  );
  const columnDefs = columns.map((c) => ({ field: c }));

  return (
    <>
      <DataTable rows={rowData} columns={columnDefs} />
      {showVis && (
        <Visualizer
          header={results[0]?.columns ?? []}
          data={results[0]?.values ?? []}
        />
      )}
    </>
  );
};

export default DataTableContainer;
