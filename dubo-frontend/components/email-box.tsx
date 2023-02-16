import { useEffect, useRef, useState } from "react";
import { MdEmail } from "react-icons/md";
import { FaSpinner } from "react-icons/fa";

import supabase from "../lib/supabase-client";

const EmailBox = ({ autoFocus }: { autoFocus?: boolean }): JSX.Element => {
  const [status, setStatus] = useState("clean");
  const [msg, setMsg] = useState("");

  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (ref.current && autoFocus) {
      ref.current.focus();
    }
  }, [ref]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    const target = event.target as HTMLFormElement;
    const email = (target[0] as HTMLInputElement).value;
    try {
      let ret = await supabase.from("waitlist").insert([{ email }]);
      const error = ret.error;
      if (error) {
        console.log(error);
        setStatus("error");
        // Error message: duplicate key value violates unique constraint \"waitlist_email_key\"
        if (error.code === "23505") {
          setMsg(
            "Your email is already the system! We'll contact you shortly."
          );
          setStatus("resolved");
        } else {
          throw error;
        }
      } else {
        setStatus("resolved");
        setMsg("Thanks for your interest! We'll contact you shortly.");
      }
    } catch (error) {
      setStatus("error");
      setMsg(
        "Something went wrong. Please try again later. If this error persists, message us directly at support@mercator.tech"
      );
    }
  };

  if (msg) {
    return <p className="font-bold text-spBlue">{msg}</p>;
  }

  return (
    <form className="pb-10 w-full" onSubmit={handleSubmit}>
      <div className="transition-opacity ease-in duration-700 opacity-100">
        <div className="flex flex-row text-slate-600 justify-between items-center border-b border-spBlue">
          <input
            className="focus:outline-none flex-1 pl-5 bg-transparent text-spBlue placeholder:text-spBlue"
            type="email"
            ref={ref}
            placeholder="Join our mailing list"
            required={true}
          />
          <button
            className="group transition bg-white h-10 p-3 text-spBlue cursor-pointer hover:bg-spBlue font-bold overflow-x-clip whitespace-nowrap text-ellipsis"
            disabled={status === "loading"}
          >
            {status === "loading" ? (
              <FaSpinner className="animate-spin" />
            ) : (
              <MdEmail className="transition fill-spBlue group-hover:fill-white" />
            )}
          </button>
        </div>
      </div>
    </form>
  );
};

export default EmailBox;
