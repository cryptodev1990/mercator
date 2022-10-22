import { useState } from "react";
import { supabase } from "../../common/supabase-client";

export const EmailBox = (): JSX.Element => {
  const [status, setStatus] = useState("clean");

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
          alert(
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
      alert("Something went wrong. Please try again.");
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
      <div>
        <div className="flex flex-row bg-white text-slate-600 text-sm sm:text-xl gap-3 justify-between items-baseline rounded-2xl w-full">
          <input
            className="focus:outline-none p-3 rounded-l-3xl"
            type="email"
            placeholder="Your email here"
            required={true}
          />
          <button
            className="transition bg-purple-500 text-white cursor-pointer 2 p-3 pr-3 hover:bg-tertiary rounded-r-2xl font-bold overflow-x-clip whitespace-nowrap text-ellipsis"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Submitting..." : "Get early access"}
          </button>
        </div>
      </div>
    </form>
  );
};
