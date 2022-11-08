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
  console.log("properties", properties);
  const { fields, append, remove } = useFieldArray({
    name: "properties",
    control,
  });
  const onSubmit = (data: FormValues) => {
    // convert array of properties to property object
    const formProperties = data["properties"].reduce(
      (obj, item) => Object.assign(obj, { [item.key]: item.value }),
      {}
    );
    console.log("formProperties", formProperties);
    handleResults(formProperties);
  };

  return (
    <div>
      <form onSubmit={handleSubmit(onSubmit)}>
        {fields.map((field, index) => {
          if (field.key.startsWith("__")) {
            return null;
          }
          console.log("field", field);
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
                  className={`col-span-5 text-black ${
                    errors?.properties?.[index]?.value ? "error" : ""
                  }`}
                />
                {field.key === "name" ? null : (
                  <button
                    type="button"
                    className="col-span-2"
                    onClick={() => remove(index)}
                  >
                    <TbTrash />
                  </button>
                )}
              </section>
            </div>
          );
        })}

        <button
          type="button"
          onClick={() =>
            append({
              key: `New Key ${fields.length}`,
              value: `New Value ${fields.length}`,
            })
          }
        >
          APPEND
        </button>
        <input
          type="submit"
          className="text-white cursor-pointer bg-black p-2"
        />
      </form>
    </div>
  );
}
