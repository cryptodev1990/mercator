import { useSelectedShapes } from "features/geofence-map/hooks/use-selected-shapes";
import { useUiModals } from "features/geofence-map/hooks/use-ui-modals";
import { UIModalEnum } from "features/geofence-map/types";
import { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";
import React, { useState, useEffect } from "react";
import {
  ColumnDef,
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  RowData,
  useReactTable,
} from "@tanstack/react-table";
import { Properties } from "@turf/helpers";
import _ from "lodash";
import { MdDelete } from "react-icons/md";
import { GeofencerService } from "client";
import { useShapes } from "features/geofence-map/hooks/use-shapes";

declare module "@tanstack/react-table" {
  interface TableMeta<TData extends RowData> {
    updateData: (rowIndex: number, columnId: string, value: unknown) => void;
    updateHeader: (rowIndex: number, columnId: string, value: string) => void;
    deleteColumn: (columnId: string) => void;
  }
}

// Give our default column cell renderer editing superpowers!
const defaultColumn: Partial<ColumnDef<Properties>> = {
  cell: ({ getValue, row: { index }, column: { id }, table }) => {
    const initialValue = getValue();
    /* eslint-disable */
    const [value, setValue] = useState(initialValue);
    const onBlur = () => {
      table.options.meta?.updateData(index, id, value);
    };

    /* eslint-disable */
    useEffect(() => {
      setValue(initialValue);
    }, [initialValue]);

    return (
      <input
        value={value as string}
        onChange={(e) => setValue(e.target.value)}
        onBlur={onBlur}
      />
    );
  },

  header: (prop) => {
    const initialValue = prop.column.id;
    /* eslint-disable */
    const [value, setValue] = useState(initialValue);
    const onBlur = () => {
      prop.table.options.meta?.updateHeader(
        prop.header.index,
        prop.column.id,
        value
      );
    };

    /* eslint-disable */
    useEffect(() => {
      setValue(initialValue);
    }, [initialValue]);

    return (
      <div className="flex">
        <input
          value={value as string}
          onChange={(e) => setValue(e.target.value)}
          onBlur={onBlur}
        />

        <MdDelete
          className="cursor-pointer"
          onClick={() => prop.table.options.meta?.deleteColumn(prop.column.id)}
        />
      </div>
    );
  },
};

const BulkEditModal = () => {
  const { modal, closeModal } = useUiModals();
  const { multiSelectedShapes } = useSelectedShapes();

  const [data, setData] = React.useState(() =>
    multiSelectedShapes.map((shape) => shape.properties)
  );

  const { setRefreshTiles } = useShapes();

  const [tableColumns, setTableColumns] = useState([
    "NAMELSAD",
    "LSAD",
    "MEMI",
    "ALAND",
    "GEOID",
    "MTFCC",
    "AWATER",
    "CBSAFP",
    "INTPTLAT",
  ]);

  const columnHelper = createColumnHelper<Properties>();

  const columns = tableColumns.map((column) =>
    columnHelper.accessor(column, {})
  );

  const table = useReactTable({
    data: data,
    columns,
    defaultColumn,
    getCoreRowModel: getCoreRowModel(),
    meta: {
      updateData: (rowIndex, columnId, value) => {
        const newData = data.map((row, index) => {
          if (index === rowIndex) {
            return {
              ...data[rowIndex]!,
              [columnId]: value,
            };
          }
          return row;
        });
        setData(newData);
      },
      updateHeader: (index: number, columnId: string, value: string) => {
        const newData = data.map((row: any) => {
          const temp = row[columnId];
          const newObj = _.omit(row, columnId);
          return {
            ...newObj,
            [value]: temp,
          };
        });
        const newTableColumns = [...tableColumns];
        newTableColumns[index] = value;

        setTableColumns(newTableColumns);

        setData(newData);
      },
      deleteColumn: (columnId: string) => {
        const newData = data.map((row) => {
          const newObj = _.omit(row, columnId);
          return newObj;
        });
        setTableColumns(tableColumns.filter((column) => column !== columnId));
        setData(newData);
      },
    },
  });

  return (
    <Transition.Root show={modal === UIModalEnum.BulkEditModal} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={closeModal}>
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all p-4">
                <div>
                  <Dialog.Title
                    as="h1"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    Bulk Edit Updte
                  </Dialog.Title>
                </div>
                <div>
                  <table className="border-collapse border border-slate-500">
                    <thead>
                      {table.getHeaderGroups().map((headerGroup) => (
                        <tr key={headerGroup.id}>
                          {headerGroup.headers.map((header) => (
                            <th
                              className="border border-slate-600 text-black"
                              key={header.id}
                            >
                              {header.isPlaceholder
                                ? null
                                : flexRender(
                                    header.column.columnDef.header,
                                    header.getContext()
                                  )}
                            </th>
                          ))}
                        </tr>
                      ))}
                    </thead>
                    <tbody>
                      {table.getRowModel().rows.map((row) => {
                        return (
                          <tr key={row.id}>
                            {row.getVisibleCells().map((cell) => (
                              <td
                                className="border border-slate-700 text-black"
                                key={cell.id}
                              >
                                {flexRender(
                                  cell.column.columnDef.cell,
                                  cell.getContext()
                                )}
                              </td>
                            ))}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                    onClick={() => closeModal()}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                    onClick={() => {
                      for (let shapeProperties of data) {
                        GeofencerService.patchShapesShapeIdGeofencerShapesShapeIdPatchAny(
                          shapeProperties && shapeProperties.__uuid,
                          {
                            properties: shapeProperties,
                            namespace_id:
                              shapeProperties && shapeProperties.__namespace_id,
                          }
                        ).then((res) => {
                          setRefreshTiles();
                        });
                      }

                      console.log("data", data);
                    }}
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                    onClick={() => {
                      // add new column to tableColumns using setTableColumns
                      const headerName = tableColumns.length + 1;
                      setTableColumns((old) => {
                        return [...old, `Column ${headerName}`];
                      });
                      setData((old) => {
                        return old.map((row) => {
                          return {
                            ...row,
                            [`Column ${headerName}`]: "",
                          };
                        });
                      });
                    }}
                  >
                    Add Column
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};

export default BulkEditModal;
