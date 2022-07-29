import { useForm } from "react-hook-form";
import { useEffect, useState } from "react";
import { TbTrash } from "react-icons/tb";

interface IDictionary<T> {
  [index: string]: T;
}

interface IJsonEditorProps {
  properties: Array<{ key: string; value: any }>;
  handleResults: (properties: IDictionary<string>) => void;
}

export function JsonEditor({ properties, handleResults }: IJsonEditorProps) {
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

  const clear = () => {
    setIndexes([]);
  };

  return (
    <div className="flex overflow-x-hidden p-3">
      <form onSubmit={handleSubmit(onFormSubmit)}>
        <table>
          <tbody>
            {indexes.map((index) => {
              const fieldName = `properties[${index}]`;
              return (
                <fieldset name={fieldName} key={fieldName}>
                  <tr className="flex">
                    <td>
                      <span>
                        <input
                          {...register(`properties[${index}].key`)}
                          type="text"
                          className="text-black px-2 w-[100px] read-only:bg-slate-400 read-only:text-white read-only:select-none read-only:cursor-default"
                          hidden={properties?.[index]?.key.startsWith("__")}
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
                          className="text-black px-2 w-[150px] disabled:text-white"
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
                      <TbTrash />
                    </button>
                  </tr>
                </fieldset>
              );
            })}

            <button className="btn btn-sm btn-primary bg-ublue" onClick={addKv}>
              Add key-value pair
            </button>
            <button
              className="btn btn-sm btn-accent bg-porsche"
              onSubmit={(d: any) => {
                onFormSubmit(d);
              }}
              type="submit"
            >
              Submit
            </button>
          </tbody>
        </table>
      </form>
    </div>
  );
}
