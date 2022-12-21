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
import { AiOutlinePlus } from "react-icons/ai";

declare module "@tanstack/react-table" {
  interface TableMeta<TData extends RowData> {
    updateData: (rowIndex: number, columnId: string, value: unknown) => void;
    updateHeader: (rowIndex: number, columnId: string, value: string) => void;
    deleteColumn: (columnId: string) => void;
  }
}

// Give our default column cell renderer editing superpowers!
const defaultColumn: Partial<ColumnDef<Properties>> = {
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
      <div className="flex bg-gray-50 border border-gray-300 dark:bg-slate-800 p-1 w-full">
        <input
          value={value as string}
          onChange={(e) => setValue(e.target.value)}
          onBlur={onBlur}
          className={`text-ellipsis text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block dark:bg-slate-800  dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 `}
        />

        <MdDelete
          className="cursor-pointer fill-white"
          onClick={() => prop.table.options.meta?.deleteColumn(prop.column.id)}
        />
      </div>
    );
  },
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
        className={`text-ellipsis bg-gray-50 border border-gray-300 text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-full p-1 dark:bg-slate-800 dark:border-gray-600 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
      />
    );
  },
};

const BulkEditModal = () => {
  const { modal, closeModal } = useUiModals();
  const { multiSelectedShapes, clearSelectedShapeUuids } = useSelectedShapes();

  const [data, setData] = React.useState(() =>
    multiSelectedShapes.map((shape) => shape.properties)
  );

  const [tableColumns, setTableColumns] = useState<string[]>([]);

  const { setShapeLoading, tileUpdateCount, setTileUpdateCount } = useShapes();

  useEffect(() => {
    const cols = [
      ...new Set(
        multiSelectedShapes
          .map((shape: any) => Object.keys(shape.properties))
          .flat()
          .filter((column) => !["__uuid", "__namespace_id"].includes(column))
      ),
    ];
    setTableColumns(cols);
  }, []);

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
              <Dialog.Panel
                className="relative transform overflow-hidden bg-slate-700 text-left shadow-2xl transition-all"
                style={{ width: 700 }}
              >
                <h1 className="text-3xl font-bold text-white bg-slate-800 text-center p-2">
                  Bulk Edit Updte
                </h1>
                <div>
                  <div className="overflow-x-auto p-2">
                    <table className="w-full p-2 m-1">
                      <thead>
                        {table.getHeaderGroups().map((headerGroup) => (
                          <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                              <th key={header.id}>
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
                                <td key={cell.id}>
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
                  <div className="flex justify-end p-2">
                    <button
                      type="button"
                      className="btn btn-primary btn-xs"
                      onClick={() => {
                        const headerName = tableColumns.length + 1;
                        setTableColumns((old) => {
                          return [`Column ${headerName}`, ...old];
                        });
                        setData((old) => {
                          return old.map((row) => {
                            return {
                              [`Column ${headerName}`]: "",
                              ...row,
                            };
                          });
                        });
                      }}
                    >
                      <AiOutlinePlus />
                    </button>
                    <button
                      type="button"
                      className="btn btn-success btn-xs capitalize"
                      onClick={async () => {
                        closeModal();
                        setShapeLoading(true);
                        for (let shapeProperties of data) {
                          const response =
                            await GeofencerService.patchShapesShapeIdGeofencerShapesShapeIdPatchAny(
                              shapeProperties && shapeProperties.__uuid,
                              {
                                properties: shapeProperties,
                                namespace_id:
                                  shapeProperties &&
                                  shapeProperties.__namespace_id,
                              }
                            );
                        }
                        clearSelectedShapeUuids();
                        setTileUpdateCount(tileUpdateCount + 1);
                        setShapeLoading(false);
                      }}
                    >
                      Save
                    </button>
                    <button
                      type="button"
                      className="btn btn-base-300 btn-xs capitalize"
                      onClick={() => closeModal()}
                    >
                      Cancel
                    </button>
                  </div>
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
