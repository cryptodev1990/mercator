import { useForm } from "react-hook-form";
import { useState } from "react";
import { TrashIcon } from "../../../../../common/components/icons";

interface IDictionary<T> {
  [index: string]: T;
}

interface IJsonEditorProps {
  properties: Array<{ key: string; value: any }>;
  handleResults: (properties: IDictionary<string>) => void;
  disableSubmit: boolean;
}

export function JsonEditor({
  properties,
  handleResults,
  disableSubmit,
}: IJsonEditorProps) {
  const numProps = properties?.length ?? 0;
  const range = [...Array(numProps).keys()];

  const [indexes, setIndexes] = useState<number[]>(properties ? range : [0]);
  const [counter, setCounter] = useState<number>(properties ? numProps + 1 : 1);
  const { register, handleSubmit } = useForm();

  const onFormSubmit = (data: any) => {
    const outputData: IDictionary<string> = {};
    for (const i of indexes) {
      const { key: k, value: v } = data.properties[i] as {
        key: string;
        value: string;
      };
      outputData[k] = v;
    }
    handleResults(outputData);
  };

  const addKv = (e: any) => {
    e.preventDefault();
    setIndexes((prevIndexes) => [...prevIndexes, counter]);
    setCounter((prevCounter) => prevCounter + 1);
  };

  const remove = (index: number) => () => {
    setIndexes((prevIndexes) => [
      ...prevIndexes.filter((item) => item !== index),
    ]);
    setCounter((prevCounter) => prevCounter - 1);
  };

  return (
    <div className="p-3">
      <form onSubmit={handleSubmit(onFormSubmit)}>
        <div className="overflow-scroll h-[500px] scrollbar-thin hover:scrollbar-track-none hover:scrollbar-thumb-slate-900">
          <table>
            <tbody className="">
              {indexes.map((index) => {
                const fieldName = `properties[${index}]`;
                return (
                  <tr key={fieldName} className="flex">
                    <td>
                      <span>
                        <input
                          {...register(`properties[${index}].key`)}
                          type="text"
                          spellCheck={false}
                          className={
                            "text-white bg-slate-500 font-bold focus:text-black focus:font-normal read-only:font-bold px-2 w-[100px] read-only:bg-slate-400 read-only:text-white focus:bg-white read-only:select-none read-only:cursor-default text-ellipsis" +
                            (properties?.[index]?.key.length > 7
                              ? " focus:w-[85%] focus:z-50 focus:translate-y-[-5] focus:absolute focus:shadow"
                              : "")
                          }
                          hidden={properties?.[index]?.key.startsWith("__")}
                          {...(properties?.[index]?.key === "name"
                            ? { tabIndex: -1 }
                            : {})}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              e.preventDefault();
                              e.stopPropagation();
                            }
                          }}
                          readOnly={
                            properties?.[index]?.key.startsWith("__") ||
                            properties?.[index]?.key === "name"
                          }
                          defaultValue={
                            properties?.[index]?.key ?? "New Key " + index
                          }
                          name={`${fieldName}.key`}
                        />
                      </span>
                    </td>
                    <td>
                      <span>
                        <input
                          {...register(`properties[${index}].value`, {
                            minLength: 1,
                          })}
                          type="text"
                          autoFocus={index === 0}
                          className={
                            "text-black px-2 w-[150px] disabled:text-white" +
                            (properties?.[index]?.value.length > 9
                              ? " focus:w-[85%] focus:z-50 focus:translate-y-[-5] focus:absolute focus:shadow"
                              : "")
                          }
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              e.preventDefault();
                              e.stopPropagation();
                            }
                          }}
                          defaultValue={
                            properties?.[index]?.value ?? `New Value ` + index
                          }
                          hidden={properties?.[index]?.key.startsWith("__")}
                          name={`${fieldName}.value`}
                        />
                      </span>
                    </td>
                    <td>
                      <button
                        className="bg-ublue hover:bg-red-700 text-white disabled:text-slate-600 disabled:bg-slate-600 font-sans py-1 px-1 rounded text-sm"
                        hidden={properties?.[index]?.key.startsWith("__")}
                        disabled={
                          properties?.[index]?.key.startsWith("__") ||
                          properties?.[index]?.key === "name"
                        }
                        type="button"
                        onClick={remove(index)}
                      >
                        <TrashIcon />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="my-5">
          <button
            className="btn btn-sm btn-primary bg-blue-600"
            onClick={addKv}
          >
            Add key-value pair
          </button>
          <button
            className="btn btn-sm btn-accent bg-green-600"
            disabled={disableSubmit}
            type="submit"
          >
            Submit
          </button>
        </div>
      </form>
    </div>
  );
}
