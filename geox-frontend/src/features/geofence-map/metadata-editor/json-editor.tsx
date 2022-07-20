import GenericButton from "../../../common/components/button";

import { useForm } from "react-hook-form";
import { useState } from "react";

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

  const addKv = () => {
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
    <form onSubmit={handleSubmit(onFormSubmit)}>
      {indexes.map((index) => {
        const fieldName = `properties[${index}]`;
        return (
          <fieldset name={fieldName} key={fieldName}>
            <label>
              Key {index}:
              <input
                {...register(`properties[${index}].key`)}
                type="text"
                className="text-black"
                defaultValue={`New Key ` + index}
                name={`${fieldName}.key`}
              />
            </label>
            <label>
              Value {index}:
              <input
                {...register(`properties[${index}].value`)}
                type="text"
                className="text-black"
                defaultValue={`New Value ` + index}
                name={`${fieldName}.value`}
              />
            </label>
            <button
              className="bg-ublue hover:bg-red-700 text-white font-sans py-1 px-1 rounded text-sm"
              type="button"
              onClick={remove(index)}
            >
              Remove
            </button>
          </fieldset>
        );
      })}

      <GenericButton onClick={addKv} text="Add key-value pair" />
      <GenericButton onClick={clear} text="Clear" />
      <GenericButton
        onSubmit={(d: any) => {
          onFormSubmit(d);
        }}
        type="submit"
        text="Submit"
        extraClasses="bg-ublue"
      />
    </form>
  );
}
