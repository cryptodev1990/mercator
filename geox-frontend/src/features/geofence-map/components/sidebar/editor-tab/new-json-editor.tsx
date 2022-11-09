import { useForm, useFieldArray } from "react-hook-form";
import { TbTrash } from "react-icons/tb";

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
  properties: Array<{ key: string; value: any }>;
  handleResults: (properties: IDictionary<string>) => void;
}

export default function NewJsonEditor({
  properties,
  handleResults,
}: IJsonEditorProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
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
                className={`col-span-3 text-black ${
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
                className={`col-span-6 text-black ${
                  errors?.properties?.[index]?.value ? "error" : ""
                }`}
              />
              {field.key === "name" ? null : (
                <button
                  className="btn btn-error btn-xs p-0 col-span-1"
                  onClick={() => remove(index)}
                >
                  <TbTrash color="white" size={16} />
                </button>
              )}
            </section>
          </div>
        );
      })}
      <div className="flex justify-end">
        {" "}
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={() =>
            append({
              key: `New Key ${fields.length}`,
              value: `New Value ${fields.length}`,
            })
          }
        >
          APPEND
        </button>
        <input type="submit" className="btn btn-success btn-sm" />
      </div>
    </form>
  );
}
