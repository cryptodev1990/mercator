import {
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import simplur from "simplur";
import { AgGridReact } from "ag-grid-react";
import { format } from "date-fns";
import fileDownload from "js-file-download";
import clsx from "clsx";

import DownloadDropdown from "./download-dropdown";

const DataTable = ({
  rows,
  columns,
  className,
  theme,
  titleBarChildren,
}: {
  rows: object[];
  columns: object[];
  className?: string;
  theme?: { theme: string; bgColor: string; secondaryBgColor: string };
  titleBarChildren?: ReactNode;
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

  const handleJSONExport = useCallback(() => {
    const date = new Date();

    fileDownload(
      new Blob([JSON.stringify(rowData, null, 2)], {
        type: "application/json",
      }),
      `${format(date, "yyyy-MM-dd")}_${format(date, "hh.mm.ss")} export.json`
    );
  }, [rowData]);

  return (
    <div className={clsx("mt-6 animate-fadeIn100", className)}>
      <div className="flex justify-between">
        <p className="text-lg">
          Results: {simplur`${rows.length} row[|s] returned`}
        </p>
        <div className="flex">
          <DownloadDropdown
            handleCSVExport={handleCSVExport}
            handleJSONExport={handleJSONExport}
            theme={theme}
          />
          {titleBarChildren}
        </div>
      </div>
      <div
        className={clsx("mt-2 ag-theme-alpine", theme?.theme)}
        style={{ height: 300 }}
      >
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

export default DataTable;
