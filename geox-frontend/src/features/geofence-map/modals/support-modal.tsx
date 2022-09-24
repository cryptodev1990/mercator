import { useUiModals } from "../hooks/use-ui-modals";
import { UIModalEnum } from "../types";
import { ModalCard } from "./modal-card";

import { useForm, Resolver } from "react-hook-form";
import { supabase } from "../../../common/supabase-client";
import { toast } from "react-hot-toast";
import { useAuth0 } from "@auth0/auth0-react";
import { useState } from "react";
import { BiBug } from "react-icons/bi";
import Loading from "react-loading";

interface SupportTicket {
  email: string;
  description: string;
}

async function publishSupport(ticket: SupportTicket) {
  const ret = await supabase.from("support_tickets").insert([ticket], {
    returning: "minimal",
  });
  if (ret.status === 201) {
    toast.success("Your ticket has been submitted. We'll be in touch shortly.");
  }
  if (ret.error) {
    toast.error(
      "Error publishing support ticket. Contact support@mercator.tech."
    );
  }
}

const validateInput = (values: SupportTicket) => {
  const errors: any = {};
  if (!values.description) {
    errors.description = {
      type: "required",
      message: "Please provide a ticket description.",
    };
  }
  return errors;
};

const resolver: Resolver<SupportTicket> = async (values) => {
  return {
    values: values.description && values.email ? values : {},
    errors: validateInput(values),
  };
};

const SupportForm = () => {
  const { closeModal } = useUiModals();
  const { user } = useAuth0();
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, reset } = useForm<SupportTicket>({
    resolver,
    defaultValues: {
      email: user?.email,
    },
  });

  const attrs = [
    {
      name: "Email",
      placeholder: "The best email for follow-up",
      key: "email",
      inputType: "email",
    },
    {
      name: "Description",
      placeholder: "Describe the issue or feature to us",
      key: "description",
      inputType: "textarea",
    },
  ];
  const elements = attrs.map(({ key, name, inputType, placeholder }, i) => {
    return (
      <>
        <div key={i} className="w-full flex flex-col">
          <label
            className="label label-text text-black font-semibold text-xs"
            htmlFor={key}
          >
            {name}
          </label>
          {inputType === "textarea" && (
            <textarea
              {...register(key as any)}
              className="p-1 textarea textarea-primary bg-white border-gray-300 text-black"
              placeholder={placeholder}
            />
          )}
          {inputType !== "textarea" && (
            <input
              type={inputType}
              {...register(key as any, { required: true })}
              className="p-1 input input-primary bg-white border-gray-300 text-black"
              placeholder={placeholder}
            />
          )}
        </div>
      </>
    );
  });

  return (
    <div>
      <form
        className="flex flex-col"
        onSubmit={(e) => {
          setLoading(true);
          e?.preventDefault();
          handleSubmit((data) => {
            if (!data.email && user?.email) {
              data.email = user.email;
            }
            publishSupport(data)
              .then(() => {
                reset();
                closeModal();
              })
              .finally(() => {
                setLoading(false);
              });
          })();
        }}
      >
        {elements}
        <input
          type="submit"
          value={loading ? "Submitting..." : "Submit"}
          className="btn btn-primary mt-2 w-[50%] self-end"
          onClick={(e) => {}}
        />
      </form>
    </div>
  );
};

export const SupportModal = () => {
  const { modal, closeModal } = useUiModals();

  return (
    <ModalCard
      open={modal === UIModalEnum.SupportModal}
      onClose={closeModal}
      icon={<BiBug className="h-6 w-6 text-green-600" aria-hidden="true" />}
      title="Report a bug or request a feature"
    >
      <div>
        <p>
          You can also email{" "}
          <a href="mailto:support@mercator.tech" className="link link-primary">
            support@mercator.tech
          </a>{" "}
        </p>
        <SupportForm />
      </div>
    </ModalCard>
  );
};
