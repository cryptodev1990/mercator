import { useForm, useFieldArray } from "react-hook-form";
import { AiOutlinePlus } from "react-icons/ai";
import { MdDelete as DeleteIcon } from "react-icons/md";
import { useEffect } from "react";

type FormValues = {
  properties: {
    key: string;
    value: string;
  }[];
};

interface IDictionary<T> {
  [index: string]: T;
}

interface IJsonEditorProps {
  uuid: string;
  properties: Array<{ key: string; value: any }>;
  handleResults: (properties: IDictionary<string>) => void;
}

export default function JsonEditor({
  uuid,
  properties,
  handleResults,
}: IJsonEditorProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormValues>({
    defaultValues: {
      properties,
    },
    mode: "onBlur",
  });
  const { fields, append, remove } = useFieldArray({
    name: "properties",
    control,
  });
  const onSubmit = (data: FormValues) => {
    // convert array of properties e.g [{key: 'key 1', value: 'value 1'}] to property object {'key 1': 'value 1'}
    const formProperties = data["properties"].reduce(
      (obj, item) => Object.assign(obj, { [item.key]: item.value }),
      {}
    );
    handleResults(formProperties);
  };

  useEffect(() => {
    reset({ properties });
  }, [uuid]);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {fields.map((field, index) => {
        if (field.key.startsWith("__")) {
          return null;
        }
        return (
          <div key={field.id}>
            <section className={"section grid grid-cols-10"} key={field.id}>
              <input
                placeholder="key"
                {...register(`properties.${index}.key` as const, {
                  required: true,
                })}
                className={`col-span-4 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-1 dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 ${
                  errors?.properties?.[index]?.value ? "error" : ""
                }`}
                disabled={field.key === "name" ? true : false}
              />
              <input
                placeholder="value"
                type="string"
                {...register(`properties.${index}.value` as const, {
                  required: true,
                })}
                className={`col-span-5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-1 dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500${
                  errors?.properties?.[index]?.value ? "error" : ""
                }`}
              />
              {field.key === "name" ? null : (
                <button
                  className="bg-slate-700 hover:bg-red-400 grid place-items-center hover:border-red-400 disabled:bg-slate-700 rounded m-1 disabled:cursor-not-allowed"
                  title="Delete this namespace"
                  data-tip={`Delete the property`}
                  data-tip-skew="right"
                  onClick={() => remove(index)}
                >
                  <DeleteIcon className="fill-white" />
                </button>
              )}
            </section>
          </div>
        );
      })}
      <div className="flex justify-end mt-2">
        {" "}
        <button
          type="button"
          className="btn btn-primary btn-xs"
          onClick={() =>
            append({
              key: `New Key ${fields.length}`,
              value: `New Value ${fields.length}`,
            })
          }
        >
          <AiOutlinePlus />
        </button>
        <input
          type="submit"
          value="save"
          className="btn btn-success btn-xs capitalize"
        />
      </div>
    </form>
  );
}
