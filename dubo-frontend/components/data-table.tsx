import { useMemo, useState } from "react";
import simplur from "simplur";
import { AgGridReact } from "ag-grid-react";
import { QueryExecResult } from "sql.js";

export const DataTable = ({
  rows,
  columns,
}: {
  rows: object[];
  columns: object[];
}) => {
  const [rowData, setRowData] = useState<object[]>(rows);
  const [columnDefs, setColumnDefs] = useState<object[]>(columns);

  const defaultColDef = useMemo(
    () => ({ sortable: true, filter: true, resizable: true }),
    []
  );

  return (
    <div className="mt-6 animate-fadeIn100">
      <p>Results: {simplur`${rows.length} row[|s] returned`}</p>
      <div className="mt-2 ag-theme-alpine" style={{ height: 300 }}>
        <AgGridReact
          defaultColDef={defaultColDef}
          rowData={rowData}
          columnDefs={columnDefs}
        />
      </div>
    </div>
  );
};

const DataTableContainer = ({ results }: { results: QueryExecResult[] }) => {
  const res = results[0];
  const { values, columns } = res;

  const rowData = values.map((row) =>
    columns.reduce((acc, c, index) => ({ ...acc, [c]: row[index] }), {})
  );
  const columnDefs = columns.map((c) => ({ field: c }));

  return <DataTable rows={rowData} columns={columnDefs} />;
};

export default DataTableContainer;
