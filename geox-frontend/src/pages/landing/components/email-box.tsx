import { useEffect, useRef, useState } from "react";
import { toast } from "react-hot-toast";
import { MdEmail } from "react-icons/md";
import Loading from "react-loading";
import { supabase } from "../../../common/supabase-client";

export const EmailBox = ({
  autoFocus,
  ...props
}: {
  autoFocus?: boolean;
}): JSX.Element => {
  const [status, setStatus] = useState("clean");

  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current && autoFocus) {
      ref.current.focus();
    }
  }, [ref, autoFocus]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    const target = event.target as HTMLFormElement;
    const email = (target[0] as HTMLInputElement).value;
    try {
      let ret = await supabase
        .from("waitlist")
        .insert([{ email }], { returning: "minimal" });
      const error = ret.error;
      if (error) {
        console.log(error);
        setStatus("error");
        // Error message: duplicate key value violates unique constraint \"waitlist_email_key\"
        if (error.code === "23505") {
          toast.success(
            "Your email is already the system. We appreciate your interest. We'll contact you shortly."
          );
          setStatus("resolved");
        } else {
          throw error;
        }
      } else {
        setStatus("resolved");
      }
    } catch (error) {
      setStatus("error");
      toast.error("Something went wrong. Please try again.");
    }
  };

  if (status === "resolved") {
    return (
      <p className="font-bold text-white">
        We appreciate your interest. We'll contact you shortly.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="transition-opacity ease-in duration-700 opacity-100">
        <div className="flex flex-row text-slate-600 justify-between items-center border-b border-white">
          <input
            className="focus:outline-none flex-1 pl-5 bg-transparent text-white placeholder:text-purple-200"
            type="email"
            ref={ref}
            placeholder="Join our waitlist"
            required={true}
          />
          <button
            className="transition bg-white h-10 p-3 text-white cursor-pointer hover:bg-purple-300 font-bold overflow-x-clip whitespace-nowrap text-ellipsis"
            disabled={status === "loading"}
          >
            {status === "loading" ? (
              <Loading type="spin" color="#000" height={20} width={20} />
            ) : (
              <MdEmail className="fill-purple-500" />
            )}
          </button>
        </div>
      </div>
    </form>
  );
};
