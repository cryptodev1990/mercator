import { useForm } from "react-hook-form";
import { useState } from "react";
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
                          className="text-black w-[100px]"
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
                          {...register(`properties[${index}].value`)}
                          type="text"
                          className="text-black w-[150px]"
                          defaultValue={
                            properties?.[index]?.value ?? `New Value ` + index
                          }
                          name={`${fieldName}.value`}
                        />
                      </span>
                    </td>
                    <button
                      className="bg-ublue hover:bg-red-700 text-white font-sans py-1 px-1 rounded text-sm"
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
