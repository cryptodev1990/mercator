import { useSelectedShapes } from "features/geofence-map/hooks/use-selected-shapes";
import { useUiModals } from "features/geofence-map/hooks/use-ui-modals";
import { UIModalEnum } from "features/geofence-map/types";
import { Fragment, useRef } from "react";
import { Dialog, Transition } from "@headlessui/react";
import * as React from "react";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Properties } from "@turf/helpers";

// Create an editable cell renderer
const EditableCell = ({
  value: initialValue,
}: // row: { index },
// column: { id },
// updateMyData,
{
  value: any;
  // row: any;
  // column: any;
  // updateMyData: any;
}) => {
  // We need to keep and update the state of the cell normally
  const [value, setValue] = React.useState(initialValue);

  const onChange = (e: any) => {
    setValue(e.target.value);
  };

  // We'll only update the external data when the input is blurred
  // const onBlur = () => {
  //   updateMyData(index, id, value);
  // };

  // If the initialValue is changed external, sync it up with our state
  React.useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  return <input value={value} onChange={onChange} />;
};

const BulkEditModal = () => {
  const { modal, closeModal } = useUiModals();
  const { multiSelectedShapes } = useSelectedShapes();

  const columnHelper = createColumnHelper<Properties>();

  const columns = [
    columnHelper.accessor("NAMELSAD", {
      header: () => "Name",
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("LSAD", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("MEMI", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("ALAND", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    // columnHelper.accessor("CSAFP", {
    //   cell: (info) => info.getValue(),
    // }),
    columnHelper.accessor("GEOID", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("MTFCC", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("AWATER", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("CBSAFP", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    columnHelper.accessor("INTPTLAT", {
      cell: (info) => <EditableCell value={info.getValue()} />,
    }),
    // columnHelper.accessor("topojson_object_name", {
    //   cell: (info) => info.getValue(),
    // }),
    // columnHelper.accessor("__uuid", {
    //   cell: (info) => info.getValue(),
    // }),
    columnHelper.accessor("__namespace_id", {
      header: () => "Namespace ID",
      cell: (info) => info.getValue(),
    }),
    // columnHelper.accessor("layerName", {
    //   header: () => "Layer Name",
    //   cell: (info) => info.getValue(),
    // }),
  ];

  const table = useReactTable({
    data: multiSelectedShapes.map((shape) => shape.properties),
    columns,
    getCoreRowModel: getCoreRowModel(),
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
                      console.log("row", row);
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
                <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                  <button
                    type="button"
                    className="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                    onClick={() => closeModal()}
                  >
                    Cancel
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
